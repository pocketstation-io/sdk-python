"""Transcribe both sides of a desktop voice application without mixing them."""

import asyncio

import pocketstation.aio as pks
from pocketstation_examples import FasterWhisper


async def main() -> None:
    application = input("Desktop voice application: ")
    live = pks.capture(
        application=application,
        microphone=True,
        stream_audio=False,
    )
    transcripts = FasterWhisper().transcribe(live)

    async with live:
        async for transcript in transcripts:
            print(f"source {transcript.source_id}: {transcript.text}")


asyncio.run(main())
