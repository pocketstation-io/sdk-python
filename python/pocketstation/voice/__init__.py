"""Provider-neutral contracts and composition for live voice applications.

Provider packages implement these contracts. PocketStation continues to own
the native Session, source-aware audio paths, bounded routing, recording,
Relay delivery, and output cancellation.
"""

from .capabilities import (
    DuplexVoiceCapabilities,
    ResponseCapabilities,
    SpeechDetectionCapabilities,
    SynthesisCapabilities,
    TranscriptionCapabilities,
    VoiceCapabilities,
)
from .configuration import (
    ConversationConfig,
    InterruptionConfig,
    VoiceDeadlines,
    VoiceLimits,
)
from .conversation import Conversation, RunningConversation
from .duplex import (
    DuplexVoiceConnection,
    DuplexVoiceContext,
    DuplexVoiceModel,
)
from .errors import (
    MissingProviderCredentialError,
    ProviderStartupError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    UnsupportedVoiceCapabilityError,
    VoiceConfigurationError,
    VoiceError,
)
from .events import VoiceEvent
from .response import (
    ConversationResponse,
    ConversationResponseChunk,
    ResponseChunk,
    ResponseModel,
    ResponseRequest,
    ToolEvent,
)
from .speech_detection import SpeechActivity, SpeechDetector
from .synthesis import (
    SpeechSynthesizer,
    SynthesisChunk,
    SynthesisRequest,
)
from .transcription import (
    StreamingTranscriber,
    TranscriptionConnection,
    TranscriptUpdate,
)
from .turns import (
    ConversationContext,
    ConversationMessage,
    ConversationOutcome,
    ConversationTurn,
)

__all__ = [
    "Conversation",
    "ConversationConfig",
    "ConversationContext",
    "ConversationMessage",
    "ConversationOutcome",
    "ConversationResponse",
    "ConversationResponseChunk",
    "ConversationTurn",
    "DuplexVoiceCapabilities",
    "DuplexVoiceConnection",
    "DuplexVoiceContext",
    "DuplexVoiceModel",
    "InterruptionConfig",
    "MissingProviderCredentialError",
    "ProviderStartupError",
    "ProviderTimeoutError",
    "ProviderUnavailableError",
    "ResponseCapabilities",
    "ResponseChunk",
    "ResponseModel",
    "ResponseRequest",
    "RunningConversation",
    "SpeechActivity",
    "SpeechDetectionCapabilities",
    "SpeechDetector",
    "SpeechSynthesizer",
    "StreamingTranscriber",
    "SynthesisCapabilities",
    "SynthesisChunk",
    "SynthesisRequest",
    "ToolEvent",
    "TranscriptUpdate",
    "TranscriptionCapabilities",
    "TranscriptionConnection",
    "UnsupportedVoiceCapabilityError",
    "VoiceCapabilities",
    "VoiceConfigurationError",
    "VoiceDeadlines",
    "VoiceError",
    "VoiceEvent",
    "VoiceLimits",
]
