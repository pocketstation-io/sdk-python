"""Real relay declaration, invitation, readiness, and secrecy contracts."""

from __future__ import annotations

import json

import httpx
import pytest
from pocketstation import _native
from pocketstation._api import (
    ControlClient,
    ControlPlaneError,
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


def test_relay_session_rejects_unbounded_request_timeout() -> None:
    with pytest.raises((TypeError, ValueError)):
        RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            request_timeout_seconds=None,
        )


@pytest.mark.parametrize("word_count", [None, 3])
def test_relay_composes_two_native_buses_with_authoritative_readiness(
    word_count: int | None,
) -> None:
    control_requests: list[httpx.Request] = []
    snapshots = iter(
        [
            _snapshot(ready=True, subscription_count=0),
            _snapshot(ready=True, subscription_count=1),
            _snapshot(ready=True, subscription_count=2),
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
            return httpx.Response(201, json=INVITATION_RESPONSE)
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient(
            "https://control.example",
            http_client=control_http,
        )
        remote = RelaySession.create(
            control_plane_url="https://control.example",
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
        invitation = remote.create_receiver_invitation(word_count=word_count)
        receiver_ready = remote.wait_for_receiver(
            minimum_receivers=2,
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )

        assert app_route.bus_id == "application"
        assert mic_route.bus_id == "microphone"
        assert app_route.route_id != mic_route.route_id
        assert publisher_ready.snapshot.ready is True
        assert publisher_ready.snapshot.subscription_count == 0
        assert receiver_ready.snapshot.subscription_count == 2
        assert remote.relay_url == "https://relay.example"
        assert "source-secret" not in repr(remote)

        assert invitation.join_code.expose_secret() == JOIN_CODE
        assert invitation.share_alias == "gentleglow-cedarbloom-riverglen"
        assert invitation.share_url is not None
        assert str(invitation.share_url) == "[redacted]"
        assert "share-secret" not in repr(invitation)
        assert invitation.expose_url().endswith(f"#join={JOIN_CODE}")
        assert "session_123" not in invitation.expose_url()

        remote.close()
        remote.close()

    assert [(request.method, request.url.path) for request in control_requests] == [
        ("POST", "/v1/sessions"),
        ("GET", "/v1/sessions/session_123"),
        ("POST", "/v1/sessions/session_123/invitations"),
        ("GET", "/v1/sessions/session_123"),
        ("GET", "/v1/sessions/session_123"),
        ("DELETE", "/v1/sessions/session_123"),
    ]
    expected = {"bus_id": "mix"}
    if word_count is not None:
        expected["word_count"] = word_count
    assert json.loads(control_requests[2].content) == expected


def test_relay_forwards_control_plane_stun_servers_to_native_publisher() -> None:
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

    def control_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(201, json=response)
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        remote = RelaySession.create(
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
        remote.close()

    assert calls == [
        (
            "https://relay.example",
            "session_123",
            "source-secret",
            [["stun:stun.example:3478"]],
        )
    ]


@pytest.mark.parametrize(
    "ice_server",
    [
        {
            "urls": ["turn:turn.example:3478"],
            "username": None,
            "credential": None,
        },
        {
            "urls": ["stun:stun.example:3478"],
            "username": "publisher",
            "credential": "turn-secret",
        },
    ],
)
def test_relay_rejects_unsupported_ice_and_deletes_remote_session(
    ice_server: dict[str, object],
) -> None:
    requests: list[tuple[str, str]] = []

    def control_handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url.path))
        if request.method == "POST":
            return httpx.Response(
                201,
                json={**CREATE_RESPONSE, "ice_servers": [ice_server]},
            )
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        with pytest.raises(RelayError) as unsupported:
            RelaySession.create(
                control_plane_url="https://control.example",
                control_client=control,
            )

    assert unsupported.value.code == "relay.unsupported_ice_server"
    assert "turn-secret" not in str(unsupported.value)
    assert requests == [
        ("POST", "/v1/sessions"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


def test_native_relay_route_accepts_stun_configuration() -> None:
    session = _native.Session()
    source = session.audio_input(48_000, 1)
    publisher = session.relay(
        "https://relay.example",
        "session_123",
        "source-secret",
        [["stun:stun.example:3478"]],
    )

    route_id = source.output.publish(publisher, "application")

    assert int(route_id) > 0


def test_native_relay_route_rejects_unsupported_ice_configuration() -> None:
    with pytest.raises(ValueError, match=r"\[relay\.invalid_configuration\]"):
        _native.Session().relay(
            "https://relay.example",
            "session_123",
            "source-secret",
            [["turn:turn.example:3478"]],
        )


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


def test_relay_wait_retries_transient_control_transport_failure() -> None:
    get_calls = 0

    def control_handler(request: httpx.Request) -> httpx.Response:
        nonlocal get_calls
        if request.method == "POST":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            get_calls += 1
            if get_calls == 1:
                raise httpx.ReadTimeout("temporary read timeout", request=request)
            return httpx.Response(200, json=_snapshot(ready=True, subscription_count=0))
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as control_http:
        control = ControlClient("https://control.example", http_client=control_http)
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="https://relay.example",
            control_client=control,
        )

        activation = remote.wait_for_publisher(
            timeout_seconds=0.1,
            poll_interval_seconds=0.001,
        )

        assert activation.snapshot.ready is True
        assert get_calls == 2
        remote.close()


@pytest.mark.parametrize(
    "join_url",
    [
        (
            "https://receiver.example/join/"
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa#secret=share-secret"
        ),
        (
            f"https://receiver.example/join/{JOIN_CODE}"
            "?token=subscriber-secret#secret=share-secret"
        ),
        (
            f"https://receiver.example/join/{JOIN_CODE}"
            "?session_id=session_123#secret=share-secret"
        ),
        (f"https://receiver.example/join/{JOIN_CODE}/session_123#secret=share-secret"),
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
                    **INVITATION_RESPONSE,
                    "join_url": join_url,
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
        with pytest.raises((ControlPlaneError, RelayError)) as unsafe:
            remote.create_receiver_invitation()
        assert unsafe.value.code in {
            "control.response_decode",
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


def test_relay_origin_rejects_query_and_fragment_before_creation() -> None:
    for relay_url in (
        "https://relay.example?authority=other",
        "https://relay.example#secret",
    ):
        with pytest.raises(ValueError, match="must not include"):
            RelaySession.create(
                control_plane_url="https://control.example",
                relay_url=relay_url,
            )


def test_relay_origin_is_canonicalized_like_a_web_url() -> None:
    def control_handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(
                201,
                json={
                    **CREATE_RESPONSE,
                    "whip_url": (
                        "HTTPS://Relay.Example:443/v1/sessions/session_123/whip"
                    ),
                    "whep_url": (
                        "HTTPS://Relay.Example:443/v1/sessions/session_123/whep"
                    ),
                },
            )
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as http_client:
        control = ControlClient(
            "https://control.example",
            http_client=http_client,
        )
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            relay_url="HTTPS://Relay.Example:443/",
            control_client=control,
        )
        assert remote.relay_url == "https://relay.example"
        remote.close()


def test_relay_endpoint_mismatch_deletes_created_remote_session() -> None:
    requests: list[httpx.Request] = []

    def control_handler(request: httpx.Request) -> httpx.Response:
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

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as http_client:
        control = ControlClient(
            "https://control.example",
            http_client=http_client,
        )
        with pytest.raises(RelayError) as mismatch:
            RelaySession.create(
                control_plane_url="https://control.example",
                control_client=control,
            )
    assert mismatch.value.code == "relay.response_identity"
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
