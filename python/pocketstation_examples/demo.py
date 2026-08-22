"""Run the installed application-and-microphone product demo."""

import asyncio
import json
import os
import webbrowser

import pocketstation.aio as pks

from .faster_whisper import FasterWhisper

DEMO_CONTROL_PLANE_URL = "https://pocketstation-api.fly.dev"
DEMO_RELAY_URL = "https://pocketstation-relay.fly.dev"


async def run_demo() -> None:
    """Inspect both sides of a live voice application without mixing them."""
    application = input("Desktop application name, PID, or bundle ID: ")
    control_plane_url = os.getenv("POCKETSTATION_CONTROL_URL", DEMO_CONTROL_PLANE_URL)
    relay_url = os.getenv("POCKETSTATION_RELAY_URL", DEMO_RELAY_URL)
    if control_plane_url == DEMO_CONTROL_PLANE_URL:
        print("Using the limited shared demo; HTTP 429 means it is busy.")
    remote = await pks.RelaySession.create(
        control_plane_url=control_plane_url,
        relay_url=relay_url,
    )
    live = pks.capture(
        application=application, record_to="recordings", stream_audio=False
    )
    publisher = remote.publisher(live.session)
    for bus, stem in zip(("application", "microphone"), live.stems, strict=True):
        stem.publish(publisher, bus)
    transcripts = FasterWhisper().attach_many(live.session, live.stems)
    async with remote, live:
        invitation = await remote.wait_for_publisher_and_invitation(timeout_seconds=30)
        print(f"Listen live: {invitation.join_url}", flush=True)
        webbrowser.open(invitation.join_url)
        await remote.wait_for_receiver(timeout_seconds=30)
        async for event in live.signals(transcripts):
            transcript = json.loads(event.payload)
            print(f"source {transcript['source_id']}: {transcript['text']}", flush=True)


def main() -> None:
    """Run the installed demo until capture ends or the user interrupts it."""
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
