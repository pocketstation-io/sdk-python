"""Private bounded PCM16 window wire format between demo-owned Operators.

The audio reader never performs inference. Each queued value owns one converted
16 kHz mono window plus its original lineage. Core owns queue admission/loss.
"""

from __future__ import annotations

import json
import math
import struct
import sys
from array import array
from collections.abc import Iterable
from dataclasses import fields
from typing import cast

from pocketstation.graph import SignalSpec

from .audio_windows import AudioWindow

WINDOW_SIGNAL = SignalSpec.binary(
    role="transcription.window", schema="pks.demo.window.pcm16.v1"
)
MAXIMUM_WINDOW_BYTES = 1_048_576
MAXIMUM_HEADER_BYTES = 8_192
INTEGER_FIELDS = (
    "session_id",
    "source_id",
    "stream_id",
    "policy_epoch",
    "sequence_start",
    "sequence_end",
    "discontinuity_epoch",
    "timestamp_start_ns",
    "timestamp_end_ns",
    "source_timestamp_start_ns",
    "source_timestamp_end_ns",
    "session_timestamp_start_ns",
    "session_timestamp_end_ns",
)


def encode_window(window: AudioWindow, audio: object) -> bytes:
    metadata = {
        field.name: getattr(window, field.name)
        for field in fields(window)
        if field.name != "samples"
    }
    for key in INTEGER_FIELDS:
        if metadata[key] is not None:
            metadata[key] = str(metadata[key])
    metadata["duration_ms"] = window.duration_ms
    header = json.dumps(metadata, separators=(",", ":")).encode()
    if len(header) > MAXIMUM_HEADER_BYTES:
        raise ValueError("transcription window metadata exceeds its bound")
    pcm = array("h")
    limit = (MAXIMUM_WINDOW_BYTES - len(header) - 4) // 2
    for value in cast(Iterable[float], audio):
        if len(pcm) >= limit or not math.isfinite(value):
            raise ValueError("transcription PCM window exceeds its finite bound")
        pcm.append(
            math.floor(
                max(-1.0, min(1.0, value)) * (32768 if value < 0 else 32767) + 0.5
            )
        )
    if sys.byteorder != "little":
        pcm.byteswap()
    return struct.pack("<I", len(header)) + header + pcm.tobytes()


def decode_window(payload: object) -> tuple[AudioWindow, array[float], int]:
    if not isinstance(payload, bytes) or not 4 <= len(payload) <= MAXIMUM_WINDOW_BYTES:
        raise ValueError("invalid transcription window payload")
    length = struct.unpack_from("<I", payload)[0]
    if (
        not 0 < length <= MAXIMUM_HEADER_BYTES
        or length + 4 > len(payload)
        or (len(payload) - length - 4) % 2
    ):
        raise ValueError("invalid transcription window framing")
    metadata = json.loads(payload[4 : 4 + length])
    duration_ms = metadata.pop("duration_ms")
    for key in INTEGER_FIELDS:
        metadata[key] = None if metadata.get(key) is None else int(metadata[key])
    metadata["discontinuity_reasons"] = tuple(metadata["discontinuity_reasons"])
    window = AudioWindow(**metadata)
    pcm = array("h")
    pcm.frombytes(payload[4 + length :])
    if sys.byteorder != "little":
        pcm.byteswap()
    return (
        window,
        array("f", (value / (32768 if value < 0 else 32767) for value in pcm)),
        duration_ms,
    )
