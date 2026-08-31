from __future__ import annotations

import base64
from array import array
from types import SimpleNamespace

import pytest
from pocketstation_demo.openai_realtime import (
    OpenAIRealtime,
    _encode_microphone_frame,
    _transcript_event_values,
    _TranscriptProgress,
)


@pytest.mark.parametrize("sample_count", [480, 960])
def test_realtime_input_accepts_ten_and_twenty_millisecond_frames(
    sample_count: int,
) -> None:
    samples = array("f", [0.25] * sample_count)
    frame = SimpleNamespace(
        sample_rate_hz=48_000,
        channel_count=1,
        samples_f32le=samples.tobytes(),
    )

    encoded = _encode_microphone_frame(frame)

    assert len(base64.b64decode(encoded, validate=True)) == sample_count


def test_realtime_transcript_deltas_receive_stable_identity_and_revision() -> None:
    transcripts: dict[str, _TranscriptProgress] = {}
    first = _transcript_event_values(
        transcripts,
        "conversation.item.input_audio_transcription.delta",
        {"item_id": "item-1"},
        "hello",
    )
    second = _transcript_event_values(
        transcripts,
        "conversation.item.input_audio_transcription.delta",
        {"item_id": "item-1"},
        " world",
    )
    final = _transcript_event_values(
        transcripts,
        "conversation.item.input_audio_transcription.completed",
        {"item_id": "item-1"},
        "hello world",
    )

    assert first == {
        "text": "hello",
        "stable_prefix": "",
        "utterance_id": "item-1",
        "transcript_revision": 1,
        "final": False,
    }
    assert second["text"] == "hello world"
    assert second["transcript_revision"] == 2
    assert final["transcript_revision"] == 3
    assert final["stable_prefix"] == "hello world"
    assert final["final"] is True


def test_realtime_capabilities_do_not_invent_stable_partial_text() -> None:
    provider = OpenAIRealtime(api_key="test-only")

    assert provider.capabilities.transcript_revisions is True
    assert provider.capabilities.stable_prefix is False
