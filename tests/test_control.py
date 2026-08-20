"""Bounded, typed control-plane client contract tests."""

from __future__ import annotations

import httpx
import pytest
from pocketstation import (
    ControlClient,
    ControlPlaneError,
    SecretToken,
    SessionId,
)
from pocketstation.aio import ControlClient as AsyncControlClient

CREATE_RESPONSE = {
    "session_id": "session_123",
    "source_token": "source-secret",
    "subscriber_token": "subscriber-secret",
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


def test_sync_client_maps_the_exact_session_contract_and_redacts_tokens() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST" and request.url.path.endswith("/v1/sessions"):
            return httpx.Response(201, json=CREATE_RESPONSE)
        if request.method == "GET":
            return httpx.Response(
                200,
                json={
                    "session_id": "session_123",
                    "source_active": True,
                    "subscription_count": 2,
                    "codec": "opus",
                },
            )
        if request.url.path.endswith("/subscribe"):
            return httpx.Response(
                200,
                json={
                    "session_id": "session_123",
                    "subscriber_token": "next-subscriber-secret",
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
            snapshot = client.session(credentials.session_id)
            subscriber = client.issue_subscriber_credentials(credentials.session_id)
            client.delete_session(credentials.session_id, credentials.source_token)

    assert credentials.session_id == SessionId("session_123")
    assert credentials.source_token.expose_secret() == "source-secret"
    assert "source-secret" not in repr(credentials.source_token)
    assert credentials.ice_servers[0].urls == ("turn:turn.example:3478",)
    assert credentials.ice_servers[0].credential is not None
    assert credentials.ice_servers[0].credential.expose_secret() == "turn-secret"
    assert "turn-secret" not in repr(credentials)
    assert snapshot.source_active is True
    assert snapshot.subscription_count == 2
    assert subscriber.subscriber_token.expose_secret() == "next-subscriber-secret"
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/base/v1/sessions"),
        ("GET", "/base/v1/sessions/session_123"),
        ("POST", "/base/v1/sessions/session_123/subscribe"),
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
                200,
                json={
                    "session_id": "session_123",
                    "source_active": False,
                    "subscription_count": 0,
                    "codec": "opus",
                },
            )
        if request.url.path.endswith("/subscribe"):
            return httpx.Response(
                200,
                json={
                    "session_id": "session_123",
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
            snapshot = await client.session(credentials.session_id)
            subscriber = await client.issue_subscriber_credentials(
                credentials.session_id
            )
            await client.delete_session(
                credentials.session_id,
                credentials.source_token,
            )

    assert snapshot.source_active is False
    assert subscriber.subscriber_token.expose_secret() == "next-subscriber-secret"
    assert [(request.method, request.url.path) for request in requests] == [
        ("POST", "/v1/sessions"),
        ("GET", "/v1/sessions/session_123"),
        ("POST", "/v1/sessions/session_123/subscribe"),
        ("DELETE", "/v1/sessions/session_123"),
    ]


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
                    "session_id": "session_123",
                    "source_active": True,
                    "subscription_count": value,
                    "codec": "opus",
                },
            )
        )
        with httpx.Client(transport=transport) as http_client:
            client = ControlClient("https://control.example", http_client=http_client)
            with pytest.raises(ControlPlaneError) as raised:
                client.session("session_123")
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

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    ) as http_client:
        client = AsyncControlClient(
            "https://control.example",
            timeout_seconds=7.0,
            http_client=http_client,
        )
        await client.create_session(timeout_seconds=None)

    assert observed == [7.0]
