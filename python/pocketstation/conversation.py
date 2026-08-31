"""Compatibility imports for the former conversation module.

New code should import these contracts from :mod:`pocketstation.voice`.
"""

from .voice import (
    ConversationConfig,
    ConversationContext,
    ConversationMessage,
    ConversationOutcome,
    ConversationResponse,
    ConversationResponseChunk,
    ConversationTurn,
    ToolEvent,
    TranscriptUpdate,
)
from .voice import (
    VoiceEvent as ConversationEvent,
)
from .voice.turns import ConversationDisposition, ConversationRole

__all__ = [
    "ConversationConfig",
    "ConversationContext",
    "ConversationDisposition",
    "ConversationEvent",
    "ConversationMessage",
    "ConversationOutcome",
    "ConversationResponse",
    "ConversationResponseChunk",
    "ConversationRole",
    "ConversationTurn",
    "ToolEvent",
    "TranscriptUpdate",
]
