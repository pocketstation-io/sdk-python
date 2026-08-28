"""Transcribe a desktop voice application and microphone as separate stems."""

import asyncio

import pocketstation.aio as pks
from pocketstation_demo import FasterWhisper


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
