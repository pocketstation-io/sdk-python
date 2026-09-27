"""Typed synchronous client for the PocketStation control-plane Session API."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from types import TracebackType
from typing import Any, TypeVar, cast
from urllib.parse import parse_qs, quote, urljoin, urlparse

import httpx

from .errors import PocketStationError

_MAX_ERROR_BODY_BYTES = 4_096
_MAX_JSON_BODY_BYTES = 65_536
_MAX_SESSION_ID_BYTES = 128
_MAX_SECRET_BYTES = 4_096
_MAX_ICE_SERVERS = 32
_MAX_ICE_URLS = 16


class ControlPlaneError(PocketStationError):
    """A configuration, transport, HTTP, or decoding control-plane failure."""

    def __init__(
        self,
        message: str,
        code: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message, code)
        self.status_code = status_code


class InvitationUnavailableError(ControlPlaneError):
    """An invitation is invalid, expired, revoked, or already redeemed."""

    def __init__(self) -> None:
        super().__init__(
            "invitation is unavailable",
            "control.invitation_unavailable",
            status_code=404,
        )


class SessionId(str):
    """Validated Session identifier safe for one URL path segment."""

    def __new__(cls, value: str) -> SessionId:
        if (
            not value
            or len(value.encode("utf-8")) > _MAX_SESSION_ID_BYTES
            or not all(
                character.isascii() and (character.isalnum() or character in "-_")
                for character in value
            )
        ):
            raise ValueError(
                "Session ID must contain only ASCII letters, digits, '-' or '_'"
            )
        return str.__new__(cls, value)


class SecretToken:
    """Credential that redacts itself unless exposure is explicitly requested."""

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not value:
            raise ValueError("credential token must not be empty")
        if len(value.encode("utf-8")) > _MAX_SECRET_BYTES:
            raise ValueError(
                f"credential token must not exceed {_MAX_SECRET_BYTES} bytes"
            )
        self._value = value

    def expose_secret(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "SecretToken('[redacted]')"

    def __str__(self) -> str:
        return "[redacted]"


class InvitationVisibility(StrEnum):
    """Deprecated legacy formatting selector, never authorization."""

    PUBLIC = "public"
    PRIVATE = "private"


class InvitationAlias(str):
    """Validated readable invitation locator with 2 to 15 words."""

    def __new__(cls, value: str) -> InvitationAlias:
        words = value.split("-")
        if (
            not 7 <= len(value) <= 134
            or not 2 <= len(words) <= 15
            or any(
                not 3 <= len(word) <= 24
                or not all("a" <= character <= "z" for character in word)
                for word in words
            )
        ):
            raise ValueError(
                "invitation alias must contain 2 to 15 lowercase ASCII "
                "words of 3 to 24 letters separated by '-'"
            )
        return str.__new__(cls, value)


class InvitationLocator(str):
    """Validated opaque join code or readable invitation alias."""

    def __new__(cls, value: str) -> InvitationLocator:
        if _is_opaque_invitation_code(value):
            return str.__new__(cls, value)
        try:
            InvitationAlias(value)
        except ValueError as error:
            raise ValueError(
                "invitation locator must be an opaque join code or readable alias"
            ) from error
        return str.__new__(cls, value)


class InvitationLink:
    """Receiver URL carrying the original delegated join code; always redacted."""

    __slots__ = ("_url", "visibility")

    def __init__(self, url: str, visibility: InvitationVisibility) -> None:
        parsed = urlparse(url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
        ):
            raise ValueError("invitation URL must be an absolute HTTP or HTTPS URL")
        if _fragment_join_code(parsed.fragment) is None:
            raise ValueError(
                "invitation URL must contain its delegated join credential"
            )
        self._url = url
        self.visibility = visibility

    @property
    def is_private(self) -> bool:
        """Deprecated sensitivity alias: every link contains private authority."""
        return True

    def expose_url(self) -> str:
        """Explicitly reveal the complete URL and delegated join credential."""
        return self._url

    def expose_join_code(self) -> SecretToken:
        """Return the original opaque delegated join credential."""
        value = _fragment_join_code(urlparse(self._url).fragment)
        if value is None:
            raise ValueError("invitation URL has no join credential")
        return SecretToken(value)

    def expose_secret(self) -> SecretToken:
        """Deprecated alias of expose_join_code; no separate secret exists."""
        return self.expose_join_code()

    def __str__(self) -> str:
        return "[redacted]"

    def __repr__(self) -> str:
        return f"InvitationLink('[redacted]', visibility={self.visibility.value!r})"


@dataclass(frozen=True, slots=True)
class IceServer:
    urls: tuple[str, ...]
    username: str | None = None
    credential: SecretToken | None = None


@dataclass(frozen=True, slots=True)
class SessionCredentials:
    session_id: SessionId
    required_buses: tuple[str, ...]
    source_token: SecretToken
    whip_url: str | None = None
    whep_url: str | None = None
    ice_servers: tuple[IceServer, ...] = ()


@dataclass(frozen=True, slots=True)
class SessionRenewal:
    """Replacement owner capability and its server-declared expiry."""

    source_token: SecretToken
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class BusState:
    bus_id: str
    role: str
    source_active: bool
    source_generation: int


@dataclass(frozen=True, slots=True)
class SubscriptionState:
    subscriber_id: str
    bus_id: str


@dataclass(frozen=True, slots=True)
class SessionSnapshot:
    session_id: SessionId
    state_revision: int
    relay_epoch: str | None
    relay_revision: int
    required_buses: tuple[str, ...]
    buses: tuple[BusState, ...]
    subscriptions: tuple[SubscriptionState, ...]
    ready: bool
    subscription_count: int
    codec: str


@dataclass(frozen=True, slots=True)
class Invitation:
    session_id: SessionId
    join_code: SecretToken
    share_alias: InvitationAlias
    visibility: InvitationVisibility
    expires_at: datetime
    join_url: InvitationLink | None
    share_url: InvitationLink | None

    @property
    def word_count(self) -> int:
        """Number of words in the validated readable name."""
        return len(self.share_alias.split("-"))


@dataclass(frozen=True, slots=True)
class InvitationMetadata:
    """Non-consuming invitation metadata containing no receiver capability."""

    share_alias: InvitationAlias
    visibility: InvitationVisibility
    expires_at: datetime

    @property
    def word_count(self) -> int:
        """Number of words in the validated readable name."""
        return len(self.share_alias.split("-"))


@dataclass(frozen=True, slots=True)
class ReceiverAccess:
    """Single-use subscriber capability scoped to one exact AudioBus."""

    session_id: SessionId
    bus_id: str
    subscriber_token: SecretToken
    signal_url: str
    whep_url: str | None
    ice_servers: tuple[IceServer, ...]


@dataclass(frozen=True, slots=True)
class SubscriberCredentials:
    session_id: SessionId
    bus_id: str
    subscriber_token: SecretToken


@dataclass(frozen=True, slots=True)
class PublisherCredentials:
    """Media-only publisher capability scoped to one AudioBus."""

    session_id: SessionId
    bus_id: str
    publisher_token: SecretToken
    signal_url: str
    ice_servers: tuple[IceServer, ...]


class ControlClient:
    """Reusable, bounded HTTP client for Session lifecycle operations."""

    def __init__(
        self,
        control_plane_url: str,
        *,
        timeout_seconds: float = 10.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.control_plane_url = _normalize_base_url(control_plane_url)
        self._timeout_seconds = _validate_timeout(timeout_seconds)
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(timeout=timeout_seconds)
        self._closed = False

    def create_session(
        self,
        *,
        required_buses: tuple[str, ...] = ("application", "microphone"),
        timeout_seconds: float | None = None,
    ) -> SessionCredentials:
        required_buses = _bus_ids(required_buses, "required_buses")
        payload = self._json_request(
            "POST",
            "v1/sessions",
            expected_status=201,
            timeout_seconds=timeout_seconds,
            json_body={"required_buses": list(required_buses)},
        )
        return _decode_response(_session_credentials, payload)

    def renew_session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionRenewal:
        """Renew Session lifetime and replace its owner capability."""
        identifier = SessionId(str(session_id))
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/renew",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
        )
        return _decode_response(_session_renewal, payload)

    def session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> SessionSnapshot:
        identifier = SessionId(str(session_id))
        payload = self._json_request(
            "GET",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
        )
        return _decode_response(_session_snapshot, payload)

    def issue_subscriber_credentials(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str = "mix",
        timeout_seconds: float | None = None,
    ) -> SubscriberCredentials:
        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/subscribe",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body={"bus_id": bus_id},
        )
        return _decode_response(_subscriber_credentials, payload)

    def issue_publisher_credentials(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str,
        timeout_seconds: float | None = None,
    ) -> PublisherCredentials:
        """Issue a media-only capability for one exact AudioBus."""

        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/publish",
            expected_status=200,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body={"bus_id": bus_id},
        )
        return _decode_response(_publisher_credentials, payload)

    def create_invitation(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        bus_id: str = "mix",
        visibility: InvitationVisibility | str | None = None,
        word_count: int | None = None,
        timeout_seconds: float | None = None,
    ) -> Invitation:
        identifier = SessionId(str(session_id))
        bus_id = _bus_id(bus_id, "bus_id")
        body = _invitation_request(bus_id, visibility, word_count)
        payload = self._json_request(
            "POST",
            f"v1/sessions/{quote(identifier, safe='')}/invitations",
            expected_status=201,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            json_body=body,
        )
        return _decode_response(_invitation, payload, identifier, body)

    def inspect_invitation(
        self,
        locator: str | InvitationLocator | SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> InvitationMetadata:
        """Inspect an invitation without consuming its single-use access."""

        identifier = _invitation_locator(locator)
        if _is_opaque_invitation_code(identifier):
            raise ValueError("Inspection requires a readable navigation alias")
        try:
            payload = self._json_request(
                "GET",
                f"v1/invitations/{quote(identifier, safe='')}",
                expected_status=200,
                timeout_seconds=timeout_seconds,
            )
        except ControlPlaneError as error:
            if error.status_code == 404:
                raise InvitationUnavailableError() from None
            raise
        return _decode_response(_invitation_metadata, payload)

    def redeem_invitation(
        self,
        locator: str | InvitationLocator | SecretToken,
        *,
        join_code: SecretToken | None = None,
        secret: SecretToken | None = None,
        timeout_seconds: float | None = None,
    ) -> ReceiverAccess:
        """Redeem with the original opaque credential, never readable words alone.

        ``secret`` is a deprecated alias of ``join_code``, not a second factor.
        """

        identifier = _invitation_locator(locator)
        credential = _redemption_join_code(join_code, secret)
        if not _is_opaque_invitation_code(identifier) and credential is None:
            raise InvitationUnavailableError()
        if _is_opaque_invitation_code(identifier) and credential not in {
            None,
            identifier,
        }:
            raise InvitationUnavailableError()
        opaque_locator = _is_opaque_invitation_code(identifier)
        credential = identifier if opaque_locator else credential
        json_body = {"join_code": credential}
        try:
            payload = self._json_request(
                "POST",
                "v1/join"
                if opaque_locator
                else f"v1/join/{quote(identifier, safe='')}",
                expected_status=200,
                timeout_seconds=timeout_seconds,
                json_body=json_body,
                redacted_values=(identifier,)
                if credential is None
                else (identifier, credential),
            )
        except ControlPlaneError as error:
            if error.status_code == 404:
                raise InvitationUnavailableError() from None
            raise
        return _decode_response(_receiver_access, payload)

    def delete_session(
        self,
        session_id: str | SessionId,
        source_token: SecretToken,
        *,
        timeout_seconds: float | None = None,
    ) -> None:
        identifier = SessionId(str(session_id))
        self._request(
            "DELETE",
            f"v1/sessions/{quote(identifier, safe='')}",
            expected_status=204,
            timeout_seconds=timeout_seconds,
            authorization=source_token,
            expect_json=False,
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self) -> ControlClient:
        if self._closed:
            raise RuntimeError("ControlClient has closed")
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def _json_request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        timeout_seconds: float | None,
        authorization: SecretToken | None = None,
        json_body: dict[str, Any] | None = None,
        redacted_values: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        return self._request(
            method,
            path,
            expected_status=expected_status,
            timeout_seconds=timeout_seconds,
            authorization=authorization,
            expect_json=True,
            json_body=json_body,
            redacted_values=redacted_values,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        expected_status: int,
        timeout_seconds: float | None,
        authorization: SecretToken | None,
        expect_json: bool,
        json_body: dict[str, Any] | None = None,
        redacted_values: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        if self._closed:
            raise RuntimeError("ControlClient has closed")
        headers = {}
        if authorization is not None:
            exposed = authorization.expose_secret()
            headers["Authorization"] = f"Bearer {exposed}"
            redacted_values = (*redacted_values, exposed)
        timeout = _resolve_timeout(self._timeout_seconds, timeout_seconds)
        transport_failure: ControlPlaneError | None = None
        try:
            with self._http_client.stream(
                method,
                urljoin(self.control_plane_url, path),
                headers=headers,
                json=json_body,
                timeout=timeout,
                follow_redirects=False,
            ) as response:
                if response.status_code != expected_status:
                    body = _read_bounded(response.iter_bytes(), _MAX_ERROR_BODY_BYTES)
                    raise ControlPlaneError(
                        f"control-plane returned HTTP {response.status_code}",
                        "control.http_status",
                        status_code=response.status_code,
                    )
                if not expect_json:
                    return {}
                body = _read_bounded(response.iter_bytes(), _MAX_JSON_BODY_BYTES)
        except ControlPlaneError:
            raise
        except httpx.HTTPError:
            transport_failure = ControlPlaneError(
                "control-plane request failed",
                "control.request",
            )
        if transport_failure is not None:
            raise transport_failure
        decode_failed = False
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            decode_failed = True
        if decode_failed:
            raise ControlPlaneError(
                "control-plane response could not be decoded",
                "control.response_decode",
            )
        if not isinstance(payload, dict):
            raise ControlPlaneError(
                "control-plane response must be a JSON object",
                "control.response_decode",
            )
        return payload


def _normalize_base_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("control_plane_url must be an absolute http or https URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("control_plane_url must not contain credentials")
    return value.split("?", 1)[0].split("#", 1)[0].rstrip("/") + "/"


_Decoded = TypeVar("_Decoded")


def _decode_response(decoder: Callable[..., _Decoded], *arguments: Any) -> _Decoded:
    """Detach untrusted field values and parser exceptions at the API boundary."""
    code = "control.response_decode"
    try:
        return decoder(*arguments)
    except (ValueError, TypeError, ControlPlaneError) as error:
        if isinstance(error, ControlPlaneError):
            code = error.code
    # Raise outside the handler so raw exceptions are not retained as context.
    raise ControlPlaneError("control-plane response fields are invalid", code)


def _validate_timeout(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("timeout_seconds must be a number")
    if not 0 < value <= 300:
        raise ValueError("timeout_seconds must be greater than 0 and at most 300")
    return float(value)


def _resolve_timeout(default: float, override: float | None) -> float:
    """Resolve a per-request override without permitting unbounded I/O."""

    return default if override is None else _validate_timeout(override)


def _read_bounded(chunks: Any, limit_bytes: int) -> bytes:
    body = bytearray()
    for chunk in chunks:
        remaining = limit_bytes + 1 - len(body)
        if remaining <= 0:
            break
        body.extend(chunk[:remaining])
    if len(body) > limit_bytes:
        raise ControlPlaneError(
            f"control-plane response exceeds {limit_bytes} bytes",
            "control.response_too_large",
        )
    return bytes(body)


def _required(payload: dict[str, Any], key: str, expected_type: type[Any]) -> Any:
    value = payload.get(key)
    valid = isinstance(value, expected_type)
    if expected_type is int and isinstance(value, bool):
        valid = False
    if not valid:
        raise ControlPlaneError(
            f"control-plane response field {key!r} has the wrong type",
            "control.response_decode",
        )
    return value


def _ice_servers(payload: dict[str, Any]) -> tuple[IceServer, ...]:
    raw_servers = payload.get("ice_servers", [])
    if not isinstance(raw_servers, list):
        raise ControlPlaneError(
            "control-plane response field 'ice_servers' has the wrong type",
            "control.response_decode",
        )
    if len(raw_servers) > _MAX_ICE_SERVERS:
        raise ControlPlaneError(
            f"control-plane returned more than {_MAX_ICE_SERVERS} ICE servers",
            "control.response_too_large",
        )
    servers: list[IceServer] = []
    for raw_server in raw_servers:
        if not isinstance(raw_server, dict):
            raise ControlPlaneError(
                "control-plane ICE server must be a JSON object",
                "control.response_decode",
            )
        urls = _required(raw_server, "urls", list)
        if not all(isinstance(url, str) for url in urls):
            raise ControlPlaneError(
                "control-plane ICE server URLs must be strings",
                "control.response_decode",
            )
        if len(urls) > _MAX_ICE_URLS:
            raise ControlPlaneError(
                f"ICE server returned more than {_MAX_ICE_URLS} URLs",
                "control.response_too_large",
            )
        username = raw_server.get("username")
        credential = raw_server.get("credential")
        if username is not None and not isinstance(username, str):
            raise ControlPlaneError(
                "ICE username must be a string", "control.response_decode"
            )
        if credential is not None and not isinstance(credential, str):
            raise ControlPlaneError(
                "ICE credential must be a string", "control.response_decode"
            )
        servers.append(
            IceServer(
                tuple(urls),
                username,
                None if credential is None else SecretToken(credential),
            )
        )
    return tuple(servers)


def _session_credentials(payload: dict[str, Any]) -> SessionCredentials:
    return SessionCredentials(
        session_id=SessionId(_required(payload, "session_id", str)),
        required_buses=_decoded_bus_ids(
            tuple(_required(payload, "required_buses", list)),
            "required_buses",
        ),
        source_token=SecretToken(_required(payload, "source_token", str)),
        whip_url=_optional_string(payload, "whip_url"),
        whep_url=_optional_string(payload, "whep_url"),
        ice_servers=_ice_servers(payload),
    )


def _session_renewal(payload: dict[str, Any]) -> SessionRenewal:
    return SessionRenewal(
        source_token=SecretToken(_required(payload, "source_token", str)),
        expires_at=_timestamp(payload, "expires_at"),
    )


def _session_snapshot(payload: dict[str, Any]) -> SessionSnapshot:
    state_revision = _nonnegative_integer(payload, "state_revision", minimum=1)
    relay_revision = _nonnegative_integer(payload, "relay_revision")
    subscription_count = _required(payload, "subscription_count", int)
    if subscription_count < 0:
        raise ControlPlaneError(
            "control-plane subscription_count must not be negative",
            "control.response_decode",
        )
    return SessionSnapshot(
        session_id=SessionId(_required(payload, "session_id", str)),
        state_revision=state_revision,
        relay_epoch=_optional_string(payload, "relay_epoch"),
        relay_revision=relay_revision,
        required_buses=_decoded_bus_ids(
            tuple(_required(payload, "required_buses", list)),
            "required_buses",
        ),
        buses=_bus_states(payload),
        subscriptions=_subscription_states(payload),
        ready=_required(payload, "ready", bool),
        subscription_count=subscription_count,
        codec=_required(payload, "codec", str),
    )


def _subscriber_credentials(payload: dict[str, Any]) -> SubscriberCredentials:
    return SubscriberCredentials(
        session_id=SessionId(_required(payload, "session_id", str)),
        bus_id=_bus_id(_required(payload, "bus_id", str), "bus_id"),
        subscriber_token=SecretToken(_required(payload, "subscriber_token", str)),
    )


def _publisher_credentials(payload: dict[str, Any]) -> PublisherCredentials:
    signal_url = _required(payload, "signal_url", str)
    parsed_signal_url = urlparse(signal_url)
    if parsed_signal_url.scheme not in {"ws", "wss"} or not parsed_signal_url.netloc:
        raise ControlPlaneError(
            "control-plane signal_url must be an absolute ws or wss URL",
            "control.response_decode",
        )
    try:
        return PublisherCredentials(
            session_id=SessionId(_required(payload, "session_id", str)),
            bus_id=_required_identifier(payload, "bus_id", maximum=64),
            publisher_token=SecretToken(_required(payload, "publisher_token", str)),
            signal_url=signal_url,
            ice_servers=_ice_servers(payload),
        )
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _invitation(
    payload: dict[str, Any],
    session_id: SessionId,
    request_body: dict[str, Any] | None = None,
) -> Invitation:
    try:
        visibility = _invitation_visibility(_required(payload, "visibility", str))
        alias = InvitationAlias(_required(payload, "share_alias", str))
        _validate_invitation_word_count(payload, alias, visibility)
        requested = None if request_body is None else request_body.get("word_count")
        if (
            requested is None
            and request_body is not None
            and "visibility" in request_body
        ):
            requested = 2 if request_body["visibility"] == "public" else 3
        if requested is not None and len(alias.split("-")) != requested:
            raise ValueError("invitation response does not match the requested count")
        join_value = _required(payload, "join_code", str)
        if not _is_opaque_invitation_code(join_value):
            raise ValueError("join_code must be an opaque delegated credential")
        join_code = SecretToken(join_value)
        join_url = _optional_invitation_link(payload, "join_url", visibility)
        share_url = _optional_invitation_link(payload, "share_url", visibility)
        _validate_invitation_links(
            join_code,
            alias,
            join_url,
            share_url,
        )
        return Invitation(
            session_id=session_id,
            join_code=join_code,
            share_alias=alias,
            visibility=visibility,
            expires_at=_timestamp(payload, "expires_at"),
            join_url=join_url,
            share_url=share_url,
        )
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _invitation_metadata(payload: dict[str, Any]) -> InvitationMetadata:
    try:
        visibility = _invitation_visibility(_required(payload, "visibility", str))
        alias = InvitationAlias(_required(payload, "share_alias", str))
        _validate_invitation_word_count(payload, alias, visibility)
        return InvitationMetadata(
            share_alias=alias,
            visibility=visibility,
            expires_at=_timestamp(payload, "expires_at"),
        )
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _receiver_access(payload: dict[str, Any]) -> ReceiverAccess:
    signal_url = _required(payload, "signal_url", str)
    parsed_signal_url = urlparse(signal_url)
    if parsed_signal_url.scheme not in {"ws", "wss"} or not parsed_signal_url.netloc:
        raise ControlPlaneError(
            "control-plane signal_url must be an absolute ws or wss URL",
            "control.response_decode",
        )
    try:
        session_id = SessionId(_required(payload, "session_id", str))
        whep_url = _optional_string(payload, "whep_url")
        if whep_url is not None:
            _validate_media_endpoint(whep_url, session_id, "whep")
        return ReceiverAccess(
            session_id=session_id,
            bus_id=_bus_id(_required(payload, "bus_id", str), "bus_id"),
            subscriber_token=SecretToken(_required(payload, "subscriber_token", str)),
            signal_url=signal_url,
            whep_url=whep_url,
            ice_servers=_ice_servers(payload),
        )
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _validate_invitation_word_count(
    payload: dict[str, Any],
    alias: InvitationAlias,
    visibility: InvitationVisibility,
) -> None:
    actual = len(alias.split("-"))
    if "word_count" in payload:
        declared = payload["word_count"]
        if type(declared) is not int or not 2 <= declared <= 15:
            raise ValueError("invalid invitation word count")
    else:
        # Old services described only the original two/three-word formats.
        declared = 2 if visibility is InvitationVisibility.PUBLIC else 3
    if actual != declared:
        raise ValueError("invitation word count does not match its readable name")
    if (visibility is InvitationVisibility.PUBLIC) != (declared == 2):
        raise ValueError("invitation compatibility format does not match its count")


def _invitation_request(
    bus_id: str,
    visibility: InvitationVisibility | str | None,
    word_count: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"bus_id": bus_id}
    if word_count is not None:
        if type(word_count) is not int or not 2 <= word_count <= 15:
            raise ValueError("word_count must be an integer from 2 to 15")
        body["word_count"] = word_count
    if visibility is not None:
        selected = _invitation_visibility(visibility)
        if word_count is not None and word_count != (
            2 if selected is InvitationVisibility.PUBLIC else 3
        ):
            raise ValueError("word_count conflicts with visibility")
        body["visibility"] = selected.value
    return body


def _invitation_visibility(
    value: InvitationVisibility | str,
) -> InvitationVisibility:
    try:
        return InvitationVisibility(value)
    except ValueError as error:
        raise ValueError("visibility must be 'public' or 'private'") from error


def _timestamp(payload: dict[str, Any], key: str) -> datetime:
    value = _required(payload, key, str)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{key} must be an RFC 3339 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{key} must include a UTC offset")
    return parsed.astimezone(UTC)


def _optional_invitation_link(
    payload: dict[str, Any],
    key: str,
    visibility: InvitationVisibility,
) -> InvitationLink | None:
    value = _optional_string(payload, key)
    if not value:
        return None
    return InvitationLink(value, visibility)


def _fragment_join_code(fragment: str) -> str | None:
    if not fragment:
        return None
    try:
        values = parse_qs(fragment, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise ValueError("invalid invitation fragment") from None
    if set(values) != {"join"} or len(values["join"]) != 1:
        raise ValueError("invitation fragment must contain only one join credential")
    value = values["join"][0]
    if not _is_opaque_invitation_code(value):
        raise ValueError("invitation fragment must contain an opaque join credential")
    return value


def _invitation_locator(
    value: str | InvitationLocator | SecretToken,
) -> InvitationLocator:
    return InvitationLocator(
        value.expose_secret() if isinstance(value, SecretToken) else str(value)
    )


def _redemption_join_code(
    join_code: SecretToken | None, secret: SecretToken | None
) -> str | None:
    """The deprecated secret argument aliases the same join code."""
    for token in (join_code, secret):
        if token is not None and not isinstance(token, SecretToken):
            raise TypeError("join_code must be a SecretToken")
    primary = None if join_code is None else join_code.expose_secret()
    compatibility = None if secret is None else secret.expose_secret()
    if primary is not None and compatibility is not None and primary != compatibility:
        raise ValueError("join_code and deprecated secret alias disagree")
    value = primary if primary is not None else compatibility
    if value is not None and not _is_opaque_invitation_code(value):
        raise ValueError("join_code must be an opaque delegated credential")
    return value


def _validate_invitation_links(
    join_code: SecretToken,
    share_alias: InvitationAlias,
    join_url: InvitationLink | None,
    share_url: InvitationLink | None,
) -> None:
    origins = set()
    for link, expected_path in ((join_url, "/join"), (share_url, f"/{share_alias}")):
        if link is None:
            continue
        parsed = urlparse(link.expose_url())
        if parsed.path != expected_path or parsed.params or parsed.query:
            raise ValueError("invitation URL does not match its locator")
        if link.expose_join_code().expose_secret() != join_code.expose_secret():
            raise ValueError(
                "invitation URL does not carry its delegated join credential"
            )
        origins.add((parsed.scheme, parsed.netloc))
    if len(origins) > 1:
        raise ValueError("invitation URLs must use one receiver origin")


def _is_opaque_invitation_code(value: str) -> bool:
    if len(value) != 36:
        return False
    for index, character in enumerate(value):
        if index in {8, 13, 18, 23}:
            if character != "-":
                return False
        elif not ("0" <= character <= "9" or "a" <= character <= "f"):
            return False
    return True


def _validate_media_endpoint(
    value: str,
    session_id: SessionId,
    endpoint: str,
) -> None:
    parsed = urlparse(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path != f"/v1/sessions/{session_id}/{endpoint}"
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            f"control-plane {endpoint.upper()} endpoint does not match its Session"
        )


def _nonnegative_integer(payload: dict[str, Any], key: str, *, minimum: int = 0) -> int:
    value = cast(int, _required(payload, key, int))
    if value < minimum:
        raise ControlPlaneError(
            f"control-plane response field {key!r} must be at least {minimum}",
            "control.response_decode",
        )
    return value


def _identifier(value: str, field: str, maximum: int) -> str:
    if (
        not value
        or len(value) > maximum
        or not all(
            character.isascii() and (character.isalnum() or character in "._-")
            for character in value
        )
    ):
        raise ValueError(
            f"{field} must contain 1 to {maximum} ASCII letters, digits, "
            "'.', '_' or '-'"
        )
    return value


def _bus_id(value: str, field: str) -> str:
    return _identifier(value, field, 64)


def _bus_ids(values: tuple[Any, ...], field: str) -> tuple[str, ...]:
    if not 1 <= len(values) <= 16 or not all(
        isinstance(value, str) for value in values
    ):
        raise ValueError(f"{field} must contain between 1 and 16 bus IDs")
    result = tuple(_bus_id(value, field) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must not contain duplicate bus IDs")
    return result


def _decoded_bus_ids(values: tuple[Any, ...], field: str) -> tuple[str, ...]:
    try:
        return _bus_ids(values, field)
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _required_identifier(payload: dict[str, Any], key: str, *, maximum: int) -> str:
    try:
        return _identifier(_required(payload, key, str), key, maximum)
    except ValueError as error:
        raise ControlPlaneError(str(error), "control.response_decode") from error


def _bus_states(payload: dict[str, Any]) -> tuple[BusState, ...]:
    raw = _required(payload, "buses", list)
    if len(raw) > 16 or not all(isinstance(value, dict) for value in raw):
        raise ControlPlaneError(
            "control-plane buses must contain at most 16 objects",
            "control.response_decode",
        )
    return tuple(
        BusState(
            bus_id=_required_identifier(value, "bus_id", maximum=64),
            role=_required_identifier(value, "role", maximum=64),
            source_active=_required(value, "source_active", bool),
            source_generation=_nonnegative_integer(value, "source_generation"),
        )
        for value in raw
    )


def _subscription_states(payload: dict[str, Any]) -> tuple[SubscriptionState, ...]:
    raw = _required(payload, "subscriptions", list)
    if len(raw) > 1_024 or not all(isinstance(value, dict) for value in raw):
        raise ControlPlaneError(
            "control-plane subscriptions must contain at most 1024 objects",
            "control.response_decode",
        )
    return tuple(
        SubscriptionState(
            subscriber_id=_required_identifier(value, "subscriber_id", maximum=128),
            bus_id=_required_identifier(value, "bus_id", maximum=64),
        )
        for value in raw
    )


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is not None and not isinstance(value, str):
        raise ControlPlaneError(
            f"control-plane response field {key!r} has the wrong type",
            "control.response_decode",
        )
    return value


__all__ = [
    "BusState",
    "ControlClient",
    "ControlPlaneError",
    "IceServer",
    "Invitation",
    "InvitationAlias",
    "InvitationLink",
    "InvitationLocator",
    "InvitationMetadata",
    "InvitationUnavailableError",
    "InvitationVisibility",
    "PublisherCredentials",
    "ReceiverAccess",
    "SecretToken",
    "SessionCredentials",
    "SessionId",
    "SessionRenewal",
    "SessionSnapshot",
    "SubscriberCredentials",
    "SubscriptionState",
]
