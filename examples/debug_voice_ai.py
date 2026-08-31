import asyncio
import os
import webbrowser
from array import array

import pocketstation.aio as pks
from pocketstation import Source
from pocketstation_demo import demo_relay_session
from pocketstation_demo.openai_realtime import OpenAIRealtime


async def main() -> None:
    app = input("Browser application playing the agent: ")
    buses = ("application", "microphone", "assistant")
    remote = await demo_relay_session(required_buses=buses)
    session = pks.Session(recording_root="recordings/voice-agent-debug")
    application = session.capture(Source.application(app))
    mic = session.capture(Source.microphone_default())
    assistant = session.audio_input("assistant")
    observed = session.polled_audio()
    labels = {
        int(application.send(observed)): "browser-output",
        int(assistant.output.send(observed)): "assistant-output",
    }
    publisher = remote.publisher(session)
    application.record("application")
    application.publish(publisher, "application")
    mic.record("microphone")
    mic.publish(publisher, "microphone")
    assistant.output.record("assistant")
    assistant.output.publish(publisher, "assistant")
    model = OpenAIRealtime(api_key=os.environ["OPENAI_API_KEY"], route_labels=labels)
    conversation = session.conversation(input=mic, output=assistant, voice_model=model)
    async with remote, await session.start() as running:
        await assistant.write(array("f", [0.0]) * 480)
        invite = await remote.wait_for_publisher_and_invitation(
            bus_id="assistant", timeout_seconds=30
        )
        print(f"Invitation: {invite.join_code}  {invite.join_url}")
        webbrowser.open(invite.join_url)
        await remote.wait_for_receiver(timeout_seconds=30)
        voice = await conversation.start(running)
        try:
            await voice.wait()
        finally:
            await voice.aclose(abort=True)
            model.print_report()


asyncio.run(main())
