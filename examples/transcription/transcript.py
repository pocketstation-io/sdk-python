"""Typed transcript signal shared by transcription providers."""

import pocketstation

TRANSCRIPT_SIGNAL = pocketstation.SignalSpec.text(
    pocketstation.TextFormat.JSON,
    role="transcript.final",
    schema="io.pocketstation.transcript.batch.v1",
)

__all__ = ["TRANSCRIPT_SIGNAL"]
