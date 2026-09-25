"""Errors raised by provider-neutral voice composition."""

from __future__ import annotations

from ..errors import PocketStationError
from ._validation import require_boolean, require_nonempty


class VoiceError(PocketStationError):
    """Base error with cleanup and recovery facts for one voice operation."""

    _default_code = "voice.error"

    def __init__(
        self,
        message: str,
        *,
        stage: str,
        provider_id: str | None = None,
        cleaned_up: tuple[str, ...] = (),
        input_remains_active: bool = False,
        next_action: str | None = None,
    ) -> None:
        require_nonempty("stage", stage)
        if provider_id is not None:
            require_nonempty("provider_id", provider_id)
        require_boolean("input_remains_active", input_remains_active)
        immutable_cleanup = tuple(cleaned_up)
        super().__init__(message, self._default_code)
        self.stage = stage
        self.provider_id = provider_id
        self.cleaned_up = immutable_cleanup
        self.input_remains_active = input_remains_active
        self.next_action = next_action


class VoiceConfigurationError(VoiceError, ValueError):
    """The declared voice components cannot form one valid conversation."""

    _default_code = "voice.invalid_configuration"


class MissingProviderCredentialError(VoiceConfigurationError):
    """A selected provider did not receive a required credential."""

    _default_code = "voice.missing_provider_credential"


class ProviderStartupError(VoiceError):
    """A provider failed before the conversation became ready."""

    _default_code = "voice.provider_startup"


class ProviderTimeoutError(VoiceError, TimeoutError):
    """A provider operation exceeded its configured deadline."""

    _default_code = "voice.provider_timeout"


class ProviderUnavailableError(VoiceError):
    """A provider could not serve the requested voice operation."""

    _default_code = "voice.provider_unavailable"


class UnsupportedVoiceCapabilityError(VoiceConfigurationError):
    """A provider cannot satisfy a capability required by the composition."""

    _default_code = "voice.unsupported_capability"


__all__ = [
    "MissingProviderCredentialError",
    "ProviderStartupError",
    "ProviderTimeoutError",
    "ProviderUnavailableError",
    "UnsupportedVoiceCapabilityError",
    "VoiceConfigurationError",
    "VoiceError",
]
