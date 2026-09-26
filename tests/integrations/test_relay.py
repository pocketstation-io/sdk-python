from __future__ import annotations

from typing import Any, cast

import httpx
import pytest
from pocketstation._api import ControlClient, RelaySession, Session


def test_relay_integration_is_bounded_secret_safe_and_idempotently_closed() -> None:
    source_token = "catalog-source-secret"
    requests: list[tuple[str, str]] = []

    def control_handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url.path))
        if request.method == "POST":
            return httpx.Response(
                201,
                json={
                    "session_id": "catalog-session",
                    "required_buses": ["application", "microphone"],
                    "source_token": source_token,
                    "whip_url": (
                        "https://relay.example/v1/sessions/catalog-session/whip"
                    ),
                    "whep_url": (
                        "https://relay.example/v1/sessions/catalog-session/whep"
                    ),
                    "ice_servers": [],
                },
            )
        assert request.headers["authorization"] == f"Bearer {source_token}"
        return httpx.Response(204)

    with httpx.Client(transport=httpx.MockTransport(control_handler)) as http:
        control = ControlClient("https://control.example", http_client=http)
        remote = RelaySession.create(
            control_plane_url="https://control.example",
            request_timeout_seconds=1.0,
            control_client=control,
        )
        publisher = remote.publisher(Session())

        assert publisher.relay_url == "https://relay.example"
        assert source_token not in repr(remote)
        assert source_token not in repr(publisher)

        remote.close()
        remote.close()

    assert requests == [
        ("POST", "/v1/sessions"),
        ("DELETE", "/v1/sessions/catalog-session"),
    ]


@pytest.mark.parametrize("timeout", [None, True, 0.0, 301.0, float("inf")])
def test_relay_integration_rejects_unbounded_request_deadlines(
    timeout: object,
) -> None:
    with pytest.raises((TypeError, ValueError)):
        RelaySession.create(
            control_plane_url="https://control.example",
            request_timeout_seconds=cast(Any, timeout),
        )
