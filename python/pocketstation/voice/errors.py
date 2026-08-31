"""Errors raised by provider-neutral voice composition."""

from __future__ import annotations


class VoiceError(Exception):
    """Base error with cleanup and recovery facts for one voice operation."""

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
        super().__init__(message)
        self.stage = stage
        self.provider_id = provider_id
        self.cleaned_up = cleaned_up
        self.input_remains_active = input_remains_active
        self.next_action = next_action


class VoiceConfigurationError(VoiceError, ValueError):
    """The declared voice components cannot form one valid conversation."""


class MissingProviderCredentialError(VoiceConfigurationError):
    """A selected provider did not receive a required credential."""


class ProviderStartupError(VoiceError):
    """A provider failed before the conversation became ready."""


class ProviderTimeoutError(VoiceError, TimeoutError):
    """A provider operation exceeded its configured deadline."""


class ProviderUnavailableError(VoiceError):
    """A provider could not serve the requested voice operation."""


class UnsupportedVoiceCapabilityError(VoiceConfigurationError):
    """A provider cannot satisfy a capability required by the composition."""


__all__ = [
    "MissingProviderCredentialError",
    "ProviderStartupError",
    "ProviderTimeoutError",
    "ProviderUnavailableError",
    "UnsupportedVoiceCapabilityError",
    "VoiceConfigurationError",
    "VoiceError",
]
