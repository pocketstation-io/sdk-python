"""Example-owned provider integrations over the installed PocketStation SDK."""

from .demo import main
from .faster_whisper import FasterWhisper, FasterWhisperConfiguration
from .transcript import TRANSCRIPT_SIGNAL

__all__ = ["TRANSCRIPT_SIGNAL", "FasterWhisper", "FasterWhisperConfiguration", "main"]
