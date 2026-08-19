"""Explicit control and declaration composition for the real relay services."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic, sleep
from types import TracebackType
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, quote, urljoin, urlparse

import httpx

from ._native import RelayPublisher as _NativeRelayPublisher
from .control import (
    ControlClient,
    SecretToken,
    SessionCredentials,
    SessionId,
    SessionSnapshot,
)
from .errors import PocketStationError, _native_call

if TYPE_CHECKING:
    from .session import Session

_MAX_RELAY_RESPONSE_BYTES = 16_384


class RelayError(PocketStationError):
    """A relay declaration, HTTP, activation, or lifecycle failure."""


class RelayTimeoutError(RelayError):
    """An authoritative publisher or receiver activation deadline expired."""


@dataclass(frozen=True, slots=True)
class RelayRoute:
    """One native Session route publishing a named AudioBus."""

    bus_id: str
    route_id: int


@dataclass(frozen=True, slots=True)
class PublisherActivation:
    """Control-plane snapshot after the relay confirmed a live source."""

    snapshot: SessionSnapshot


@dataclass(frozen=True, slots=True)
class ReceiverActivation:
    """Control-plane snapshot after relay WebRTC/downlink activation."""

    snapshot: SessionSnapshot


@dataclass(frozen=True, slots=True)
class ReceiverInvitation:
    """Opaque relay-issued browser invitation containing no subscriber token."""

    session_id: SessionId
    join_code: str
    url: str

    @property
    def join_url(self) -> str:
        return self.url


class RelayPublisher:
    """Session-scoped handle for the existing bounded Rust relay connector."""

    __slots__ = ("_native", "relay_url", "session_id")

    def __init__(
        self,
        native: _NativeRelayPublisher,
        *,
        relay_url: str,
        session_id: SessionId,
    ) -> None:
        self._native = native
        self.relay_url = relay_url
        self.session_id = session_id


class RelaySession:
    """Explicit owner of one remote Session and its bounded control clients.

    The object creates no relay, control-plane, browser, signaling, or media
    process. Callers provide already-running service origins. Audio remains in
    the canonical Rust Session and shared ``pocketstation-relay`` crate.
    """

    def __init__(
        self,
        *,
        relay_url: str,
        credentials: SessionCredentials,
        control: ControlClient,
        relay_http: httpx.Client,
        owns_control: bool,
        owns_relay_http: bool,
        request_timeout_seconds: float | None,
    ) -> None:
        self.relay_url = _normalize_relay_url(relay_url)
        self.credentials = credentials
        self._control = control
        self._relay_http = relay_http
        self._owns_control = owns_control
        self._owns_relay_http = owns_relay_http
        self._request_timeout_seconds = request_timeout_seconds
        self._publisher_activation: PublisherActivation | None = None
        self._invitation: ReceiverInvitation | None = None
        self._receiver_activation: ReceiverActivation | None = None
        self._closed = False

    @classmethod
    def create(
        cls,
        *,
        control_plane_url: str,
        relay_url: str,
        request_timeout_seconds: float | None = 10.0,
        control_client: ControlClient | None = None,
        relay_http_client: httpx.Client | None = None,
    ) -> RelaySession:
        _validate_optional_timeout(request_timeout_seconds, "request_timeout_seconds")
        normalized_relay_url = _normalize_relay_url(relay_url)
        owns_control = control_client is None
        owns_relay_http = relay_http_client is None
        control = control_client or ControlClient(
            control_plane_url,
            timeout_seconds=request_timeout_seconds,
        )
        relay_http = relay_http_client or httpx.Client(
            timeout=request_timeout_seconds,
        )
        try:
            credentials = control.create_session(
                timeout_seconds=request_timeout_seconds,
            )
        except Exception:
            if owns_relay_http:
                relay_http.close()
            if owns_control:
                control.close()
            raise
        return cls(
            relay_url=normalized_relay_url,
            credentials=credentials,
            control=control,
            relay_http=relay_http,
            owns_control=owns_control,
            owns_relay_http=owns_relay_http,
            request_timeout_seconds=request_timeout_seconds,
        )

    @property
    def session_id(self) -> SessionId:
        return self.credentials.session_id

    @property
    def publisher_activation(self) -> PublisherActivation | None:
        return self._publisher_activation

    @property
    def invitation(self) -> ReceiverInvitation | None:
        return self._invitation

    @property
    def receiver_activation(self) -> ReceiverActivation | None:
        return self._receiver_activation

    def publisher(self, session: Session) -> RelayPublisher:
        """Declare the native relay endpoint on an unstarted Session."""
        self._require_open()
        native = _native_call(
            lambda: session._native.relay(
                self.relay_url,
                str(self.session_id),
                self.credentials.source_token.expose_secret(),
            )
        )
        return RelayPublisher(
            native,
            relay_url=self.relay_url,
            session_id=self.session_id,
        )

    def wait_for_publisher(
        self,
        *,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> PublisherActivation:
        """Wait for the relay's source-active callback, within one deadline."""
        self._require_open()
        snapshot = self._wait_for_snapshot(
            lambda value: value.source_active,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            timeout_code="relay.publisher_timeout",
            timeout_message="relay publisher did not become active before the deadline",
        )
        activation = PublisherActivation(snapshot)
        self._publisher_activation = activation
        return activation

    def create_receiver_invitation(self) -> ReceiverInvitation:
        """Ask the relay for an opaque invitation after publisher activation."""
        self._require_open()
        if self._publisher_activation is None:
            raise RelayError(
                "wait_for_publisher() must succeed before creating an invitation",
                "relay.publisher_not_active",
            )
        payload = _relay_json_request(
            self._relay_http,
            relay_url=self.relay_url,
            method="POST",
            path=(f"v1/sessions/{quote(str(self.session_id), safe='')}/invitations"),
            expected_status=201,
            authorization=self.credentials.source_token,
            timeout_seconds=self._request_timeout_seconds,
        )
        invitation = _receiver_invitation(payload, self.session_id)
        self._invitation = invitation
        return invitation

    def wait_for_publisher_and_invitation(
        self,
        *,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverInvitation:
        self.wait_for_publisher(
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        return self.create_receiver_invitation()

    def wait_for_receiver(
        self,
        *,
        timeout_seconds: float = 30.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverActivation:
        """Wait for relay-confirmed WebRTC connection and downlink install."""
        self._require_open()
        if self._invitation is None:
            raise RelayError(
                "create_receiver_invitation() must succeed before waiting "
                "for a receiver",
                "relay.invitation_missing",
            )
        snapshot = self._wait_for_snapshot(
            lambda value: value.source_active and value.subscription_count > 0,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            timeout_code="relay.receiver_timeout",
            timeout_message="relay receiver did not become active before the deadline",
        )
        activation = ReceiverActivation(snapshot)
        self._receiver_activation = activation
        return activation

    def close(self, *, delete_remote_session: bool = True) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if delete_remote_session:
                self._control.delete_session(
                    self.session_id,
                    self.credentials.source_token,
                    timeout_seconds=self._request_timeout_seconds,
                )
        finally:
            if self._owns_relay_http:
                self._relay_http.close()
            if self._owns_control:
                self._control.close()

    def __enter__(self) -> RelaySession:
        self._require_open()
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        return (
            "RelaySession("
            f"session_id={self.session_id!r}, relay_url={self.relay_url!r}, "
            "credentials=[redacted])"
        )

    def _wait_for_snapshot(
        self,
        predicate: Callable[[SessionSnapshot], bool],
        *,
        timeout_seconds: float,
        poll_interval_seconds: float,
        timeout_code: str,
        timeout_message: str,
    ) -> SessionSnapshot:
        _validate_wait(timeout_seconds, poll_interval_seconds)
        deadline = monotonic() + timeout_seconds
        while True:
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise RelayTimeoutError(timeout_message, timeout_code)
            request_timeout = _bounded_request_timeout(
                remaining,
                self._request_timeout_seconds,
            )
            snapshot = self._control.session(
                self.session_id,
                timeout_seconds=request_timeout,
            )
            if predicate(snapshot):
                return snapshot
            sleep(min(poll_interval_seconds, max(0.0, deadline - monotonic())))

    def _require_open(self) -> None:
        if self._closed:
            raise RelayError("RelaySession has closed", "relay.closed")


def _normalize_relay_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("relay_url must be an absolute http or https origin")
    if parsed.path not in {"", "/"}:
        raise ValueError("relay_url must not include a path")
    return value.split("?", 1)[0].split("#", 1)[0].rstrip("/")


def _validate_optional_timeout(value: float | None, name: str) -> None:
    if value is not None and (isinstance(value, bool) or value <= 0):
        raise ValueError(f"{name} must be positive or None")


def _validate_wait(timeout_seconds: float, poll_interval_seconds: float) -> None:
    for name, value in (
        ("timeout_seconds", timeout_seconds),
        ("poll_interval_seconds", poll_interval_seconds),
    ):
        if isinstance(value, bool) or value <= 0:
            raise ValueError(f"{name} must be positive")


def _bounded_request_timeout(
    remaining_seconds: float,
    configured_seconds: float | None,
) -> float:
    if configured_seconds is None:
        return remaining_seconds
    return min(remaining_seconds, configured_seconds)


def _relay_json_request(
    client: httpx.Client,
    *,
    relay_url: str,
    method: str,
    path: str,
    expected_status: int,
    authorization: SecretToken,
    timeout_seconds: float | None,
) -> dict[str, Any]:
    exposed = authorization.expose_secret()
    try:
        with client.stream(
            method,
            urljoin(relay_url + "/", path),
            headers={"Authorization": f"Bearer {exposed}"},
            timeout=timeout_seconds,
        ) as response:
            body = _read_bounded(response.iter_bytes(), _MAX_RELAY_RESPONSE_BYTES)
            if response.status_code != expected_status:
                detail = body.decode("utf-8", errors="replace").replace(
                    exposed,
                    "[redacted]",
                )
                raise RelayError(
                    f"relay returned HTTP {response.status_code}: {detail}",
                    "relay.http_status",
                )
    except RelayError:
        raise
    except httpx.HTTPError as error:
        message = str(error).replace(exposed, "[redacted]")
        raise RelayError(f"relay request failed: {message}", "relay.request") from error
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RelayError(
            f"relay response could not be decoded: {error}",
            "relay.response_decode",
        ) from error
    if not isinstance(payload, dict):
        raise RelayError(
            "relay response must be a JSON object",
            "relay.response_decode",
        )
    return payload


def _read_bounded(chunks: Any, limit_bytes: int) -> bytes:
    body = bytearray()
    for chunk in chunks:
        remaining = limit_bytes + 1 - len(body)
        if remaining <= 0:
            break
        body.extend(chunk[:remaining])
    if len(body) > limit_bytes:
        raise RelayError(
            f"relay response exceeds {limit_bytes} bytes",
            "relay.response_too_large",
        )
    return bytes(body)


def _receiver_invitation(
    payload: dict[str, Any],
    expected_session_id: SessionId,
) -> ReceiverInvitation:
    session_id = SessionId(_required_string(payload, "session_id"))
    if session_id != expected_session_id:
        raise RelayError(
            "relay invitation belongs to a different Session",
            "relay.response_identity",
        )
    join_code = _required_string(payload, "join_code")
    invitation_url = _required_string(payload, "join_url")
    parsed = urlparse(invitation_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RelayError(
            "relay invitation URL must be absolute HTTP or HTTPS",
            "relay.response_decode",
        )
    query = parse_qs(parsed.query, keep_blank_values=True)
    unsafe_keys = {
        "session",
        "session_id",
        "source_token",
        "subscriber_token",
        "token",
    }
    if unsafe_keys.intersection(query):
        raise RelayError(
            "relay invitation URL exposes a credential or Session identifier",
            "relay.unsafe_invitation",
        )
    if query.get("join") != [join_code]:
        raise RelayError(
            "relay invitation URL does not contain its opaque join code",
            "relay.response_identity",
        )
    if parsed.fragment or expected_session_id in invitation_url:
        raise RelayError(
            "relay invitation URL exposes the Session identifier",
            "relay.unsafe_invitation",
        )
    return ReceiverInvitation(session_id, join_code, invitation_url)


def _required_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise RelayError(
            f"relay response field {key!r} must be a non-empty string",
            "relay.response_decode",
        )
    return value


__all__ = [
    "PublisherActivation",
    "ReceiverActivation",
    "ReceiverInvitation",
    "RelayError",
    "RelayPublisher",
    "RelayRoute",
    "RelaySession",
    "RelayTimeoutError",
]
