from __future__ import annotations

import json
import sys
from array import array
from collections.abc import Callable
from typing import Any, cast

import pocketstation.aio as pks
import pytest
from pocketstation.voice import ConversationConfig, DuplexVoiceContext
from pocketstation_demo.openai_realtime import (
    OpenAIRealtime,
    RealtimeVoiceConfig,
    _OpenAIRealtimeVoice,
    _Pcm24To48,
)


class _EventSink:
    def __init__(self) -> None:
        self.records: list[dict[str, object]] = []

    def try_write(self, event: dict[str, object], *, timestamp_ns: int) -> None:
        assert timestamp_ns > 0
        self.records.append(event)

    async def aclose(self) -> None:
        return None


def test_realtime_provider_error_redacts_its_api_key_from_retained_state() -> None:
    api_key = "sk-test-catalog-secret"
    events = _EventSink()
    voice = _OpenAIRealtimeVoice(
        api_key=api_key,
        microphone_route_id=1,
        output=cast(Any, object()),
        events=cast(Any, events),
        route_labels={1: "microphone"},
    )

    voice._handle_event(
        {
            "type": "error",
            "error": {"message": f"authorization rejected {api_key}"},
        }
    )

    retained = json.dumps(events.records, sort_keys=True)
    outcome = voice.outcome("failed")
    assert api_key not in retained
    assert outcome.failure is not None
    assert api_key not in outcome.failure
    assert "[REDACTED]" in retained
    assert "[REDACTED]" in outcome.failure


@pytest.mark.asyncio
async def test_realtime_connection_is_one_shot_and_cleanup_is_idempotent() -> None:
    session = pks.Session()
    microphone = session.audio_input("microphone")
    assistant = session.audio_input("assistant")
    provider = OpenAIRealtime(api_key="test-only")
    context = DuplexVoiceContext(
        session=session,
        input=microphone.output,
        output=assistant,
        config=ConversationConfig(),
    )

    connection = provider.connect(context)
    with pytest.raises(RuntimeError, match="only one connection"):
        provider.connect(context)

    await connection.aclose()
    await connection.aclose()


def test_realtime_owns_bounded_pcm24_to_pcm48_conversion() -> None:
    pcm24 = array("h", [8_192] * 240)
    if sys.byteorder != "little":
        pcm24.byteswap()
    converter = _Pcm24To48()

    assert converter.append(pcm24.tobytes()) == ()
    frames = converter.finish()

    assert len(frames) == 1
    assert len(frames[0]) == 480
    assert all(0.24 < sample < 0.26 for sample in frames[0])


@pytest.mark.parametrize(
    "configuration",
    [
        lambda: RealtimeVoiceConfig(connect_timeout_s=True),
        lambda: RealtimeVoiceConfig(close_timeout_s=True),
        lambda: RealtimeVoiceConfig(maximum_session_s=True),
        lambda: RealtimeVoiceConfig(maximum_output_tokens=True),
        lambda: RealtimeVoiceConfig(input_queue_frames=True),
        lambda: RealtimeVoiceConfig(output_queue_chunks=True),
        lambda: RealtimeVoiceConfig(maximum_buffered_output_s=True),
    ],
)
def test_realtime_rejects_booleans_as_numeric_configuration(
    configuration: Callable[[], RealtimeVoiceConfig],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        configuration()
