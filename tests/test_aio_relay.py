"""Async relay surface symmetry over the same Rust and service contracts."""

from __future__ import annotations

import httpx
import pytest
from pocketstation import Source
from pocketstation.aio import ControlClient, RelaySession, Session

CREATE_RESPONSE = {
    "session_id": "session_123",
    "source_token": "source-secret",
    "subscriber_token": "subscriber-secret",
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
    relay_requests: list[httpx.Request] = []
    snapshots = iter([_snapshot(True, 0), _snapshot(True, 1)])

    async def control_handler(request: httpx.Request) -> httpx.Response:
        control_requests.append(request)
        if request.method == "POST":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            return httpx.Response(200, json=next(snapshots))
        return httpx.Response(204)

    async def relay_handler(request: httpx.Request) -> httpx.Response:
        relay_requests.append(request)
        assert request.headers["authorization"] == "Bearer source-secret"
        return httpx.Response(
            201,
            json={
                "session_id": "session_123",
                "join_code": "opaque-code",
                "join_url": "https://receiver.example/?join=opaque-code",
            },
        )

    async with (
        httpx.AsyncClient(
            transport=httpx.MockTransport(control_handler)
        ) as control_http,
        httpx.AsyncClient(transport=httpx.MockTransport(relay_handler)) as relay_http,
    ):
        control = ControlClient(
            "https://control.example",
            http_client=control_http,
        )
        remote = await RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example/",
            control_client=control,
            relay_http_client=relay_http,
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
        ("GET", "/v1/sessions/session_123"),
        ("DELETE", "/v1/sessions/session_123"),
    ]
    assert len(relay_requests) == 1


def _snapshot(source_active: bool, subscription_count: int) -> dict[str, object]:
    return {
        "session_id": "session_123",
        "source_active": source_active,
        "subscription_count": subscription_count,
        "codec": "opus",
    }
