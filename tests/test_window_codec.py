"""The private inter-Operator boundary is bounded and preserves exact lineage."""

from array import array

import pytest
from pocketstation_demo.audio_windows import AudioWindow
from pocketstation_demo.window_signal import decode_window, encode_window


def window():
    return AudioWindow(
        sample_rate_hz=48000,
        channel_count=1,
        session_id=18446744073709551615,
        source_id=9007199254740993,
        stream_id=3,
        clock_id=1,
        source_generation=1,
        policy_epoch=0,
        sequence_start=0,
        sequence_end=49,
        discontinuity_epoch=0,
        timestamp_start_ns=0,
        timestamp_end_ns=980000000,
        source_timestamp_start_ns=None,
        source_timestamp_end_ns=None,
        session_timestamp_start_ns=0,
        session_timestamp_end_ns=980000000,
        discontinuity_reasons=("sequence-gap",),
        samples=array("f", [0.0] * 48000),
    )


def test_exact_lineage_duration_and_clipped_pcm16():
    decoded, audio, duration = decode_window(
        encode_window(window(), [-2, -0.5, 0, 0.5, 2])
    )
    assert decoded.source_id == 9007199254740993
    assert decoded.session_id == 18446744073709551615
    assert decoded.source_timestamp_start_ns is None
    assert decoded.discontinuity_reasons == ("sequence-gap",)
    assert duration == 1000
    assert list(audio) == pytest.approx([-1, -0.5, 0, 0.5, 1], abs=0.0001)


def test_reject_truncation_oversize_and_nonfinite():
    encoded = encode_window(window(), [0.1])
    with pytest.raises(ValueError):
        decode_window(encoded[:-1])
    with pytest.raises(ValueError):
        decode_window(b"123")
    with pytest.raises(ValueError, match="bound"):
        encode_window(window(), [0.0] * 524288)
    with pytest.raises(ValueError, match="finite"):
        encode_window(window(), [float("nan")])
