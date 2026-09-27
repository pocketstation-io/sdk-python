"""Actual native PCM/recording with a deterministic held model callback (MOCKED)."""

from __future__ import annotations

import asyncio
import json
import os
from array import array
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path
from threading import Event
from time import monotonic, sleep

import pocketstation._api as pks
import pocketstation.aio as aio
import pytest
from pocketstation_demo import FasterWhisper, FasterWhisperConfiguration

FRAME_SECONDS = 0.02
SATURATION_FRAMES = 100
RECOVERY_FRAMES = 20
SHUTDOWN_BUDGET_SECONDS = 2.0


@dataclass(frozen=True)
class _Segment:
    start: float = 0.0
    end: float = 0.1
    text: str = "finite model result"


@dataclass(frozen=True)
class _Info:
    language: str = "en"
    language_probability: float = 1.0


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ("recover", "abort"))
async def test_complete_window_overload_isolates_recording_and_joins(
    tmp_path: Path, mode: str
) -> None:
    release = Event()

    class HeldModel:
        calls = 0
        active = 0
        maximum_active = 0

        def transcribe(self, _audio, **_options):
            self.calls += 1
            self.active += 1
            self.maximum_active = max(self.maximum_active, self.active)
            try:
                assert release.wait(6), "test model was not released"
                # Keep transcript production below the independently bounded output
                # subscriber capacity; this case overloads model INPUT windows.
                sleep(0.01)
                return iter((_Segment(),)), _Info()
            finally:
                self.active -= 1

    model = HeldModel()
    session = aio.Session(recording_root=tmp_path, channels=1)
    inputs = [
        session.audio_input(name, capacity_frames=32, frame_samples_per_channel=960)
        for name in ("application", "microphone")
    ]
    transcriber = FasterWhisper(
        FasterWhisperConfiguration(
            model="test-model",
            window_seconds=0.1,
            maximum_sources=2,
            inference_timeout_s=10,
        ),
        model_factory=lambda _: model,
        _audio_converter=lambda window: list(window.samples),
    )
    subscription = transcriber.attach_many(session, (item.output for item in inputs))
    for item, name in zip(inputs, ("application", "microphone"), strict=True):
        item.output.record(name)
    running = await session.start()
    events = []

    async def collect():
        stream = running.signals(subscription)
        while True:
            envelope = await stream.read(timeout_s=0.1)
            if isinstance(envelope, pks.EndOfStream):
                return
            if envelope is None:
                continue
            payload = json.loads(str(envelope.payload))
            assert str(envelope.lineage.source_id) == payload["source_id"]
            events.append(payload)

    collector = asyncio.create_task(collect())

    async def feed(frames):
        for _ in range(frames):
            for index, item in enumerate(inputs):
                await item.write(array("f", [0.1 if index == 0 else -0.1] * 960))
            await asyncio.sleep(FRAME_SECONDS)

    async def release_finite_callback():
        # Python cannot preempt arbitrary callback code. Release this finite
        # callback after cancellation starts; verify queued windows are discarded.
        await asyncio.sleep(0.05)
        release.set()

    releaser = None
    try:
        await feed(SATURATION_FRAMES)
        assert model.calls == 1
        metrics = await running.metrics()
        inference = next(
            item
            for item in metrics.operators
            if any(port.port_name == "window" for port in item.input_ports)
        )
        delivery = inference.input_delivery
        assert delivery.frames_dropped_total > 0
        assert delivery.queue_capacity_frames <= 16
        assert delivery.queue_peak_frames <= delivery.queue_capacity_frames
        if mode == "recover":
            release.set()
            await feed(RECOVERY_FRAMES)
        if mode == "recover":
            for item in inputs:
                await item.close()
        started = monotonic()
        if mode == "abort":
            releaser = asyncio.create_task(release_finite_callback())
            outcome = await running.cancel()
        else:
            outcome = await running.stop()
        shutdown_seconds = monotonic() - started
        await collector
        if output := os.environ.get("PKS_TEST_EVIDENCE_DIR"):
            (Path(output) / f"python-overload-{mode}.json").write_text(
                json.dumps(
                    {
                        "classification": (
                            "actual native PCM/recording; model callback MOCKED"
                        ),
                        "mode": mode,
                        "calls": model.calls,
                        "maximum_active": model.maximum_active,
                        "shutdown_seconds": shutdown_seconds,
                        "cancellation_contract": (
                            "finite callback released 50ms after cancel begins; "
                            "no arbitrary Python preemption"
                        ),
                        "saturated": asdict(delivery),
                        "outcome": asdict(outcome),
                        "events": events,
                    },
                    default=str,
                    indent=2,
                )
            )
        assert shutdown_seconds < SHUTDOWN_BUDGET_SECONDS
        assert outcome.success
        assert outcome.recording is not None and outcome.recording.complete
        assert model.maximum_active == 1 and model.active == 0
        for stem in outcome.recording.stems:
            assert stem.frames_written_total == SATURATION_FRAMES + (
                RECOVERY_FRAMES if mode == "recover" else 0
            )
            assert stem.frames_dropped_total == 0
            assert stem.discontinuities_total == 0
        assert all(
            route.delivery.frames_dropped_total == 0 for route in outcome.metrics.routes
        )
        assert all(item.worker.joined for item in outcome.metrics.operators)
        if mode == "abort":
            assert outcome.disposition == "cancelled"
            final_inference = next(
                item
                for item in outcome.metrics.operators
                if any(port.port_name == "window" for port in item.input_ports)
            )
            assert final_inference.worker.cancellation_total == 1
            assert model.calls < delivery.frames_enqueued_total
            completed = (model.calls, len(events))
            await asyncio.sleep(0.05)
            assert (model.calls, len(events)) == completed
            assert model.active == 0
        else:
            for item in inputs:
                source = [
                    event
                    for event in events
                    if event["source_id"] == str(item.source_id)
                ]
                assert any(
                    int(current["sequence_start"]) > int(previous["sequence_end"]) + 1
                    for previous, current in pairwise(source)
                )
    finally:
        release.set()
        for item in inputs:
            await item.close()
        await running.cancel()
        await collector
        if releaser is not None:
            await releaser
