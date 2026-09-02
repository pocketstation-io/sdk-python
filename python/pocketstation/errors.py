"""Stable exception hierarchy for the PocketStation Python SDK."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

_Result = TypeVar("_Result")
_CODED_ERROR = re.compile(r"\[([a-z0-9_.-]+)\]\s*(.*)", re.DOTALL)


class PocketStationError(Exception):
    """Base SDK failure with a stable machine-readable error code."""

    def __init__(self, message: str, code: str = "error") -> None:
        super().__init__(message)
        self.code = code


class SessionError(PocketStationError):
    """Base failure from Session declaration, startup, or runtime ownership."""


class SessionDeclarationError(SessionError, ValueError):
    """The Session draft, selector, route, or declaration is invalid."""


@dataclass(frozen=True, slots=True)
class SessionCompileDiagnostic:
    """Machine-readable location and validation details for a compile failure."""

    code: str
    node_index: int | None = None
    edge_index: int | None = None
    operator_id: str | None = None
    operator_instance_id: int | None = None
    node_type_id: str | None = None
    source_type_id: str | None = None
    port_name: str | None = None
    direction: str | None = None
    expected: str | None = None
    actual: str | None = None


class SessionStartError(SessionError):
    """Transactional Session startup failed before delivery became active."""

    def __init__(
        self,
        message: str,
        code: str = "error",
        *,
        diagnostic: SessionCompileDiagnostic | None = None,
    ) -> None:
        super().__init__(message, code)
        self.diagnostic = diagnostic


class SessionRuntimeError(SessionError):
    """The running Session or its native owner became unavailable."""


class CaptureError(SessionStartError):
    """Capture authorization, availability, or backend startup failed."""


class GraphError(PocketStationError, ValueError):
    """A graph, signal, port, edge, or media declaration is invalid."""


class SourceError(PocketStationError):
    """An externally authored Source failed validation or lifecycle work."""


class OperatorError(PocketStationError):
    """An externally authored Operator failed validation or lifecycle work."""


class ConnectorRuntimeError(PocketStationError):
    """Connector registration, declaration, or runtime ownership failed."""


class StreamError(PocketStationError):
    """Base failure for managed consumption of one native endpoint."""


class StreamModeError(StreamError):
    """Raised when one stream is consumed through incompatible reader modes."""

    def __init__(self, active_mode: str, requested_mode: str) -> None:
        super().__init__(
            f"stream already uses {active_mode!r}; cannot switch to {requested_mode!r}",
            "stream.mode_conflict",
        )
        self.active_mode = active_mode
        self.requested_mode = requested_mode


class StreamInUseError(StreamError):
    """Raised instead of waiting when another reader owns the stream."""

    def __init__(self, mode: str) -> None:
        super().__init__(
            f"stream already has an active {mode!r} reader",
            "stream.in_use",
        )
        self.mode = mode


class SidecarError(PocketStationError):
    """Base failure from one Session-owned process sidecar."""


class SidecarBackpressureError(SidecarError):
    """The configured finite sidecar data or control queue is full."""


class SidecarProtocolError(SidecarError):
    """The child violated the frozen PKSS wire protocol or handshake."""


class SidecarTimeoutError(SidecarError):
    """A ready, processing, close, cancel, or reap deadline expired."""


class ExtensionError(PocketStationError):
    """A compiled extension descriptor or ABI requirement was rejected."""


class AudioInputError(PocketStationError):
    """Base failure from one bounded application-owned PCM input."""


class AudioInputFullError(AudioInputError):
    """No preallocated frame or queue slot is currently available."""


class AudioInputClosedError(AudioInputError):
    """The input was closed or its Session has stopped."""


class AudioInputCancelledError(AudioInputError):
    """The owning Session cancelled this input."""


class AudioInputBufferError(AudioInputError, ValueError):
    """The supplied object is not one exact contiguous float32 frame."""


class EventInputError(PocketStationError):
    """Base error for bounded typed-event ingress."""


class EventInputFullError(EventInputError, BufferError):
    """The bounded event input has no free capacity."""


class EventInputClosedError(EventInputError):
    """The event input no longer accepts writes."""


def _native_call(operation: Callable[[], _Result]) -> _Result:
    """Execute one synchronous native call through the shared error policy."""
    try:
        return operation()
    except (RuntimeError, ValueError) as error:
        raise _normalize_native_error(error) from error


def _normalize_native_error(error: Exception) -> PocketStationError:
    message = str(error)
    match = _CODED_ERROR.search(message)
    if match is None:
        return PocketStationError(message, "session.internal")
    code = match.group(1)
    detail = match.group(2) or code
    if code in {"sidecar.queue_full", "sidecar.control_queue_full"}:
        return SidecarBackpressureError(detail, code)
    if code in {
        "sidecar.protocol",
        "sidecar.unexpected_eof",
        "sidecar.unexpected_message",
        "sidecar.invalid_message_kind",
    }:
        return SidecarProtocolError(detail, code)
    if code in {"sidecar.timeout", "sidecar.processing_timeout"}:
        return SidecarTimeoutError(detail, code)
    if code.startswith("sidecar."):
        return SidecarError(detail, code)
    if code.startswith("extension."):
        return ExtensionError(detail, code)
    if code == "audio_input.full":
        return AudioInputFullError(detail, code)
    if code == "audio_input.closed":
        return AudioInputClosedError(detail, code)
    if code == "audio_input.cancelled":
        return AudioInputCancelledError(detail, code)
    if code in {
        "audio_input.invalid_buffer",
        "audio_input.invalid_configuration",
        "audio_input.declaration_failed",
    }:
        return AudioInputBufferError(detail, code)
    if code.startswith("audio_input."):
        return AudioInputError(detail, code)
    if code.startswith("capture."):
        return CaptureError(detail, code)
    if code.startswith("graph."):
        return GraphError(detail, code)
    if code.startswith("source."):
        return SourceError(detail, code)
    if code.startswith("operator."):
        return OperatorError(detail, code)
    if code.startswith("connector."):
        return ConnectorRuntimeError(detail, code)
    if code.startswith("session.start_") or code in {
        "session.host_setup_failed",
        "session.unsupported_platform",
        "session.declaration_invalid",
        "session.compile_failed",
        "session.runtime_prepare_failed",
        "session.invalid_start_options",
        "session.unsupported_source_topology",
        "session.missing_endpoint_declaration",
        "session.endpoint_prepare_failed",
        "session.endpoint_start_failed",
        "session.runtime_start_failed",
        "session.missing_audio_receipt",
        "session.missing_recording_configuration",
        "session.missing_event_receiver",
        "session.trace_recorder_setup_failed",
    }:
        return SessionStartError(
            detail,
            code,
            diagnostic=_native_compile_diagnostic(error),
        )
    if code.startswith("session."):
        declaration_codes = {
            "session.no_sources",
            "session.no_routes",
            "session.no_source_outputs",
            "session.invalid_selector",
            "session.invalid_frame_duration",
            "session.invalid_endpoint",
            "session.invalid_operator",
            "session.invalid_route",
            "session.foreign_endpoint",
            "session.draft_frozen",
            "session.id_exhausted",
            "session.unsupported_version",
            "session.unknown_endpoint",
            "session.unknown_stem",
            "session.unknown_source",
            "session.unknown_operator_instance",
            "session.operator_has_no_destination",
        }
        if code in declaration_codes:
            return SessionDeclarationError(detail, code)
        return SessionRuntimeError(detail, code)
    return PocketStationError(detail, code)


def _native_optional_string(error: Exception, name: str) -> str | None:
    value = getattr(error, name, None)
    return value if isinstance(value, str) else None


def _native_optional_integer(error: Exception, name: str) -> int | None:
    value = getattr(error, name, None)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _native_compile_diagnostic(
    error: Exception,
) -> SessionCompileDiagnostic | None:
    code = _native_optional_string(error, "_pocketstation_compile_code")
    if code is None:
        return None
    return SessionCompileDiagnostic(
        code=code,
        node_index=_native_optional_integer(error, "_pocketstation_compile_node_index"),
        edge_index=_native_optional_integer(error, "_pocketstation_compile_edge_index"),
        operator_id=_native_optional_string(
            error, "_pocketstation_compile_operator_id"
        ),
        operator_instance_id=_native_optional_integer(
            error, "_pocketstation_compile_operator_instance_id"
        ),
        node_type_id=_native_optional_string(
            error, "_pocketstation_compile_node_type_id"
        ),
        source_type_id=_native_optional_string(
            error, "_pocketstation_compile_source_type_id"
        ),
        port_name=_native_optional_string(error, "_pocketstation_compile_port_name"),
        direction=_native_optional_string(error, "_pocketstation_compile_direction"),
        expected=_native_optional_string(error, "_pocketstation_compile_expected"),
        actual=_native_optional_string(error, "_pocketstation_compile_actual"),
    )


__all__ = [
    "AudioInputBufferError",
    "AudioInputCancelledError",
    "AudioInputClosedError",
    "AudioInputError",
    "AudioInputFullError",
    "CaptureError",
    "ConnectorRuntimeError",
    "EventInputClosedError",
    "EventInputError",
    "EventInputFullError",
    "ExtensionError",
    "GraphError",
    "OperatorError",
    "PocketStationError",
    "SessionCompileDiagnostic",
    "SessionDeclarationError",
    "SessionError",
    "SessionRuntimeError",
    "SessionStartError",
    "SidecarBackpressureError",
    "SidecarError",
    "SidecarProtocolError",
    "SidecarTimeoutError",
    "SourceError",
    "StreamError",
    "StreamInUseError",
    "StreamModeError",
]
