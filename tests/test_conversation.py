from __future__ import annotations

import pytest
from pocketstation.conversation import (
    ConversationConfig,
    ConversationResponse,
    ToolEvent,
    TranscriptUpdate,
)


def test_given_unbounded_contract_when_created_then_validation_rejects_it() -> None:
    with pytest.raises(ValueError, match="history_capacity"):
        ConversationConfig(history_capacity=0)
    with pytest.raises(ValueError, match="response_timeout_s"):
        ConversationConfig(response_timeout_s=0)
    with pytest.raises(ValueError, match="provider_close_timeout_s"):
        ConversationConfig(provider_close_timeout_s=0)
    with pytest.raises(ValueError, match="output_drain_timeout_s"):
        ConversationConfig(output_drain_timeout_s=0)
    with pytest.raises(ValueError, match="maximum_output_frames_per_turn"):
        ConversationConfig(maximum_output_frames_per_turn=1_000_001)
    with pytest.raises(ValueError, match="final transcript update"):
        TranscriptUpdate("speech-1", 1, "", final=True)
    with pytest.raises(ValueError, match="stable_prefix"):
        TranscriptUpdate("speech-1", 1, "hello", stable_prefix="goodbye")
    with pytest.raises(ValueError, match="response text"):
        ConversationResponse(" ")
    with pytest.raises(ValueError, match="tool event name"):
        ToolEvent("", "completed")


def test_given_default_contract_when_created_then_all_work_is_finite() -> None:
    config = ConversationConfig()
    assert config.history_capacity == 32
    assert config.event_capacity == 128
    assert config.provider_close_timeout_s == 10
    assert config.response_timeout_s == 60
    assert config.synthesis_timeout_s == 60
    assert config.maximum_output_frames_per_turn == 3_000
