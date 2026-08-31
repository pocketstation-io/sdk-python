"""Async relay surface symmetry over the same Rust and service contracts."""

from __future__ import annotations

import httpx
import pytest
from pocketstation._api import Source
from pocketstation.aio._api import ControlClient, RelaySession, Session

CREATE_RESPONSE = {
    "session_id": "session_123",
    "required_buses": ["application", "microphone"],
    "source_token": "source-secret",
    "whip_url": "https://relay.example/v1/sessions/session_123/whip",
    "whep_url": "https://relay.example/v1/sessions/session_123/whep",
    "ice_servers": [],
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
            return httpx.Response(
                201,
                json={
                    "join_code": "opaque-code",
                    "join_url": "https://receiver.example/?join=opaque-code",
                    "expires_at": "2026-08-21T18:00:00Z",
                },
            )
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
            relay_url="https://relay.example/",
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
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )

        assert app_route.route_id != mic_route.route_id
        assert invitation.join_code == "opaque-code"
        assert receiver.snapshot.subscription_count == 1
        assert "source-secret" not in repr(remote)

        await remote.aclose()
        await remote.aclose()

    assert [(request.method, request.url.path) for request in control_requests] == [
        ("POST", "/v1/sessions"),
        ("GET", "/v1/sessions/session_123"),
        ("POST", "/v1/sessions/session_123/invitations"),
        ("GET", "/v1/sessions/session_123"),
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
