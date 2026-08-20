"""Capture one playing macOS application and the default microphone."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import monotonic

import pocketstation


def _application_source(name: str) -> pocketstation.DiscoveredSource:
    matches = tuple(
        source
        for source in pocketstation.discover_sources()
        if source.name == name
        and source.stable_id.kind is pocketstation.SourceKind.APPLICATION
    )
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one application named {name!r}, found {len(matches)}"
        )
    return matches[0]


def capture_physical_sources(
    *,
    application_name: str,
    recording_root: Path,
    duration_s: float = 5.0,
) -> dict[str, object]:
    """Run the physical app+microphone path and return bounded observations."""
    if not 0.1 <= duration_s <= 300:
        raise ValueError("duration_s must be between 0.1 and 300")
    application_source = _application_source(application_name)
    session = pocketstation.Session(recording_root=recording_root)
    application = session.capture(
        pocketstation.Source.from_discovered(application_source)
    )
    microphone = session.capture(pocketstation.Source.microphone_default())
    endpoint = session.polled_audio()
    application.send(endpoint)
    microphone.send(endpoint)
    application.record("application")
    microphone.record("microphone")

    running = session.start()
    frames_by_stem: dict[int, int] = {}
    deadline = monotonic() + duration_s
    try:
        while monotonic() < deadline:
            frame = running.audio.read(timeout_s=0.1)
            if frame is not None:
                frames_by_stem[frame.stem_id] = frames_by_stem.get(frame.stem_id, 0) + 1
    finally:
        outcome = running.stop()

    expected_stems = {application.id, microphone.id}
    recording = outcome.recording
    success = (
        outcome.success
        and set(frames_by_stem) == expected_stems
        and recording is not None
        and recording.complete
        and {stem.stem_name for stem in recording.stems}
        == {"application", "microphone"}
        and all(stem.frames_written_total > 0 for stem in recording.stems)
    )
    result: dict[str, object] = {
        "application": application_source.name,
        "application_process_id": application_source.process_id,
        "frames_by_stem": frames_by_stem,
        "microphone_permission": str(pocketstation.microphone_permission_observation()),
        "recording_complete": recording is not None and recording.complete,
        "success": success,
    }
    if not success:
        raise RuntimeError(json.dumps(result, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--application", required=True)
    parser.add_argument("--record-to", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=5)
    arguments = parser.parse_args()
    result = capture_physical_sources(
        application_name=arguments.application,
        recording_root=arguments.record_to,
        duration_s=arguments.duration,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
