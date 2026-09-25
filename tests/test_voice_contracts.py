from __future__ import annotations

from collections.abc import Callable
from typing import cast

import pytest
from pocketstation import PocketStationError
from pocketstation.identity import SourceId, StreamId
from pocketstation.voice import (
    ConversationContext,
    ConversationMessage,
    ConversationOutcome,
    ConversationResponse,
    ConversationTurn,
    DuplexVoiceCapabilities,
    InterruptionConfig,
    MissingProviderCredentialError,
    ProviderStartupError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    ResponseCapabilities,
    ResponseChunk,
    SpeechActivity,
    SpeechDetectionCapabilities,
    SynthesisCapabilities,
    SynthesisChunk,
    ToolEvent,
    TranscriptionCapabilities,
    TranscriptUpdate,
    UnsupportedVoiceCapabilityError,
    VoiceConfigurationError,
    VoiceError,
    VoiceEvent,
)
from pocketstation.voice.speech_detection import SpeechActivityKind
from pocketstation.voice.turns import ConversationRole


def test_voice_errors_have_stable_codes_and_native_python_inheritance() -> None:
    cases = (
        (VoiceError, "voice.error"),
        (VoiceConfigurationError, "voice.invalid_configuration"),
        (MissingProviderCredentialError, "voice.missing_provider_credential"),
        (ProviderStartupError, "voice.provider_startup"),
        (ProviderTimeoutError, "voice.provider_timeout"),
        (ProviderUnavailableError, "voice.provider_unavailable"),
        (UnsupportedVoiceCapabilityError, "voice.unsupported_capability"),
    )

    for error_type, code in cases:
        error = error_type(
            "failure",
            stage="provider.start",
            provider_id="provider",
            cleaned_up=("connection",),
            input_remains_active=True,
        )
        assert isinstance(error, PocketStationError)
        assert error.code == code
        assert error.cleaned_up == ("connection",)

    assert isinstance(
        VoiceConfigurationError("failure", stage="configuration"), ValueError
    )
    assert isinstance(
        ProviderTimeoutError("failure", stage="provider.response"), TimeoutError
    )
    cleanup = ["connection"]
    error = VoiceError(
        "failure",
        stage="provider",
        cleaned_up=cast(tuple[str, ...], cleanup),
    )
    cleanup.clear()
    assert error.cleaned_up == ("connection",)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: VoiceError("failure", stage=""),
        lambda: VoiceError("failure", stage="provider", provider_id=" "),
        lambda: VoiceError(
            "failure",
            stage="provider",
            input_remains_active=cast(bool, 1),
        ),
    ],
)
def test_voice_error_recovery_facts_reject_invalid_values(
    factory: Callable[[], object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory()


def test_voice_capabilities_validate_flags_numbers_and_immutable_sequences() -> None:
    rates = [16_000, 48_000]
    formats = ["pcm_s16le"]
    capabilities = TranscriptionCapabilities(
        streaming=True,
        supported_sample_rates_hz=cast(tuple[int, ...], rates),
        input_formats=cast(tuple[str, ...], formats),
        maximum_session_duration_s=60,
    )
    rates.append(96_000)
    formats.append("pcm_f32le")

    assert capabilities.supported_sample_rates_hz == (16_000, 48_000)
    assert capabilities.input_formats == ("pcm_s16le",)

    invalid: tuple[Callable[[], object], ...] = (
        lambda: TranscriptionCapabilities(streaming=cast(bool, 1)),
        lambda: ResponseCapabilities(streaming=True, cancellation=cast(bool, "yes")),
        lambda: SynthesisCapabilities(
            streaming=True,
            supported_sample_rates_hz=cast(tuple[int, ...], (True,)),
        ),
        lambda: SpeechDetectionCapabilities(confidence=cast(bool, 1)),
        lambda: DuplexVoiceCapabilities(maximum_session_duration_s=float("inf")),
    )
    for factory in invalid:
        with pytest.raises((TypeError, ValueError)):
            factory()


def test_turn_context_and_outcome_validate_identity_state_and_counters() -> None:
    turn = ConversationTurn(
        id=1,
        utterance_id="utterance-1",
        text="hello",
        source_id=SourceId(1),
        stream_id=StreamId(2),
        source_sequence=0,
        source_timestamp_ns=10,
        audio_start_ns=10,
        audio_end_ns=20,
        received_timestamp_ns=21,
    )
    message = ConversationMessage("user", turn.text, turn.id, 21)
    history = [message]
    events: list[object] = ["event"]
    context = ConversationContext(cast(tuple[ConversationMessage, ...], history), True)
    outcome = ConversationOutcome(
        "completed",
        1,
        1,
        0,
        1,
        0,
        0,
        0,
        1,
        cast(tuple[ConversationMessage, ...], history),
        cast(tuple[object, ...], events),
    )
    history.clear()
    events.clear()

    assert context.history == (message,)
    assert outcome.history == (message,)
    assert outcome.events == ("event",)
    assert outcome.success

    invalid: tuple[Callable[[], object], ...] = (
        lambda: ConversationTurn(0, "u", "", None, None, None, None, None, None, 0),
        lambda: ConversationTurn(1, "u", "", None, None, None, None, 2, 1, 0),
        lambda: ConversationMessage(cast(ConversationRole, "invalid"), "", 1, 0),
        lambda: ConversationContext((), committed=cast(bool, 1)),
        lambda: ConversationOutcome("completed", -1, 0, 0, 0, 0, 0, 0, 0, (), ()),
    )
    for factory in invalid:
        with pytest.raises((TypeError, ValueError)):
            factory()


def test_provider_values_reject_ambiguous_booleans_and_invalid_timing() -> None:
    invalid: tuple[Callable[[], object], ...] = (
        lambda: VoiceEvent("event", 0, stage=""),
        lambda: VoiceEvent("event", 0, available=cast(bool, 1)),
        lambda: TranscriptUpdate("u", 1, "hello", final=cast(bool, 1)),
        lambda: ResponseChunk(text="hello", final=cast(bool, 1)),
        lambda: SynthesisChunk([], cast(int, 1.5), 1, 0),
        lambda: SynthesisChunk([], 16_000, True, 0),
        lambda: SpeechActivity(
            cast(SpeechActivityKind, "unsupported"),
            SourceId(1),
            StreamId(1),
            0,
            0,
            "provider",
            True,
        ),
        lambda: SpeechActivity(
            "speech.started",
            SourceId(0),
            StreamId(1),
            0,
            0,
            "provider",
            True,
        ),
        lambda: SpeechActivity(
            "speech.started",
            SourceId(1),
            StreamId(1),
            0,
            0,
            "provider",
            True,
            float("nan"),
        ),
        lambda: InterruptionConfig(enabled=cast(bool, 1)),
    )
    for factory in invalid:
        with pytest.raises((TypeError, ValueError)):
            factory()


def test_provider_sequences_are_copied_into_immutable_tuples() -> None:
    tool_events: list[ToolEvent] = []
    observations: list[object] = ["measured"]
    response = ResponseChunk(
        text="hello",
        tool_events=cast(tuple[ToolEvent, ...], tool_events),
    )
    completed = ConversationResponse(
        "hello",
        cast(tuple[ToolEvent, ...], tool_events),
    )
    synthesis = SynthesisChunk(
        [],
        16_000,
        1,
        0,
        provider_observations=cast(tuple[object, ...], observations),
    )
    observations.clear()

    assert response.tool_events == ()
    assert completed.tool_events == ()
    assert synthesis.provider_observations == ("measured",)
