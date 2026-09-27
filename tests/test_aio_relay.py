"""Async relay surface symmetry over the same Rust and service contracts."""

from __future__ import annotations

import httpx
import pytest
from pocketstation._api import RelayError, Source
from pocketstation.aio._api import ControlClient, RelaySession, Session

CREATE_RESPONSE = {
    "session_id": "session_123",
    "required_buses": ["application", "microphone"],
    "source_token": "source-secret",
    "whip_url": "https://relay.example/v1/sessions/session_123/whip",
    "whep_url": "https://relay.example/v1/sessions/session_123/whep",
    "ice_servers": [],
}
JOIN_CODE = "4a54c6b9-fdc2-4e0c-a740-715efdcf03de"
INVITATION_RESPONSE = {
    "join_code": JOIN_CODE,
    "join_url": f"https://receiver.example/join#join={JOIN_CODE}",
    "share_alias": "gentleglow-cedarbloom-riverglen",
    "share_url": (
        f"https://receiver.example/gentleglow-cedarbloom-riverglen#join={JOIN_CODE}"
    ),
    "visibility": "private",
    "expires_at": "2026-09-26T18:15:00Z",
}


@pytest.mark.asyncio
async def test_async_relay_session_rejects_unbounded_request_timeout() -> None:
    with pytest.raises((TypeError, ValueError)):
        await RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            request_timeout_seconds=None,
        )


@pytest.mark.asyncio
async def test_async_relay_composes_native_routes_and_real_readiness() -> None:
    control_requests: list[httpx.Request] = []
    snapshots = iter(
        [
            _snapshot(ready=True, subscription_count=0),
            _snapshot(ready=True, subscription_count=1),
            _snapshot(ready=True, subscription_count=2),
        ]
    )

    async def control_handler(request: httpx.Request) -> httpx.Response:
        control_requests.append(request)
        if request.method == "POST" and request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            return httpx.Response(200, json=next(snapshots))
        assert request.headers["authorization"] == "Bearer source-secret"
        if request.method == "POST" and request.url.path.endswith("/invitations"):
            return httpx.Response(201, json=INVITATION_RESPONSE)
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(control_handler)
    ) as control_http:
        control = ControlClient(
            "https://control.example",
            http_client=control_http,
        )
        remote = await RelaySession.create(
            control_plane_url="https://control.example",
            control_client=control,
        )

        session = Session()
        application = session.capture(Source.application("PocketStation Fixture"))
        microphone = session.capture(Source.microphone_default())
        publisher = session.relay(remote)
        app_route = application.publish(publisher, "application")
        mic_route = microphone.publish(publisher, "microphone")

        invitation = await remote.wait_for_publisher_and_invitation(
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )
        receiver = await remote.wait_for_receiver(
            minimum_receivers=2,
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )

        assert app_route.route_id != mic_route.route_id
        assert invitation.join_code.expose_secret() == JOIN_CODE
        assert invitation.share_alias == "gentleglow-cedarbloom-riverglen"
        assert "share-secret" not in repr(invitation)
        assert invitation.expose_url().endswith(f"#join={JOIN_CODE}")
        assert receiver.snapshot.subscription_count == 2
        assert "source-secret" not in repr(remote)

        await remote.aclose()
        await remote.aclose()

    assert [(request.method, request.url.path) for request in control_requests] == [
        ("POST", "/v1/sessions"),
        ("GET", "/v1/sessions/session_123"),
        ("POST", "/v1/sessions/session_123/invitations"),
        ("GET", "/v1/sessions/session_123"),
        ("GET", "/v1/sessions/session_123"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


@pytest.mark.asyncio
async def test_async_relay_rejects_invalid_minimum_receiver_count() -> None:
    async def control_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE_RESPONSE)
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(control_handler)
    ) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        remote = await RelaySession.create(
            control_plane_url="https://control.example",
            control_client=control,
        )
        with pytest.raises((TypeError, ValueError)):
            await remote.wait_for_receiver(minimum_receivers=0)
        await remote.aclose()


@pytest.mark.asyncio
async def test_async_relay_forwards_stun_servers_to_native_publisher() -> None:
    response = {
        **CREATE_RESPONSE,
        "ice_servers": [
            {
                "urls": ["stun:stun.example:3478"],
                "username": None,
                "credential": None,
            }
        ],
    }

    async def control_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(201, json=response)
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(control_handler)
    ) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        remote = await RelaySession.create(
            control_plane_url="https://control.example",
            control_client=control,
        )
        calls: list[tuple[str, str, str, list[list[str]]]] = []

        class NativeSession:
            def relay(
                self,
                relay_url: str,
                session_id: str,
                source_token: str,
                ice_servers: list[list[str]],
            ) -> object:
                calls.append((relay_url, session_id, source_token, ice_servers))
                return object()

        class ManagedSession:
            _native = NativeSession()

        remote.publisher(ManagedSession())  # type: ignore[arg-type]
        await remote.aclose()

    assert calls == [
        (
            "https://relay.example",
            "session_123",
            "source-secret",
            [["stun:stun.example:3478"]],
        )
    ]


@pytest.mark.asyncio
async def test_async_relay_rejects_unsupported_ice_and_deletes_remote_session() -> None:
    requests: list[tuple[str, str]] = []

    async def control_handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url.path))
        if request.method == "POST":
            return httpx.Response(
                201,
                json={
                    **CREATE_RESPONSE,
                    "ice_servers": [
                        {
                            "urls": ["turn:turn.example:3478"],
                            "username": "publisher",
                            "credential": "turn-secret",
                        }
                    ],
                },
            )
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(control_handler)
    ) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        with pytest.raises(RelayError) as unsupported:
            await RelaySession.create(
                control_plane_url="https://control.example",
                control_client=control,
            )

    assert getattr(unsupported.value, "code", None) == "relay.unsupported_ice_server"
    assert "turn-secret" not in str(unsupported.value)
    assert requests == [
        ("POST", "/v1/sessions"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


@pytest.mark.asyncio
async def test_async_relay_wait_retries_transient_control_transport_failure() -> None:
    get_calls = 0

    async def control_handler(request: httpx.Request) -> httpx.Response:
        nonlocal get_calls
        if request.method == "POST":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            get_calls += 1
            if get_calls == 1:
                raise httpx.ReadTimeout("temporary read timeout", request=request)
            return httpx.Response(200, json=_snapshot(ready=True, subscription_count=0))
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(control_handler)
    ) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        remote = await RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            control_client=control,
        )

        activation = await remote.wait_for_publisher(
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )

        assert activation.snapshot.ready is True
        assert get_calls == 2
        await remote.aclose()


@pytest.mark.asyncio
async def test_async_relay_endpoint_mismatch_deletes_created_remote_session() -> None:
    requests: list[httpx.Request] = []

    async def control_handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST":
            return httpx.Response(
                201,
                json={
                    **CREATE_RESPONSE,
                    "whep_url": (
                        "https://other-relay.example/v1/sessions/session_123/whep"
                    ),
                },
            )
        return httpx.Response(204)

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(control_handler)
    ) as http_client:
        control = ControlClient(
            "https://control.example",
            http_client=http_client,
        )
        with pytest.raises(RelayError) as mismatch:
            await RelaySession.create(
                control_plane_url="https://control.example",
                control_client=control,
            )
    assert getattr(mismatch.value, "code", None) == "relay.response_identity"
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/v1/sessions"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


def _snapshot(*, ready: bool, subscription_count: int) -> dict[str, object]:
    return {
        "session_id": "session_123",
        "state_revision": 2,
        "relay_epoch": "relay-epoch-1",
        "relay_revision": 2,
        "required_buses": ["application", "microphone"],
        "buses": [
            {
                "bus_id": bus_id,
                "role": "voice",
                "source_active": ready,
                "source_generation": 1 if ready else 0,
            }
            for bus_id in ("application", "microphone")
        ],
        "subscriptions": (
            [{"subscriber_id": "receiver_1", "bus_id": "mix"}]
            if subscription_count
            else []
        ),
        "ready": ready,
        "source_active": ready,
        "subscription_count": subscription_count,
        "codec": "opus",
    }
