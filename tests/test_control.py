"""Bounded, typed control-plane client contract tests."""

from __future__ import annotations

import json

import httpx
import pytest
from pocketstation._api import (
    ControlClient,
    ControlPlaneError,
    SecretToken,
    SessionId,
)
from pocketstation.aio._api import ControlClient as AsyncControlClient

CREATE_RESPONSE = {
    "session_id": "session_123",
    "required_buses": ["application", "microphone"],
    "source_token": "source-secret",
    "whip_url": "https://relay.example/v1/sessions/session_123/whip",
    "whep_url": "https://relay.example/v1/sessions/session_123/whep",
    "ice_servers": [
        {
            "urls": ["turn:turn.example:3478"],
            "username": "session_123",
            "credential": "turn-secret",
        }
    ],
}

PUBLISH_RESPONSE = {
    "session_id": "session_123",
    "bus_id": "microphone",
    "publisher_token": "media-only-secret",
    "signal_url": "wss://relay.example/v1/signal",
    "ice_servers": CREATE_RESPONSE["ice_servers"],
}


def _snapshot(*, ready: bool, subscription_count: int) -> dict[str, object]:
    buses = [
        {
            "bus_id": bus_id,
            "role": "voice",
            "source_active": ready,
            "source_generation": 1 if ready else 0,
        }
        for bus_id in ("application", "microphone")
    ]
    return {
        "session_id": "session_123",
        "state_revision": 3,
        "relay_epoch": "relay-epoch-1" if ready else "",
        "relay_revision": 2 if ready else 0,
        "required_buses": ["application", "microphone"],
        "buses": buses,
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


def test_sync_client_maps_the_exact_session_contract_and_redacts_tokens() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path.endswith("/v1/sessions"):
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            return httpx.Response(200, json=_snapshot(ready=True, subscription_count=1))
        if request.url.path.endswith("/subscribe"):
            return httpx.Response(
                200,
                json={
                    "session_id": "session_123",
                    "bus_id": "mix",
                    "subscriber_token": "next-subscriber-secret",
                },
            )
        if request.url.path.endswith("/invitations"):
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
        assert request.headers["authorization"] == "Bearer source-secret"
        return httpx.Response(204)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http_client:
        with ControlClient(
            "https://control.example/base?discarded=yes",
            http_client=http_client,
        ) as client:
            credentials = client.create_session()
            snapshot = client.session(credentials.session_id, credentials.source_token)
            subscriber = client.issue_subscriber_credentials(
                credentials.session_id, credentials.source_token
            )
            invitation = client.create_invitation(
                credentials.session_id, credentials.source_token
            )
            client.delete_session(credentials.session_id, credentials.source_token)

    assert credentials.session_id == SessionId("session_123")
    assert credentials.source_token.expose_secret() == "source-secret"
    assert "source-secret" not in repr(credentials.source_token)
    assert credentials.ice_servers[0].urls == ("turn:turn.example:3478",)
    assert credentials.ice_servers[0].credential is not None
    assert credentials.ice_servers[0].credential.expose_secret() == "turn-secret"
    assert "turn-secret" not in repr(credentials)
    assert credentials.required_buses == ("application", "microphone")
    assert snapshot.ready is True
    assert snapshot.subscription_count == 1
    assert snapshot.buses[0].source_generation == 1
    assert subscriber.subscriber_token.expose_secret() == "next-subscriber-secret"
    assert subscriber.bus_id == "mix"
    assert invitation.join_code == "opaque-code"
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/base/v1/sessions"),
        ("GET", "/base/v1/sessions/session_123"),
        ("POST", "/base/v1/sessions/session_123/subscribe"),
        ("POST", "/base/v1/sessions/session_123/invitations"),
        ("DELETE", "/base/v1/sessions/session_123"),
    ]


@pytest.mark.asyncio
async def test_async_client_has_the_same_wire_contract() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path == "/v1/sessions":
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            return httpx.Response(
                200, json=_snapshot(ready=False, subscription_count=0)
            )
        if request.url.path.endswith("/subscribe"):
            return httpx.Response(
                200,
                json={
                    "session_id": "session_123",
                    "bus_id": "mix",
                    "subscriber_token": "next-subscriber-secret",
                },
            )
        assert request.headers["authorization"] == "Bearer source-secret"
        return httpx.Response(204)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as http_client:
        async with AsyncControlClient(
            "https://control.example",
            http_client=http_client,
        ) as client:
            credentials = await client.create_session()
            snapshot = await client.session(
                credentials.session_id, credentials.source_token
            )
            subscriber = await client.issue_subscriber_credentials(
                credentials.session_id, credentials.source_token
            )
            await client.delete_session(
                credentials.session_id,
                credentials.source_token,
            )

    assert snapshot.ready is False
    assert subscriber.subscriber_token.expose_secret() == "next-subscriber-secret"
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/v1/sessions"),
        ("GET", "/v1/sessions/session_123"),
        ("POST", "/v1/sessions/session_123/subscribe"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


def test_sync_publisher_credentials_have_exact_wire_and_redacted_secrets() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=PUBLISH_RESPONSE)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = ControlClient("https://control.example", http_client=http_client)
        publisher = client.issue_publisher_credentials(
            "session_123", SecretToken("source-secret"), bus_id="microphone"
        )

    assert publisher.session_id == SessionId("session_123")
    assert publisher.bus_id == "microphone"
    assert publisher.signal_url == "wss://relay.example/v1/signal"
    assert publisher.ice_servers[0].urls == ("turn:turn.example:3478",)
    assert publisher.publisher_token.expose_secret() == "media-only-secret"
    assert "media-only-secret" not in repr(publisher)
    assert "turn-secret" not in repr(publisher)
    assert len(requests) == 1
    assert requests[0].method == "POST"
    assert requests[0].url.path == "/v1/sessions/session_123/publish"
    assert requests[0].headers["authorization"] == "Bearer source-secret"
    assert json.loads(requests[0].content) == {"bus_id": "microphone"}


@pytest.mark.asyncio
async def test_async_client_issues_exact_bus_publisher_credentials() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=PUBLISH_RESPONSE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AsyncControlClient("https://control.example", http_client=http_client)
        publisher = await client.issue_publisher_credentials(
            "session_123", SecretToken("source-secret"), bus_id="microphone"
        )

    assert publisher.publisher_token.expose_secret() == "media-only-secret"
    assert publisher.bus_id == "microphone"
    assert "media-only-secret" not in repr(publisher)
    assert len(requests) == 1
    assert requests[0].url.path == "/v1/sessions/session_123/publish"
    assert requests[0].headers["authorization"] == "Bearer source-secret"
    assert json.loads(requests[0].content) == {"bus_id": "microphone"}


@pytest.mark.parametrize("bus_id", ["", "with/slash", "x" * 65])
def test_publisher_rejects_invalid_bus_before_network(bus_id: str) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("invalid bus ID reached the network")

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = ControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ValueError):
            client.issue_publisher_credentials(
                "session_123", SecretToken("source-secret"), bus_id=bus_id
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("bus_id", ["", "with/slash", "x" * 65])
async def test_async_publisher_rejects_invalid_bus_before_network(bus_id: str) -> None:
    async def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("invalid bus ID reached the network")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AsyncControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ValueError):
            await client.issue_publisher_credentials(
                "session_123", SecretToken("source-secret"), bus_id=bus_id
            )


@pytest.mark.parametrize(
    "field,value,expected_code",
    [
        ("bus_id", "with/slash", "control.response_decode"),
        ("publisher_token", "", "control.response_decode"),
        ("publisher_token", "x" * 4_097, "control.response_decode"),
        ("session_id", "with/slash", "control.response_decode"),
        ("signal_url", "https://relay.example/v1/signal", "control.response_decode"),
        ("ice_servers", [{}] * 33, "control.response_too_large"),
        (
            "ice_servers",
            [{"urls": ["turn:turn.example:3478"], "credential": ""}],
            "control.response_decode",
        ),
    ],
)
def test_publisher_rejects_invalid_control_response(
    field: str, value: object, expected_code: str
) -> None:
    response = {**PUBLISH_RESPONSE, field: value}
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, json=response)
        )
    ) as http_client:
        client = ControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ControlPlaneError) as raised:
            client.issue_publisher_credentials(
                "session_123", SecretToken("source-secret"), bus_id="microphone"
            )
    assert raised.value.code == expected_code


def test_publisher_http_failure_redacts_source_capability() -> None:
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(403, text="denied source-secret")
        )
    ) as http_client:
        client = ControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ControlPlaneError) as raised:
            client.issue_publisher_credentials(
                "session_123", SecretToken("source-secret"), bus_id="microphone"
            )
    assert raised.value.code == "control.http_status"
    assert raised.value.status_code == 403
    assert "source-secret" not in str(raised.value)
    assert "[redacted]" in str(raised.value)


@pytest.mark.asyncio
async def test_async_publisher_rejects_bad_response_and_redacts_denial() -> None:
    async def malformed(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={**PUBLISH_RESPONSE, "signal_url": "http://bad"}
        )

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(malformed)
    ) as http_client:
        client = AsyncControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ControlPlaneError) as raised:
            await client.issue_publisher_credentials(
                "session_123", SecretToken("source-secret"), bus_id="microphone"
            )
    assert raised.value.code == "control.response_decode"

    async def denied(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="denied source-secret")

    async with httpx.AsyncClient(transport=httpx.MockTransport(denied)) as http_client:
        client = AsyncControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ControlPlaneError) as raised:
            await client.issue_publisher_credentials(
                "session_123", SecretToken("source-secret"), bus_id="microphone"
            )
    assert raised.value.status_code == 403
    assert "source-secret" not in str(raised.value)


def test_control_client_bounds_response_bodies() -> None:
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(201, content=b"x" * 65_537)
    )
    with httpx.Client(transport=transport) as http_client:
        client = ControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ControlPlaneError) as raised:
            client.create_session()

    assert raised.value.code == "control.response_too_large"


def test_control_client_redacts_authorization_from_http_error() -> None:
    token = SecretToken("must-not-leak")
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(401, text="rejected must-not-leak")
    )
    with httpx.Client(transport=transport) as http_client:
        client = ControlClient("https://control.example", http_client=http_client)
        with pytest.raises(ControlPlaneError) as raised:
            client.delete_session("session_123", token)

    assert "must-not-leak" not in str(raised.value)
    assert "[redacted]" in str(raised.value)


@pytest.mark.parametrize("value", ["", "../escape", "with/slash", "café"])
def test_session_id_rejects_unsafe_path_values(value: str) -> None:
    with pytest.raises(ValueError):
        SessionId(value)


def test_control_decoder_rejects_boolean_or_negative_subscription_counts() -> None:
    for invalid in (True, -1):
        transport = httpx.MockTransport(
            lambda _request, value=invalid: httpx.Response(
                200,
                json={
                    **_snapshot(ready=True, subscription_count=0),
                    "subscription_count": value,
                },
            )
        )
        with httpx.Client(transport=transport) as http_client:
            client = ControlClient("https://control.example", http_client=http_client)
            with pytest.raises(ControlPlaneError) as raised:
                client.session("session_123", SecretToken("source-secret"))
        assert raised.value.code == "control.response_decode"


@pytest.mark.parametrize(
    "url",
    ["https://user:password@control.example", "ftp://control.example"],
)
def test_control_origin_rejects_embedded_credentials_and_non_http(url: str) -> None:
    with pytest.raises(ValueError):
        ControlClient(url)


@pytest.mark.parametrize("timeout", [None, True, 0, -1, 301])
def test_control_client_rejects_invalid_timeouts(timeout) -> None:
    with pytest.raises((TypeError, ValueError)):
        ControlClient("https://control.example", timeout_seconds=timeout)


@pytest.mark.asyncio
@pytest.mark.parametrize("timeout", [None, True, 0, -1, 301])
async def test_async_control_client_rejects_invalid_timeouts(timeout) -> None:
    with pytest.raises((TypeError, ValueError)):
        AsyncControlClient("https://control.example", timeout_seconds=timeout)


def test_per_request_none_inherits_the_finite_client_timeout() -> None:
    observed: list[float | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request.extensions["timeout"]["read"])
        return httpx.Response(201, json=CREATE_RESPONSE)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = ControlClient(
            "https://control.example",
            timeout_seconds=7.0,
            http_client=http_client,
        )
        client.create_session(timeout_seconds=None)

    assert observed == [7.0]


@pytest.mark.asyncio
async def test_async_per_request_none_inherits_the_finite_client_timeout() -> None:
    observed: list[float | None] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request.extensions["timeout"]["read"])
        return httpx.Response(201, json=CREATE_RESPONSE)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AsyncControlClient(
            "https://control.example",
            timeout_seconds=7.0,
            http_client=http_client,
        )
        await client.create_session(timeout_seconds=None)

    assert observed == [7.0]
