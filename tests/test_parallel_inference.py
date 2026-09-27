"""Actual finite native graph with MOCKED model callbacks, no devices/services."""

from __future__ import annotations

import asyncio
import json
from array import array
from dataclasses import dataclass
from threading import Event
from time import monotonic, sleep

import pocketstation._api as pks
import pocketstation.aio as aio
import pytest
from pocketstation_demo import FasterWhisper, FasterWhisperConfiguration


@pytest.mark.parametrize("value", (0, 9, 1.5, True, None))
def test_rejects_invalid_inference_concurrency(value):
    with pytest.raises((ValueError, TypeError)):
        FasterWhisperConfiguration(inference_concurrency=value)


def test_cpu_budget_and_prompt_bounds():
    with pytest.raises(ValueError, match="budget"):
        FasterWhisperConfiguration(inference_concurrency=2, cpu_threads=1)
    with pytest.raises(ValueError, match="num_workers"):
        FasterWhisperConfiguration(inference_concurrency=2, num_workers=2)
    for value in ("", " ", "a\0b", "é" * 1025, False):
        with pytest.raises(ValueError, match="initial_prompt"):
            FasterWhisperConfiguration(initial_prompt=value)
    assert FasterWhisperConfiguration(initial_prompt="é" * 1024).initial_prompt
    assert FasterWhisperConfiguration().inference_concurrency == 1


def test_installed_demo_parses_explicit_model_resource_policy():
    from pocketstation_demo.demo import _parse_options

    options = _parse_options(
        [
            "--cpu-threads",
            "4",
            "--inference-concurrency",
            "2",
            "--initial-prompt",
            "Café application vocabulary",
        ]
    )
    assert options.cpu_threads == 4 and options.inference_concurrency == 2
    assert options.initial_prompt == "Café application vocabulary"


@dataclass(frozen=True)
class _Segment:
    start: float = 0.0
    end: float = 0.1
    text: str = "finite result"


@dataclass(frozen=True)
class _Info:
    language: str = "en"
    language_probability: float = 1.0


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ("stop", "cancel"))
async def test_source_affine_parallel_models_preserve_lineage_and_join(tmp_path, mode):
    release = Event()
    budgets, models, events = [], [], []
    active = maximum_active = calls = 0
    configuration = FasterWhisperConfiguration(
        model="mock",
        window_seconds=0.1,
        inference_concurrency=2,
        cpu_threads=5,
        maximum_sources=2,
        initial_prompt="application vocabulary",
    )

    class Model:
        def __init__(self):
            self.active = False
            self.sources = set()

        def transcribe(self, audio, **options):
            nonlocal active, maximum_active, calls
            assert not self.active
            assert options["initial_prompt"] == configuration.initial_prompt
            self.active = True
            self.sources.add(sum(audio) > 0)
            active += 1
            maximum_active = max(maximum_active, active)
            calls += 1
            try:
                assert release.wait(5), "held model was not released"
                sleep(0.01)
                return iter((_Segment(),)), _Info()
            finally:
                active -= 1
                self.active = False

    def create(worker):
        budgets.append(worker.cpu_threads)
        model = Model()
        models.append(model)
        return model

    transcriber = FasterWhisper(
        configuration,
        model_factory=create,
        _audio_converter=lambda window: list(window.samples),
    )
    session = aio.Session(recording_root=tmp_path, channels=1)
    inputs = [
        session.audio_input(name, capacity_frames=32, frame_samples_per_channel=960)
        for name in ("application", "microphone")
    ]
    subscription = transcriber.attach_many(session, (item.output for item in inputs))
    for item, name in zip(inputs, ("application", "microphone"), strict=True):
        item.output.record(name)
    running = await session.start()

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
    releaser = None

    async def release_finite_callback():
        # Arbitrary Python is not preemptible; test finite owned callback completion.
        await asyncio.sleep(0.05)
        release.set()

    try:
        for _ in range(20):
            for index, item in enumerate(inputs):
                await item.write(array("f", [0.1 if index == 0 else -0.1] * 960))
            await asyncio.sleep(0.02)
        assert active == 2 and calls == 2
        assert sorted(budgets) == [2, 3]
        started = monotonic()
        if mode == "stop":
            release.set()
            for item in inputs:
                await item.close()
            outcome = await running.stop()
        else:
            releaser = asyncio.create_task(release_finite_callback())
            outcome = await running.cancel()
        await collector
        assert monotonic() - started < 2
        assert outcome.success
        assert outcome.recording is not None and outcome.recording.complete
        assert [stem.frames_written_total for stem in outcome.recording.stems] == [
            20,
            20,
        ]
        assert all(item.worker.joined for item in outcome.metrics.operators)
        assert maximum_active == 2 and active == 0
        assert all(len(model.sources) == 1 for model in models)
        if mode == "stop":
            assert len(events) == 8
            assert {event["source_id"] for event in events} == {
                str(item.source_id) for item in inputs
            }
        else:
            assert outcome.disposition == "cancelled"
            completed = (calls, len(events))
            await asyncio.sleep(0.05)
            assert (calls, len(events)) == completed
    finally:
        release.set()
        for item in inputs:
            await item.close()
        await running.cancel()
        await collector
        if releaser is not None:
            await releaser
