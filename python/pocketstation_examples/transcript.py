"""Typed transcript signal shared by the example transcription provider."""

from pocketstation.graph import SignalSpec, TextFormat

TRANSCRIPT_SIGNAL = SignalSpec.text(
    TextFormat.JSON,
    role="transcript.final",
    schema="io.pocketstation.transcript.batch.v1",
)

__all__ = ["TRANSCRIPT_SIGNAL"]
