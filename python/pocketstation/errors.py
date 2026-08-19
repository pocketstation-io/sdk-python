"""Stable exception hierarchy for the PocketStation Python SDK."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import TypeVar

_Result = TypeVar("_Result")
_CODED_ERROR = re.compile(r"\[([a-z0-9_.-]+)\]\s*(.*)", re.DOTALL)


class PocketStationError(Exception):
    """Base SDK failure with a stable machine-readable error code."""

    def __init__(self, message: str, code: str = "error") -> None:
        super().__init__(message)
        self.code = code


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
    """The child violated the frozen PKSS wire or handshake contract."""


class SidecarTimeoutError(SidecarError):
    """A ready, processing, close, cancel, or reap deadline expired."""


class ExtensionError(PocketStationError):
    """A compiled extension descriptor or ABI contract was rejected."""


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
    return PocketStationError(detail, code)


__all__ = [
    "AudioInputBufferError",
    "AudioInputCancelledError",
    "AudioInputClosedError",
    "AudioInputError",
    "AudioInputFullError",
    "ExtensionError",
    "PocketStationError",
    "SidecarBackpressureError",
    "SidecarError",
    "SidecarProtocolError",
    "SidecarTimeoutError",
    "StreamError",
    "StreamInUseError",
    "StreamModeError",
]
