"""Exercise the public SDK from an isolated installed artifact."""

from __future__ import annotations

import json
import sys
from array import array
from pathlib import Path
from threading import Event

import pocketstation


def main() -> None:
    delivered = Event()

    def receive(
        item: pocketstation.ConnectorItem,
        _context: pocketstation.ConnectorContext,
    ) -> pocketstation.ConnectorDeliveryOutcome:
        if item.audio is None:
            raise RuntimeError("installed Connector received no audio")
        delivered.set()
        return pocketstation.ConnectorDeliveryOutcome.DELIVERED

    session = pocketstation.Session()
    audio = session.audio_input(
        "installed-consumer",
        capacity_frames=2,
        frame_samples_per_channel=4,
    )
    manifest = pocketstation.ConnectorManifest.audio(
        "io.pocketstation.test.installed-consumer.v1",
        package_version="1.0.0",
    )
    endpoint = session.register_connector(
        pocketstation.Connector.from_handler(manifest, receive)
    ).declare()
    audio.output.send(endpoint)
    audio.output.send(session.polled_audio())

    running = session.start()
    audio.write(array("f", [0.25, -0.25, 0.5, -0.5]))
    frame = running.audio.read(timeout_s=1.0)
    if frame is None:
        raise RuntimeError("installed consumer timed out waiting for audio")
    if not delivered.wait(1.0):
        raise RuntimeError("installed Connector did not receive audio")
    stop = running.stop()
    if not stop.success:
        raise RuntimeError("installed consumer Session did not stop successfully")
    if frame.source_id != audio.source_id or frame.stream_id != audio.stream_id:
        raise RuntimeError("installed consumer lost source or stream identity")
    package_path = Path(pocketstation.__file__).resolve()
    environment_root = Path(sys.prefix).resolve()
    if not package_path.is_relative_to(environment_root):
        raise RuntimeError("PocketStation was not imported from the environment")
    print(
        json.dumps(
            {
                "package_path": str(package_path),
                "python": sys.version.split()[0],
                "source_id": frame.source_id,
                "stream_id": frame.stream_id,
                "success": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
