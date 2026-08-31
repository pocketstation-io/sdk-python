from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from time import monotonic

import pocketstation._api as pks
import pocketstation.aio as aio
import pytest
from pocketstation._native import Session as NativeSession

CHILD = Path(__file__).with_name("_pkss_child.py")


def session_with_product_sources(tmp_path: Path) -> pks.Session:
    if not hasattr(NativeSession, "conformance"):
        pytest.skip("native extension was not built with conformance-fixtures")
    session = pks.Session._from_native(NativeSession.conformance(tmp_path))
    audio = session.polled_audio()
    session.capture(pks.Source.application("PocketStation Python Fixture")).send(audio)
    session.capture(pks.Source.microphone_default()).send(audio)
    return session


def sidecar_spec(
    mode: str,
    *,
    sidecar_id: int = 7,
    capacity: int = 2,
    shutdown_s: float = 0.2,
) -> pks.SidecarProcessSpec:
    return pks.SidecarProcessSpec(
        sidecar_id,
        sys.executable,
        (str(CHILD), mode),
        data_capacity_messages=capacity,
        deadlines=pks.SidecarDeadlines(
            ready_s=1.0,
            processing_s=1.0,
            shutdown_s=shutdown_s,
        ),
    )


def message(*, sequence: int = 1, payload: bytes = b"hello") -> pks.SidecarMessage:
    return pks.SidecarMessage.signal(
        payload,
        signal_id="io.pocketstation.test.signal.v1",
        stream_id=11,
        sequence_number=sequence,
        timestamp_ns=sequence * 1_000,
        role="transcript",
        schema="application/octet-stream",
    )


def test_session_owned_sidecar_round_trip_and_graceful_reap(tmp_path: Path) -> None:
    session = session_with_product_sources(tmp_path)
    handle = session.register_sidecar(sidecar_spec("healthy"))

    running = session.start()
    sidecar = running.sidecar(handle)
    sidecar.send(message())
    received = sidecar.messages.read(timeout_s=1.0)

    assert isinstance(received, pks.SidecarMessage)
    assert received.payload == b"hello"
    assert received.stream_id == 11
    assert received.sequence_number == 1
    assert received.role == "transcript"
    live = sidecar.snapshot()
    assert live.state is pks.SidecarState.RUNNING
    assert live.data_enqueued_total == 1
    assert live.data_received_total == 1

    stopped = running.stop()
    assert stopped.success
    [final] = stopped.sidecar_outcomes
    assert final.state == pks.SidecarState.REAPED.value
    assert final.reaps_total == 1
    assert final.visited(pks.SidecarState.CLOSING.value)
    assert final.visited(pks.SidecarState.CLOSED.value)
    assert final.visited(pks.SidecarState.REAPED.value)


def test_sidecar_data_queue_saturation_is_typed_and_counted(tmp_path: Path) -> None:
    session = session_with_product_sources(tmp_path)
    handle = session.register_sidecar(
        sidecar_spec("saturated", capacity=1, shutdown_s=0.2)
    )
    running = session.start()
    sidecar = running.sidecar(handle)
    saturated = False
    payload = b"x" * 65_536
    for sequence in range(1, 1_001):
        try:
            sidecar.send(message(sequence=sequence, payload=payload))
        except pks.SidecarBackpressureError as error:
            assert error.code == "sidecar.queue_full"
            saturated = True
            break
    assert saturated, "the finite native sidecar queue must expose saturation"
    assert sidecar.snapshot().data_dropped_total >= 1
    running.cancel()


def test_malformed_sidecar_fails_transactional_start(tmp_path: Path) -> None:
    session = session_with_product_sources(tmp_path)
    session.register_sidecar(sidecar_spec("malformed"))

    with pytest.raises(pks.PocketStationError) as caught:
        session.start()

    assert caught.value.code == "session.runtime_start_failed"
    assert "sidecar" in str(caught.value).lower()


def test_hung_sidecar_is_killed_and_reaped_within_deadline(tmp_path: Path) -> None:
    session = session_with_product_sources(tmp_path)
    handle = session.register_sidecar(sidecar_spec("hang", shutdown_s=0.05))
    running = session.start()
    assert running.sidecar(handle).snapshot().state is pks.SidecarState.RUNNING

    started = monotonic()
    stopped = running.stop()
    elapsed = monotonic() - started

    assert elapsed < 1.0
    assert not stopped.success
    [final] = stopped.sidecar_outcomes
    assert final.state == pks.SidecarState.REAPED.value
    assert final.timeouts_total >= 1
    assert final.forced_kills_total == 1
    assert final.reaps_total == 1


def test_cancel_uses_cancel_protocol_and_reaps(tmp_path: Path) -> None:
    session = session_with_product_sources(tmp_path)
    session.register_sidecar(sidecar_spec("healthy"))
    running = session.start()

    cancelled = running.cancel()

    assert cancelled.success
    [final] = cancelled.sidecar_outcomes
    assert final.visited(pks.SidecarState.CANCELLING.value)
    assert final.visited(pks.SidecarState.REAPED.value)
    assert final.reaps_total == 1


def test_sidecar_handle_is_session_scoped(tmp_path: Path) -> None:
    first = session_with_product_sources(tmp_path / "first")
    second = session_with_product_sources(tmp_path / "second")
    handle = first.register_sidecar(sidecar_spec("healthy"))
    running = second.start()
    try:
        with pytest.raises(ValueError, match="different Session"):
            running.sidecar(handle)
    finally:
        running.stop()


def test_asyncio_sidecar_uses_same_native_owner(tmp_path: Path) -> None:
    async def scenario() -> None:
        if not hasattr(NativeSession, "conformance"):
            pytest.skip("native extension was not built with conformance-fixtures")
        session = aio.Session._from_native(NativeSession.conformance(tmp_path))
        audio = session.polled_audio()
        session.capture(pks.Source.application("PocketStation Python Fixture")).send(
            audio
        )
        session.capture(pks.Source.microphone_default()).send(audio)
        handle = session.register_sidecar(sidecar_spec("healthy"))

        running = await session.start()
        sidecar = running.sidecar(handle)
        await sidecar.send(message())
        received = await sidecar.messages.read(timeout_s=1.0)
        assert isinstance(received, pks.SidecarMessage)
        assert received.payload == b"hello"
        snapshot = await sidecar.snapshot()
        assert snapshot.data_received_total == 1
        cancelled = await running.cancel()
        [final] = cancelled.sidecar_outcomes
        assert final.reaps_total == 1

    asyncio.run(scenario())
