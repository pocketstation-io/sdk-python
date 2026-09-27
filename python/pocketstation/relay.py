"""Create RelaySessions and compose their publication declarations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from time import monotonic, sleep
from types import TracebackType
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

from ._native import RelayPublisher as _NativeRelayPublisher
from .control import (
    ControlClient,
    ControlPlaneError,
    IceServer,
    InvitationAlias,
    InvitationLink,
    InvitationVisibility,
    SecretToken,
    SessionCredentials,
    SessionId,
    SessionSnapshot,
)
from .control import (
    Invitation as ControlInvitation,
)
from .errors import PocketStationError, _native_call
from .identity import RouteId

if TYPE_CHECKING:
    from .session import Session


class RelayError(PocketStationError, ValueError):
    """A relay declaration, HTTP, activation, or lifecycle failure."""


class RelayTimeoutError(RelayError):
    """An authoritative publisher or receiver activation deadline expired."""


@dataclass(frozen=True, slots=True)
class RelayRoute:
    """One native Session route publishing a named AudioBus."""

    bus_id: str
    route_id: RouteId


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
    """Readable, exact-bus receiver invitation containing no access token."""

    session_id: SessionId
    join_code: SecretToken
    share_alias: InvitationAlias
    visibility: InvitationVisibility
    expires_at: datetime
    join_link: InvitationLink | None
    share_link: InvitationLink | None

    @property
    def word_count(self) -> int:
        """Number of words selected by the Relay service."""
        return len(self.share_alias.split("-"))

    @property
    def join_url(self) -> InvitationLink | None:
        return self.join_link

    @property
    def share_url(self) -> InvitationLink | None:
        return self.share_link

    def expose_url(self) -> str:
        """Explicitly expose the preferred readable URL for sharing."""

        link = self.share_link or self.join_link
        if link is None:
            raise RelayError(
                "control plane did not provide a receiver URL",
                "relay.invitation_url_missing",
            )
        return link.expose_url()


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
    the Rust Session and shared ``pocketstation-relay`` crate.
    """

    def __init__(
        self,
        *,
        relay_url: str,
        credentials: SessionCredentials,
        control: ControlClient,
        owns_control: bool,
        request_timeout_seconds: float,
        ice_servers: tuple[tuple[str, ...], ...],
    ) -> None:
        self.relay_url = _normalize_relay_url(relay_url)
        self.credentials = credentials
        self._control = control
        self._owns_control = owns_control
        self._request_timeout_seconds = request_timeout_seconds
        self._ice_servers = ice_servers
        self._publisher_activation: PublisherActivation | None = None
        self._invitation: ReceiverInvitation | None = None
        self._receiver_activation: ReceiverActivation | None = None
        self._closed = False

    @classmethod
    def create(
        cls,
        *,
        control_plane_url: str,
        relay_url: str | None = None,
        request_timeout_seconds: float = 10.0,
        required_buses: tuple[str, ...] = ("application", "microphone"),
        control_client: ControlClient | None = None,
    ) -> RelaySession:
        request_timeout_seconds = _validate_request_timeout(request_timeout_seconds)
        requested_relay_url = (
            None if relay_url is None else _normalize_relay_url(relay_url)
        )
        owns_control = control_client is None
        control = control_client or ControlClient(
            control_plane_url,
            timeout_seconds=request_timeout_seconds,
        )
        credentials: SessionCredentials | None = None
        try:
            credentials = control.create_session(
                required_buses=required_buses,
                timeout_seconds=request_timeout_seconds,
            )
            normalized_relay_url = _resolve_relay_url(
                credentials,
                requested_relay_url,
            )
            ice_servers = _relay_publisher_ice_servers(credentials.ice_servers)
        except Exception as error:
            if credentials is not None:
                try:
                    control.delete_session(
                        credentials.session_id,
                        credentials.source_token,
                        timeout_seconds=request_timeout_seconds,
                    )
                except Exception as cleanup_error:
                    if owns_control:
                        control.close()
                    raise RelayError(
                        "relay Session validation failed and remote cleanup "
                        "also failed",
                        "relay.cleanup_failed",
                    ) from ExceptionGroup(
                        "relay creation and cleanup failures",
                        [error, cleanup_error],
                    )
            if owns_control:
                control.close()
            raise
        return cls(
            relay_url=normalized_relay_url,
            credentials=credentials,
            control=control,
            owns_control=owns_control,
            request_timeout_seconds=request_timeout_seconds,
            ice_servers=ice_servers,
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
                [list(urls) for urls in self._ice_servers],
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
            lambda value: value.ready,
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
            timeout_code="relay.publisher_timeout",
            timeout_message="relay publisher did not become active before the deadline",
        )
        activation = PublisherActivation(snapshot)
        self._publisher_activation = activation
        return activation

    def create_receiver_invitation(
        self,
        *,
        bus_id: str = "mix",
        visibility: InvitationVisibility | str | None = None,
        word_count: int | None = None,
    ) -> ReceiverInvitation:
        """Create a scoped invitation after every required bus is attached."""
        self._require_open()
        if self._publisher_activation is None:
            raise RelayError(
                "wait_for_publisher() must succeed before creating an invitation",
                "relay.publisher_not_active",
            )
        created = self._control.create_invitation(
            self.session_id,
            self.credentials.source_token,
            bus_id=bus_id,
            visibility=visibility,
            word_count=word_count,
            timeout_seconds=self._request_timeout_seconds,
        )
        invitation = _receiver_invitation(created, self.session_id)
        self._invitation = invitation
        return invitation

    def wait_for_publisher_and_invitation(
        self,
        *,
        bus_id: str = "mix",
        visibility: InvitationVisibility | str | None = None,
        word_count: int | None = None,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverInvitation:
        self.wait_for_publisher(
            timeout_seconds=timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )
        return self.create_receiver_invitation(
            bus_id=bus_id,
            visibility=visibility,
            word_count=word_count,
        )

    def wait_for_receiver(
        self,
        *,
        minimum_receivers: int = 1,
        timeout_seconds: float = 30.0,
        poll_interval_seconds: float = 0.1,
    ) -> ReceiverActivation:
        """Wait for relay-confirmed WebRTC connection and downlink install."""
        self._require_open()
        minimum_receivers = _validate_minimum_receivers(minimum_receivers)
        if self._invitation is None:
            raise RelayError(
                "create_receiver_invitation() must succeed before waiting "
                "for a receiver",
                "relay.invitation_missing",
            )
        snapshot = self._wait_for_snapshot(
            lambda value: value.ready and value.subscription_count >= minimum_receivers,
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
            try:
                snapshot = self._control.session(
                    self.session_id,
                    self.credentials.source_token,
                    timeout_seconds=request_timeout,
                )
            except ControlPlaneError as error:
                if error.code != "control.request":
                    raise
                sleep(min(poll_interval_seconds, max(0.0, deadline - monotonic())))
                continue
            if predicate(snapshot):
                return snapshot
            sleep(min(poll_interval_seconds, max(0.0, deadline - monotonic())))

    def _require_open(self) -> None:
        if self._closed:
            raise RelayError("RelaySession has closed", "relay.closed")


def _normalize_relay_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RelayError(
            "relay_url must be an absolute http or https origin",
            "relay.invalid_url",
        )
    if parsed.username is not None or parsed.password is not None:
        raise RelayError(
            "relay_url must not contain credentials",
            "relay.invalid_url",
        )
    if parsed.path not in {"", "/"}:
        raise RelayError("relay_url must not include a path", "relay.invalid_url")
    if parsed.params or parsed.query or parsed.fragment:
        raise RelayError(
            "relay_url must not include parameters, a query, or a fragment",
            "relay.invalid_url",
        )
    return _parsed_origin(
        parsed,
        code="relay.invalid_url",
        message="relay_url must contain a valid host and port",
    )


def _relay_publisher_ice_servers(
    ice_servers: tuple[IceServer, ...],
) -> tuple[tuple[str, ...], ...]:
    supported: list[tuple[str, ...]] = []
    for server in ice_servers:
        if (
            server.username is not None
            or server.credential is not None
            or any(not url.startswith("stun:") for url in server.urls)
        ):
            raise RelayError(
                "the native Relay publisher accepts unauthenticated STUN servers; "
                "the control plane returned an unsupported ICE server",
                "relay.unsupported_ice_server",
            )
        supported.append(server.urls)
    return tuple(supported)


def _resolve_relay_url(
    credentials: SessionCredentials,
    requested_relay_url: str | None,
) -> str:
    if credentials.whip_url is None:
        if requested_relay_url is not None:
            return requested_relay_url
        raise RelayError(
            "control-plane Session credentials omitted the WHIP endpoint",
            "relay.missing_relay_url",
        )
    authoritative = _media_endpoint_origin(
        credentials.whip_url,
        credentials.session_id,
        "whip",
    )
    if credentials.whep_url is not None:
        receiver_origin = _media_endpoint_origin(
            credentials.whep_url,
            credentials.session_id,
            "whep",
        )
        if receiver_origin != authoritative:
            raise RelayError(
                "control-plane WHIP and WHEP endpoints use different Relay origins",
                "relay.response_identity",
            )
    if requested_relay_url is not None and requested_relay_url != authoritative:
        raise RelayError(
            "configured Relay origin does not match the control-plane Session endpoint",
            "relay.response_identity",
        )
    return authoritative


def _media_endpoint_origin(
    value: str,
    session_id: SessionId,
    endpoint: str,
) -> str:
    parsed = urlparse(value)
    expected_path = f"/v1/sessions/{session_id}/{endpoint}"
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != expected_path
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise RelayError(
            f"control-plane {endpoint.upper()} endpoint does not match its Session",
            "relay.response_identity",
        )
    return _parsed_origin(
        parsed,
        code="relay.response_identity",
        message=f"control-plane {endpoint.upper()} endpoint has an invalid origin",
    )


def _parsed_origin(parsed: ParseResult, *, code: str, message: str) -> str:
    try:
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise RelayError(message, code) from error
    if hostname is None:
        raise RelayError(message, code)
    try:
        hostname = hostname.encode("idna").decode("ascii").lower()
    except UnicodeError as error:
        raise RelayError(message, code) from error
    if ":" in hostname:
        hostname = f"[{hostname}]"
    default_port = 80 if parsed.scheme == "http" else 443
    port_suffix = "" if port in {None, default_port} else f":{port}"
    return f"{parsed.scheme}://{hostname}{port_suffix}"


def _validate_request_timeout(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("request_timeout_seconds must be a number")
    if not 0 < value <= 300:
        raise ValueError(
            "request_timeout_seconds must be greater than 0 and at most 300"
        )
    return float(value)


def _validate_wait(timeout_seconds: float, poll_interval_seconds: float) -> None:
    for name, value in (
        ("timeout_seconds", timeout_seconds),
        ("poll_interval_seconds", poll_interval_seconds),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not isfinite(value) or not 0 < value <= 300:
            raise ValueError(f"{name} must be greater than 0 and at most 300")


def _validate_minimum_receivers(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("minimum_receivers must be an integer")
    if not 1 <= value <= 1_024:
        raise ValueError("minimum_receivers must be between 1 and 1024")
    return value


def _bounded_request_timeout(
    remaining_seconds: float,
    configured_seconds: float,
) -> float:
    return min(remaining_seconds, configured_seconds)


def _receiver_invitation(
    created: ControlInvitation,
    expected_session_id: SessionId,
) -> ReceiverInvitation:
    if created.session_id != expected_session_id:
        raise RelayError(
            "control-plane invitation belongs to a different Session",
            "relay.response_identity",
        )
    for link, expected_path in (
        (created.join_url, "/join"),
        (created.share_url, f"/{created.share_alias}"),
    ):
        if link is None:
            continue
        exposed = link.expose_url()
        parsed = urlparse(exposed)
        if parsed.path != expected_path or parsed.query:
            raise RelayError(
                "relay invitation URL does not match its invitation locator",
                "relay.response_identity",
            )
        if expected_session_id in exposed:
            raise RelayError(
                "relay invitation URL exposes the Session identifier",
                "relay.unsafe_invitation",
            )
    return ReceiverInvitation(
        session_id=created.session_id,
        join_code=created.join_code,
        share_alias=created.share_alias,
        visibility=created.visibility,
        expires_at=created.expires_at,
        join_link=created.join_url,
        share_link=created.share_url,
    )


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
