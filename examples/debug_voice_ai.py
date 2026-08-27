"""Find where an interruptible voice agent lost audio or time."""

import asyncio
import os
import webbrowser

import pocketstation.aio as pks
from pocketstation import Source
from pocketstation_examples import demo_relay_session
from pocketstation_examples.openai_realtime import OpenAIRealtimeVoice, silent_frame


async def main() -> None:
    application_name = input("Browser application playing the agent: ")
    remote = await demo_relay_session(
        required_buses=("application", "microphone", "assistant")
    )
    session = pks.Session(recording_root="recordings/voice-agent-debug")
    application = session.capture(Source.application(application_name))
    microphone = session.capture(Source.microphone_default())
    assistant = session.audio_input("assistant")
    audio = session.polled_audio()
    routes = {
        int(application.send(audio)): "browser-output",
        int(microphone.send(audio)): "microphone",
        int(assistant.output.send(audio)): "assistant-output",
    }
    publisher = remote.publisher(session)
    application.record("application")
    application.publish(publisher, "application")
    microphone.record("microphone")
    microphone.publish(publisher, "microphone")
    assistant.output.record("assistant")
    assistant.output.publish(publisher, "assistant")
    events = session.event_input("openai-realtime")
    event_log = session.subscribe(events.output, signal=events.signal)
    voice = OpenAIRealtimeVoice(
        api_key=os.environ["OPENAI_API_KEY"],
        microphone_route_id=next(
            route for route, name in routes.items() if name == "microphone"
        ),
        output=assistant,
        events=events,
        route_labels=routes,
    )
    async with remote:
        try:
            await voice.connect()
            async with await session.start() as running:
                await voice.start(running, event_log)
                for _ in range(10):
                    await assistant.write(silent_frame())
                    await asyncio.sleep(0.01)
                await remote.wait_for_publisher(timeout_seconds=30)
                invitation = await remote.create_receiver_invitation(bus_id="assistant")
                print(f"Invitation code: {invitation.join_code}")
                print(f"Agent audio: {invitation.join_url}")
                webbrowser.open(invitation.join_url)
                await remote.wait_for_receiver(timeout_seconds=30)
                voice.enable_input()
                print("Speak, interrupt the reply, then press Ctrl-C to stop.")
                await voice.wait()
        finally:
            await voice.aclose()
            voice.print_report()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
