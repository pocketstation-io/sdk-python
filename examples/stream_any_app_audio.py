"""Stream any selected desktop application's audio to a browser."""

import asyncio
import webbrowser

import pocketstation.aio as pks
from pocketstation_examples import demo_relay_session


async def main() -> None:
    application = input("Application to stream (for example, Spotify): ")
    remote = await demo_relay_session(required_buses=("application",))
    live = pks.capture(application=application, stream_audio=False)
    live.application_stem.publish(remote.publisher(live.session), "application")

    async with remote, live:
        invitation = await remote.wait_for_publisher_and_invitation(timeout_seconds=30)
        print(f"Invitation code: {invitation.join_code}")
        print(f"Listen in a browser: {invitation.join_url}")
        webbrowser.open(invitation.join_url)
        await remote.wait_for_receiver(timeout_seconds=30)
        print("Browser connected. Press Ctrl-C to stop.")
        await asyncio.Event().wait()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
