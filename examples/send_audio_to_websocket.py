"""Send one application's source-aware PCM frames to a WebSocket provider."""

import asyncio
import os

import pocketstation as pks
import pocketstation.aio as pks_aio
from websockets.asyncio.client import connect


async def main() -> None:
    application_name = input("Application to capture: ")
    token = os.environ["AUDIO_WEBSOCKET_TOKEN"]
    async with connect(
        os.environ["AUDIO_WEBSOCKET_URL"],
        additional_headers={"Authorization": f"Bearer {token}"},
    ) as socket:

        async def send_audio(frame: pks.AudioFrame) -> None:
            await socket.send(frame.samples)

        session = pks_aio.Session()
        session.capture(pks.Source.application(application_name)).send_to(
            pks_aio.Connector(send=send_audio)
        )
        async with await session.start():
            await asyncio.Event().wait()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
