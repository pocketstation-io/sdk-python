"""Run the installed application-and-microphone product demo."""

import asyncio
import webbrowser

import pocketstation.aio as pks

from .faster_whisper import FasterWhisper
from .relay import demo_relay_session


async def run_demo() -> None:
    """Inspect both sides of a live voice application without mixing them."""
    application = input("Desktop application name, PID, or bundle ID: ")
    remote = await demo_relay_session()
    live = pks.capture(
        application=application,
        microphone=True,
        record_to="recordings",
        stream_audio=False,
    )
    publisher = remote.publisher(live.session)
    for bus, stem in zip(("application", "microphone"), live.stems, strict=True):
        stem.publish(publisher, bus)
    transcripts = FasterWhisper().transcribe(live)
    async with remote, live:
        invitation = await remote.wait_for_publisher_and_invitation(timeout_seconds=30)
        print(f"Listen live: {invitation.join_url}", flush=True)
        webbrowser.open(invitation.join_url)
        await remote.wait_for_receiver(timeout_seconds=30)
        async for transcript in transcripts:
            print(f"source {transcript.source_id}: {transcript.text}", flush=True)


def main() -> None:
    """Run the installed demo until capture ends or the user interrupts it."""
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
