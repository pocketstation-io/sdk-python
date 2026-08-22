"""Real relay declaration, invitation, readiness, and secrecy contracts."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from pocketstation._api import (
    ControlClient,
    RelayError,
    RelaySession,
    RelayTimeoutError,
    Session,
    Source,
)

CREATE_RESPONSE = {
    "session_id": "session_123",
    "required_buses": ["application", "microphone"],
    "source_token": "source-secret",
    "whip_url": "https://relay.example/v1/sessions/session_123/whip",
    "whep_url": "https://relay.example/v1/sessions/session_123/whep",
    "ice_servers": [],
}


def test_relay_session_rejects_unbounded_request_timeout() -> None:
    with pytest.raises((TypeError, ValueError)):
        RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            request_timeout_seconds=None,
        )


def test_relay_composes_two_native_buses_with_authoritative_readiness() -> None:
    control_requests: list[httpx.Request] = []
    snapshots = iter(
        [
            _snapshot(ready=True, subscription_count=0),
            _snapshot(ready=True, subscription_count=1),
        ]
    )

    def control_handler(request: httpx.Request) -> httpx.Response:
        control_requests.append(request)
        if request.method == "POST" and request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE_RESPONSE)
        assert request.headers["authorization"] == "Bearer source-secret"
        if request.method == "GET":
            return httpx.Response(200, json=next(snapshots))
        if request.method == "POST" and request.url.path.endswith("/invitations"):
            return httpx.Response(
                201,
                json={
                    "join_code": "opaque-code",
                    "join_url": (
                        "https://receiver.example/?join=opaque-code"
                        "&control=https%3A%2F%2Fcontrol.example"
                    ),
                    "expires_at": "2026-08-21T18:00:00Z",
                },
            )
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient(
            "https://control.example",
            http_client=control_http,
        )
        remote = RelaySession.create(
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

        with pytest.raises(RelayError) as early_invitation:
            remote.create_receiver_invitation()
        assert early_invitation.value.code == "relay.publisher_not_active"

        publisher_ready = remote.wait_for_publisher(
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )
        invitation = remote.create_receiver_invitation()
        receiver_ready = remote.wait_for_receiver(
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )

        assert app_route.bus_id == "application"
        assert mic_route.bus_id == "microphone"
        assert app_route.route_id != mic_route.route_id
        assert publisher_ready.snapshot.ready is True
        assert publisher_ready.snapshot.subscription_count == 0
        assert receiver_ready.snapshot.subscription_count == 1
        assert remote.relay_url == "https://relay.example"
        assert "source-secret" not in repr(remote)

        parsed = urlparse(invitation.join_url)
        assert parse_qs(parsed.query)["join"] == ["opaque-code"]
        assert "token" not in parsed.query
        assert "session_123" not in invitation.join_url

        remote.close()
        remote.close()

    assert [(request.method, request.url.path) for request in control_requests] == [
        ("POST", "/v1/sessions"),
        ("GET", "/v1/sessions/session_123"),
        ("POST", "/v1/sessions/session_123/invitations"),
        ("GET", "/v1/sessions/session_123"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


def test_relay_wait_uses_a_single_bounded_deadline() -> None:
    def control_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            return httpx.Response(
                200, json=_snapshot(ready=False, subscription_count=0)
            )
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient(
            "https://control.example",
            http_client=control_http,
        )
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            control_client=control,
        )
        with pytest.raises(RelayTimeoutError) as timeout:
            remote.wait_for_publisher(
                timeout_seconds=0.005,
                poll_interval_seconds=0.001,
            )
        assert timeout.value.code == "relay.publisher_timeout"
        remote.close()


@pytest.mark.parametrize(
    "join_url",
    [
        "https://receiver.example/?join=wrong-code",
        "https://receiver.example/?join=opaque-code&token=subscriber-secret",
        "https://receiver.example/?join=opaque-code&session_id=session_123",
        "https://receiver.example/?join=opaque-code#session_123",
    ],
)
def test_relay_rejects_unsafe_or_mismatched_invitations(join_url: str) -> None:
    get_calls = 0

    def control_handler(request: httpx.Request) -> httpx.Response:
        nonlocal get_calls
        if request.method == "POST" and request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            get_calls += 1
            return httpx.Response(200, json=_snapshot(ready=True, subscription_count=0))
        if request.method == "POST" and request.url.path.endswith("/invitations"):
            return httpx.Response(
                201,
                json={
                    "join_code": "opaque-code",
                    "join_url": join_url,
                    "expires_at": "2026-08-21T18:00:00Z",
                },
            )
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient(
            "https://control.example",
            http_client=control_http,
        )
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            control_client=control,
        )
        remote.wait_for_publisher(
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )
        with pytest.raises(RelayError) as unsafe:
            remote.create_receiver_invitation()
        assert unsafe.value.code in {
            "relay.response_identity",
            "relay.unsafe_invitation",
        }
        remote.close()
    assert get_calls == 1


def test_invalid_relay_origin_fails_before_remote_session_creation() -> None:
    requests: list[httpx.Request] = []
    transport = httpx.MockTransport(
        lambda request: (
            requests.append(request),
            httpx.Response(500),
        )[1]
    )
    with httpx.Client(transport=transport) as http_client:
        control = ControlClient(
            "https://control.example",
            http_client=http_client,
        )
        with pytest.raises(ValueError, match="must not include a path"):
            RelaySession.create(
                control_plane_url="https://control.example",
                relay_url="https://relay.example/not-an-origin",
                control_client=control,
            )
    assert requests == []


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
