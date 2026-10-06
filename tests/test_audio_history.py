"""Normal Session execution through the installed production native wheel."""

import asyncio
from array import array
from time import monotonic, sleep

import pytest
from pocketstation import Session
from pocketstation.aio import Session as AsyncSession
from pocketstation.identity import StemId
from pocketstation.recording import (
    AudioHistoryConfig,
    AudioHistoryError,
    AudioHistoryState,
    RecordingClipWindow,
)

from .test_recording_clips import pcm


def wait_received(history, count):
    deadline = monotonic() + 5
    while history.observations().received_buffers_total < count:
        assert monotonic() < deadline
        sleep(0.001)


def test_live_source_windows_preserve_pcm_and_post_context():
    session = Session(channels=2, frame_duration_ms=20)
    history = session.audio_history()
    app = session.audio_input("app", capacity_frames=16)
    mic = session.audio_input("mic", capacity_frames=16)
    app.output.retain_audio()
    mic.output.retain_audio()
    running = session.start()
    try:
        for index in range(5):
            app.write(array("f", [index / 8, -index / 8] * 960), timeout_s=1)
            mic.write(array("f", [0.125, -0.125] * 960), timeout_s=1)
            wait_received(history, (index + 1) * 2)
        stem = next(s for s in history.stems if s.source_id == app.source_id)
        origin = stem.first_timestamp_ns
        window = RecordingClipWindow.around(
            origin + 40_000_000, origin + 60_000_000, 20_000_000, 60_000_000
        )
        with pytest.raises(AudioHistoryError, match="not arrived") as pending:
            history.read_clip(stem.stem_id, window)
        assert pending.value.code == "recording.history_not_ready"
        app.write(array("f", [0.625, -0.625] * 960), timeout_s=1)
        wait_received(history, 11)
        clip = history.read_clip(stem.stem_id, window)
        assert clip.stem.session_id == running.session_id
        assert clip.stem.source_id == app.source_id
        assert (clip.first_sample_frame, clip.sample_frames) == (960, 4800)
        assert pcm(clip.wav) == tuple(
            v for i in range(1, 6) for v in [i / 8, -i / 8] * 960
        )
        assert clip.discontinuities == ()
        with pytest.raises(AudioHistoryError) as unknown:
            history.read_clip(StemId(2**64 - 1), window)
        assert unknown.value.code == "recording.history_unknown_stem"
    finally:
        app.close()
        mic.close()
        assert running.stop().success
    assert history.observations().state is AudioHistoryState.COMPLETE


def test_eviction_clear_and_cancel_have_distinct_outcomes():
    session = Session(channels=2, frame_duration_ms=20)
    history = session.audio_history(AudioHistoryConfig(60_000_000, 23_040, 3))
    input_ = session.audio_input("app", capacity_frames=16)
    input_.output.retain_audio()
    running = session.start()
    try:
        for index in range(20):
            input_.write(array("f", [0.25, -0.25] * 960), timeout_s=1)
            wait_received(history, index + 1)
        stem = history.stems[0]
        observations = history.observations()
        assert (observations.retained_buffers, observations.retained_pcm_bytes) == (
            3,
            23040,
        )
        assert observations.evicted_buffers_total == 17
        with pytest.raises(AudioHistoryError) as expired:
            history.read_clip(
                stem.stem_id,
                RecordingClipWindow(
                    stem.first_timestamp_ns, stem.first_timestamp_ns + 20_000_000
                ),
            )
        assert expired.value.code == "recording.history_expired"
        history.clear()
        assert history.observations().retained_pcm_bytes == 0
        input_.write(array("f", [0.5, -0.5] * 960), timeout_s=1)
        wait_received(history, 21)
        assert history.observations().retained_buffers == 1
    finally:
        input_.close()
        running.cancel()
    assert history.observations().state is AudioHistoryState.CANCELLED
    assert history.observations().retained_pcm_bytes == 0


@pytest.mark.parametrize(
    "config",
    [
        AudioHistoryConfig(0),
        AudioHistoryConfig(max_buffers=0),
        AudioHistoryConfig(retention_ns=True),
    ],
)
def test_invalid_limits_fail_before_capture(config):
    with pytest.raises(AudioHistoryError) as failure:
        Session().audio_history(config)
    assert failure.value.code == "recording.history_invalid_limits"


def test_async_history_preserves_loop_progress_and_native_audio():
    async def run():
        session = AsyncSession(channels=2, frame_duration_ms=20)
        history = session.audio_history()
        input_ = session.audio_input("app", capacity_frames=16)
        input_.output.retain_audio()
        running = await session.start()
        try:
            await input_.try_write(array("f", [0.25, -0.25] * 960))
            deadline = monotonic() + 5
            while (await history.observations()).received_buffers_total < 1:
                assert monotonic() < deadline
                await asyncio.sleep(0.001)
            stem = (await history.get_stems())[0]
            window = RecordingClipWindow(
                stem.first_timestamp_ns, stem.final_timestamp_ns
            )
            ticks = []

            async def heartbeat():
                for _ in range(20):
                    await asyncio.sleep(0)
                    ticks.append(1)

            clips, _ = await asyncio.gather(
                asyncio.gather(
                    *(history.read_clip(stem.stem_id, window) for _ in range(4))
                ),
                heartbeat(),
            )
            assert len(ticks) == 20
            assert all(pcm(clip.wav) == (0.25, -0.25) * 960 for clip in clips)
        finally:
            await input_.close()
            assert (await running.stop()).success

    asyncio.run(run())
