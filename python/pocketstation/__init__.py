"""PocketStation's concise Python entry point.

Advanced graph, authoring, Relay, extension, and diagnostic APIs live in
their named modules. They are not duplicated at the package root.
"""

from __future__ import annotations

from . import aio as aio
from ._native import AudioFrame
from .audio_input import AudioInput, AudioInputConfig, PcmSource
from .capture import Capture, capture
from .compatibility import RUNTIME_COMPATIBILITY, RuntimeCompatibility
from .connector import Connector
from .errors import CaptureError, PocketStationError, SessionError
from .session import RecordingOutcome, RunningSession, Session, StopResult
from .sources import Source, discover_sources

__version__ = "0.1.3"

__all__ = [
    "RUNTIME_COMPATIBILITY",
    "AudioFrame",
    "AudioInput",
    "AudioInputConfig",
    "Capture",
    "CaptureError",
    "Connector",
    "PcmSource",
    "PocketStationError",
    "RecordingOutcome",
    "RunningSession",
    "RuntimeCompatibility",
    "Session",
    "SessionError",
    "Source",
    "StopResult",
    "aio",
    "capture",
    "discover_sources",
]
