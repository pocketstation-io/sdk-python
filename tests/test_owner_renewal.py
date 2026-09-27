"""Finite owner renewal, shutdown ordering and sanitized failures."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from threading import Event, Thread
from time import monotonic, sleep

import httpx
import pytest
from pocketstation.aio.control import ControlClient as AsyncControlClient
from pocketstation.aio.relay import RelaySession as AsyncRelaySession
from pocketstation.control import ControlClient, ControlPlaneError, SecretToken
from pocketstation.relay import RelayError, RelaySession

CREATE = {
    "session_id": "session_renewal",
    "required_buses": ["application", "microphone"],
    "source_token": "initial-secret",
    "whip_url": "https://relay.example/v1/sessions/session_renewal/whip",
    "whep_url": "https://relay.example/v1/sessions/session_renewal/whep",
    "ice_servers": [],
}


def renewal(token: str, ttl_seconds: float = 0.15) -> dict[str, str]:
    return {
        "source_token": token,
        "expires_at": (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat(),
    }


def until(predicate: Callable[[], bool]) -> None:
    deadline = monotonic() + 3
    while not predicate():
        assert monotonic() < deadline, "bounded renewal observation timed out"
        sleep(0.002)


@pytest.mark.parametrize("bad", [False, None, "invalid", "2026-01-01T00:00:00"])
def test_renewal_response_validation_has_no_raw_credential_chain(bad: object) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/sessions/session_renewal/renew"
        assert request.headers["authorization"] == "Bearer initial-secret"
        return httpx.Response(
            200, json={"source_token": "unknown-secret", "expires_at": bad}
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        control = ControlClient("https://control.example", http_client=http)
        with pytest.raises(ControlPlaneError) as failure:
            control.renew_session("session_renewal", SecretToken("initial-secret"))
    assert "unknown-secret" not in repr(failure.value)
    assert failure.value.__cause__ is None
    assert failure.value.__context__ is None


def test_owner_default_renews_repeatedly_and_deletes_with_latest_credential() -> None:
    tokens: list[str] = []
    deleted: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            expected = tokens[-1] if tokens else "initial-secret"
            assert request.headers["authorization"] == f"Bearer {expected}"
            token = f"renewed-secret-{len(tokens)}"
            tokens.append(token)
            return httpx.Response(200, json=renewal(token))
        assert request.method == "DELETE"
        deleted.append(request.headers["authorization"])
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            control_client=ControlClient("https://control.example", http_client=http),
        )
        try:
            until(lambda: len(tokens) >= 3)
            assert remote.owner_expires_at is not None
            assert remote.renewal_error is None
            assert tokens[-1] not in repr(remote.credentials)
        finally:
            remote.close()
        assert deleted == [f"Bearer {tokens[-1]}"]
        assert remote._renewal_thread is not None
        assert not remote._renewal_thread.is_alive()


@pytest.mark.parametrize("status,attempts", [(401, 1), (503, 3)])
def test_terminal_renewal_failure_is_observable_and_close_cannot_report_success(
    status: int, attempts: int
) -> None:
    calls = 0
    deleted = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            calls += 1
            if calls == 1:
                return httpx.Response(200, json=renewal("bootstrap-secret", 1.0))
            return httpx.Response(status, text="unknown-leaked-token")
        deleted.append(request.headers["authorization"])
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            control_client=ControlClient("https://control.example", http_client=http),
        )
        until(lambda: remote.renewal_error is not None)
        assert calls == attempts + 1
        assert "unknown-leaked-token" not in repr(remote.renewal_error)
        with pytest.raises(RelayError, match="renewal failed"):
            remote.close()
        assert deleted == ["Bearer bootstrap-secret"]
        assert remote._renewal_thread is not None
        assert not remote._renewal_thread.is_alive()


def test_close_waits_for_inflight_renewal_before_delete_and_uses_its_result() -> None:
    entered, release, closed = Event(), Event(), Event()
    calls = 0
    order: list[str] = []
    errors: list[Exception] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            calls += 1
            if calls > 1:
                entered.set()
                assert release.wait(2)
                order.append("renewed")
            return httpx.Response(200, json=renewal(f"token-{calls}"))
        order.append("deleted")
        assert request.headers["authorization"] == "Bearer token-2"
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            control_client=ControlClient("https://control.example", http_client=http),
            request_timeout_seconds=0.5,
        )
        assert entered.wait(2)

        def close() -> None:
            try:
                remote.close()
            except Exception as error:
                errors.append(error)
            finally:
                closed.set()

        thread = Thread(target=close)
        thread.start()
        assert not closed.wait(0.02)
        release.set()
        thread.join(2)
        assert not thread.is_alive()
        assert not errors
        assert order == ["renewed", "deleted"]


async def test_async_owner_default_renews_and_close_cancels_before_delete() -> None:
    calls = 0
    entered, cancelled = asyncio.Event(), asyncio.Event()
    deleted: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            calls += 1
            if calls == 3:
                entered.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    cancelled.set()
            return httpx.Response(200, json=renewal(f"async-token-{calls}"))
        assert cancelled.is_set()
        deleted.append(request.headers["authorization"])
        return httpx.Response(204)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        remote = await AsyncRelaySession.create(
            control_plane_url="https://control.example",
            control_client=AsyncControlClient(
                "https://control.example", http_client=http
            ),
        )
        await asyncio.wait_for(entered.wait(), 3)
        await remote.aclose()
        assert deleted == ["Bearer async-token-2"]
        assert remote._renewal_task is not None and remote._renewal_task.done()
        assert remote.renewal_error is None


async def test_async_permanent_renewal_failure_is_reported_without_secret() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            calls += 1
            if calls == 1:
                return httpx.Response(200, json=renewal("async-secret"))
            return httpx.Response(403, text="unknown-secret")
        return httpx.Response(204)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        remote = await AsyncRelaySession.create(
            control_plane_url="https://control.example",
            control_client=AsyncControlClient(
                "https://control.example", http_client=http
            ),
        )
        async with asyncio.timeout(3):
            while remote.renewal_error is None:
                await asyncio.sleep(0.002)
        assert calls == 2
        assert "unknown-secret" not in repr(remote.renewal_error)
        with pytest.raises(RelayError, match="renewal failed"):
            await remote.aclose()
        assert remote._renewal_task is not None and remote._renewal_task.done()


async def test_async_close_before_renewal_task_starts_still_deletes_session() -> None:
    deleted = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            return httpx.Response(200, json=renewal("bootstrap-secret", 10))
        deleted.append(request.headers["authorization"])
        return httpx.Response(204)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        remote = await AsyncRelaySession.create(
            control_plane_url="https://control.example",
            control_client=AsyncControlClient(
                "https://control.example", http_client=http
            ),
        )
        await remote.aclose()
        await remote.aclose()
        assert deleted == ["Bearer bootstrap-secret"]
        assert remote._renewal_task is not None and remote._renewal_task.done()


@pytest.mark.parametrize("async_mode", [False, True])
async def test_expired_bootstrap_is_rejected_and_created_session_is_deleted(
    async_mode: bool,
) -> None:
    deleted = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            return httpx.Response(200, json=renewal("expired-token", -1))
        assert request.headers["authorization"] == "Bearer initial-secret"
        deleted.append(request.method)
        return httpx.Response(204)

    if async_mode:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            with pytest.raises(RelayError, match="renewal failed"):
                await AsyncRelaySession.create(
                    control_plane_url="https://control.example",
                    control_client=AsyncControlClient(
                        "https://control.example", http_client=http
                    ),
                )
    else:
        with httpx.Client(transport=httpx.MockTransport(handler)) as sync_http:
            with pytest.raises(RelayError, match="renewal failed"):
                RelaySession.create(
                    control_plane_url="https://control.example",
                    control_client=ControlClient(
                        "https://control.example", http_client=sync_http
                    ),
                )
    assert deleted == ["DELETE"]


async def test_async_stuck_transport_reports_timeout_before_delete() -> None:
    calls = 0
    entered, release = asyncio.Event(), asyncio.Event()
    deleted = []

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            calls += 1
            if calls > 1:
                entered.set()
                while not release.is_set():
                    try:
                        await release.wait()
                    except asyncio.CancelledError:
                        pass
            return httpx.Response(200, json=renewal(f"token-{calls}"))
        deleted.append(request.method)
        return httpx.Response(204)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        remote = await AsyncRelaySession.create(
            control_plane_url="https://control.example",
            control_client=AsyncControlClient(
                "https://control.example", http_client=http
            ),
            request_timeout_seconds=0.05,
        )
        await asyncio.wait_for(entered.wait(), 2)
        try:
            async with asyncio.timeout(2):
                with pytest.raises(RelayError) as failure:
                    await remote.aclose()
            assert failure.value.code == "relay.owner_shutdown_timeout"
            assert not deleted
        finally:
            release.set()
            assert remote._renewal_task is not None
            await asyncio.wait_for(remote._renewal_task, 2)
            with pytest.raises(RelayError):
                await remote.aclose()
        assert deleted == ["DELETE"]


def test_sync_stuck_transport_reports_timeout_before_delete() -> None:
    calls = 0
    entered, release = Event(), Event()
    deleted = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE)
        if request.url.path.endswith("/renew"):
            calls += 1
            if calls > 1:
                entered.set()
                assert release.wait(3)
            return httpx.Response(200, json=renewal(f"token-{calls}"))
        deleted.append(request.method)
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            control_client=ControlClient("https://control.example", http_client=http),
            request_timeout_seconds=0.01,
        )
        assert entered.wait(2)
        try:
            with pytest.raises(RelayError) as failure:
                remote.close()
            assert failure.value.code == "relay.owner_shutdown_timeout"
            assert not deleted
        finally:
            release.set()
            assert remote._renewal_thread is not None
            remote._renewal_thread.join(2)
            with pytest.raises(RelayError):
                remote.close()
        assert not remote._renewal_thread.is_alive()
        assert deleted == ["DELETE"]
