"""Run the installed application-and-microphone PocketStation demo."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import webbrowser
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from pathlib import Path

import pocketstation.aio as pks
from pocketstation.relay import ReceiverInvitation

from .faster_whisper import FasterWhisper, FasterWhisperConfiguration
from .relay import demo_relay_session
from .transcript import Transcript

_DEFAULT_DURATION_SECONDS = 30.0
_MAXIMUM_DURATION_SECONDS = 3_600.0


@dataclass(frozen=True, slots=True)
class DemoOptions:
    """Finite settings for one installed demo run."""

    application: str | None
    microphone_id: str | None
    recording_root: Path
    duration_seconds: float
    model: str
    allow_model_download: bool
    no_browser: bool
    output_format: str


class _DemoOutput:
    def __init__(self, output_format: str) -> None:
        self._jsonl = output_format == "jsonl"

    def invitation(self, bus_id: str, invitation: ReceiverInvitation) -> str:
        # expose_url() is intentionally called only at this explicit display or
        # automation boundary. Invitation repr/str remain redacted.
        share_url = invitation.expose_url()
        if self._jsonl:
            self._json(
                {
                    "event": "invitation",
                    "bus_id": bus_id,
                    "share_url": share_url,
                }
            )
        else:
            print(f"{bus_id.title()} invitation: {invitation.share_alias}", flush=True)
            print(f"{bus_id.title()} listen URL: {share_url}", flush=True)
        return share_url

    def receivers_connected(self) -> None:
        if not self._jsonl:
            print("Both browser receivers connected.", flush=True)

    def transcript(self, transcript: Transcript) -> None:
        if self._jsonl:
            self._json(
                {
                    "event": "transcript",
                    "source_id": str(transcript.source_id),
                    "text": transcript.text,
                }
            )
        else:
            print(
                f"source {transcript.source_id}: {transcript.text}",
                flush=True,
            )

    def completed(self, duration_seconds: float) -> None:
        if self._jsonl:
            self._json(
                {
                    "event": "result",
                    "status": "completed",
                    "duration_seconds": duration_seconds,
                    "receiver_count": 2,
                }
            )
        else:
            print("Capture completed and both recording stems finalized.", flush=True)

    @staticmethod
    def _json(value: dict[str, object]) -> None:
        print(json.dumps(value, separators=(",", ":"), sort_keys=False), flush=True)


async def run_demo(options: DemoOptions) -> None:
    """Capture, publish, transcribe, and record two independent live stems."""
    application = options.application
    if application is None:
        application = input("Desktop application name, PID, or bundle ID: ")
    if not application.strip():
        raise ValueError("application must not be empty")

    remote = await demo_relay_session()
    live = pks.capture(
        application=application,
        microphone=options.microphone_id or True,
        record_to=options.recording_root,
        stream_audio=False,
    )
    if live.microphone_stem is None:
        raise RuntimeError("the installed demo requires a microphone stem")

    publisher = remote.publisher(live.session)
    live.application_stem.publish(publisher, "application")
    live.microphone_stem.publish(publisher, "microphone")
    transcripts = FasterWhisper(
        FasterWhisperConfiguration(
            model=options.model,
            allow_model_download=options.allow_model_download,
        )
    ).transcribe(live)
    output = _DemoOutput(options.output_format)

    async with remote, live:
        await remote.wait_for_publisher(timeout_seconds=30)
        invitation_urls: list[str] = []
        for bus_id in ("application", "microphone"):
            invitation = await remote.create_receiver_invitation(bus_id=bus_id)
            invitation_urls.append(output.invitation(bus_id, invitation))
        if not options.no_browser:
            for share_url in invitation_urls:
                webbrowser.open(share_url)
        await remote.wait_for_receiver(
            minimum_receivers=2,
            timeout_seconds=30,
        )
        output.receivers_connected()
        await _consume_transcripts_for(
            transcripts,
            duration_seconds=options.duration_seconds,
            output=output,
        )

    output.completed(options.duration_seconds)


async def _consume_transcripts_for(
    transcripts: AsyncIterator[Transcript],
    *,
    duration_seconds: float,
    output: _DemoOutput,
) -> None:
    try:
        async with asyncio.timeout(duration_seconds):
            async for transcript in transcripts:
                output.transcript(transcript)
    except TimeoutError:
        return


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pocketstation-demo",
        description=(
            "Capture one desktop application and one microphone as separate "
            "Relay and recording stems."
        ),
    )
    parser.add_argument(
        "--application",
        type=_nonempty_text,
        help="application display name, process ID, or bundle ID; prompts if omitted",
    )
    parser.add_argument(
        "--microphone-id",
        type=_nonempty_text,
        help="stable microphone device ID; the current default is used if omitted",
    )
    parser.add_argument(
        "--recording-root",
        type=Path,
        default=Path("recordings"),
        help="directory for the independent application and microphone stems",
    )
    parser.add_argument(
        "--duration-seconds",
        type=_finite_duration,
        default=_DEFAULT_DURATION_SECONDS,
        help=(
            "capture duration after both receivers connect "
            f"(default: {_DEFAULT_DURATION_SECONDS:g}; maximum: "
            f"{_MAXIMUM_DURATION_SECONDS:g})"
        ),
    )
    parser.add_argument(
        "--model",
        type=_nonempty_text,
        default="base",
        help="installed faster-whisper model name or local model path",
    )
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        help="allow faster-whisper to download a missing model",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="print invitation URLs without opening browser tabs",
    )
    parser.add_argument(
        "--output-format",
        choices=("human", "jsonl"),
        default="human",
        help=(
            "human-readable output or JSON Lines for ephemeral automation; "
            "jsonl explicitly exposes private invitation URLs"
        ),
    )
    return parser


def _parse_options(arguments: Sequence[str] | None = None) -> DemoOptions:
    values = _parser().parse_args(arguments)
    return DemoOptions(
        application=values.application,
        microphone_id=values.microphone_id,
        recording_root=values.recording_root,
        duration_seconds=values.duration_seconds,
        model=values.model,
        allow_model_download=values.allow_model_download,
        no_browser=values.no_browser,
        output_format=values.output_format,
    )


def _nonempty_text(value: str) -> str:
    if not value.strip():
        raise argparse.ArgumentTypeError("value must not be empty")
    return value


def _finite_duration(value: str) -> float:
    try:
        duration = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "duration must be a number of seconds"
        ) from error
    if not math.isfinite(duration) or not 0 < duration <= _MAXIMUM_DURATION_SECONDS:
        raise argparse.ArgumentTypeError(
            "duration must be greater than 0 and at most "
            f"{_MAXIMUM_DURATION_SECONDS:g} seconds"
        )
    return duration


def main(arguments: Sequence[str] | None = None) -> None:
    """Run one finite installed demo."""
    asyncio.run(run_demo(_parse_options(arguments)))


if __name__ == "__main__":
    main()
