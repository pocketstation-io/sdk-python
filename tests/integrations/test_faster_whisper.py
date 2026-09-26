from __future__ import annotations

from collections.abc import Callable

import pytest
from pocketstation_demo import FasterWhisperConfiguration


@pytest.mark.parametrize(
    ("field_name", "configuration"),
    [
        ("cpu_threads", lambda: FasterWhisperConfiguration(cpu_threads=True)),
        ("num_workers", lambda: FasterWhisperConfiguration(num_workers=True)),
        ("beam_size", lambda: FasterWhisperConfiguration(beam_size=True)),
        (
            "queue_capacity_signals",
            lambda: FasterWhisperConfiguration(queue_capacity_signals=True),
        ),
        (
            "maximum_sources",
            lambda: FasterWhisperConfiguration(maximum_sources=True),
        ),
        (
            "maximum_output_bytes",
            lambda: FasterWhisperConfiguration(maximum_output_bytes=True),
        ),
        (
            "window_seconds",
            lambda: FasterWhisperConfiguration(window_seconds=True),
        ),
        (
            "create_timeout_s",
            lambda: FasterWhisperConfiguration(create_timeout_s=True),
        ),
        (
            "inference_timeout_s",
            lambda: FasterWhisperConfiguration(inference_timeout_s=True),
        ),
    ],
)
def test_faster_whisper_rejects_booleans_as_numeric_configuration(
    field_name: str,
    configuration: Callable[[], FasterWhisperConfiguration],
) -> None:
    with pytest.raises(TypeError, match=field_name):
        configuration()


def test_faster_whisper_configuration_keeps_every_work_bound_finite() -> None:
    configuration = FasterWhisperConfiguration()

    assert 0 < configuration.window_seconds <= 30
    assert 0 < configuration.queue_capacity_signals <= 4_096
    assert 0 < configuration.maximum_sources <= 64
    assert 0 < configuration.maximum_output_bytes <= 16_777_216
    assert 0 < configuration.create_timeout_s <= 600
    assert 0 < configuration.inference_timeout_s <= 600
