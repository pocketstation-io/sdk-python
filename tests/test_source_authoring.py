from __future__ import annotations

import asyncio
from collections import deque
from threading import Event
from typing import cast

import pocketstation.aio._api as pks_aio
import pytest
from pocketstation._api import (
    MediaCaps,
    Multiplicity,
    PortDirection,
    PortSpec,
    Session,
    SignalEnvelope,
    SignalSpec,
    SourceCancellation,
    SourceConfiguration,
    SourceDriver,
    SourceEmission,
    SourceManifest,
    SourcePrepareContext,
    SourceProvider,
    TextFormat,
    source,
)
from pocketstation.streams import STREAM_EOF


def text_manifest(source_type_id: str) -> SourceManifest:
    signal = SignalSpec.text(TextFormat.UTF8, role="transcript")
    return SourceManifest(
        source_type_id,
        outputs=(
            PortSpec(
                "events",
                PortDirection.OUTPUT,
                signal,
                MediaCaps.text(),
                Multiplicity.MANY,
            ),
        ),
    )


@pytest.mark.parametrize("field", ["create_s", "prepare_s", "next_s", "close_s"])
@pytest.mark.parametrize("value", [True, "1.0", None])
def test_async_source_deadlines_reject_non_numbers(field: str, value: object) -> None:
    with pytest.raises(TypeError, match=rf"{field} must be a number"):
        pks_aio.SourceDeadlines(**{field: value})


@pytest.mark.parametrize("field", ["create_s", "prepare_s", "next_s", "close_s"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_async_source_deadlines_reject_non_finite_numbers(
    field: str, value: float
) -> None:
    with pytest.raises(ValueError, match=rf"{field} must be greater"):
        pks_aio.SourceDeadlines(**{field: value})


def test_iterable_source_runs_in_core_and_receives_session_lineage() -> None:
    signal = SignalSpec.text(TextFormat.UTF8, role="transcript")

    @source(text_manifest("io.pocketstation.source.python-test.v1"))
    def transcript(configuration):
        yield SourceEmission.text(
            "events",
            configuration["text"],
            signal=signal,
            source_timestamp_ns=10,
            observed_timestamp_ns=12,
            duration_ns=5,
            discontinuity_epoch=2,
            terminal=True,
        )

    session = Session()
    registered = session.register_source(transcript)
    instance = registered.declare(SourceConfiguration({"text": "hello"}))
    output = instance.output("events")
    subscription = session.subscribe(output, signal=signal)
    session_id = session.id

    with session.start() as running:
        value = running.signals(subscription).read(timeout_s=1.0)

    assert isinstance(value, SignalEnvelope)
    assert value.payload == "hello"
    assert value.lineage is not None
    assert value.lineage.session_id == session_id
    assert value.lineage.source_id == instance.source_id
    assert value.lineage.stream_id == output.stream_id
    assert value.lineage.sequence_number == 0
    assert value.lineage.discontinuity_epoch == 2
    assert value.timing.source_timestamp_ns == 10
    assert value.timing.observed_timestamp_ns == 12
    assert value.timing.duration_ns == 5


@pytest.mark.parametrize("cleanup_fails", [False, True])
def test_retained_generator_closes_on_early_session_stop(
    cleanup_fails: bool,
) -> None:
    signal = SignalSpec.text(role="transcript")
    closed: list[bool] = []

    def values():
        try:
            yield SourceEmission.text("events", "last", signal=signal)
            pytest.fail("closing the source must not advance its generator")
        finally:
            closed.append(True)
            if cleanup_fails:
                raise RuntimeError("retained generator cleanup failed")

    from pocketstation.source_authoring import _IterableDriver

    retained = values()
    entered = Event()

    class PausedIterator(_IterableDriver):
        sent = False

        def next(self, cancellation):
            if not self.sent:
                self.sent = True
                return super().next(cancellation)
            entered.set()
            while not cancellation.cancelled:
                Event().wait(0.001)
            return None

    provider = SourceProvider.with_driver(
        text_manifest("io.pocketstation.source.retained-sync.v1"),
        FactoryWithoutValidator(PausedIterator(retained)),
    )
    session = Session()
    output = session.register_source(provider).declare().output("events")
    subscription = session.subscribe(output, signal=signal)
    running = session.start()
    assert running.signals(subscription).read(timeout_s=1).payload == "last"
    assert entered.wait(1)
    result = running.stop()
    assert result.success is not cleanup_fails
    assert closed == [True]
    assert retained.gi_frame is None
    if cleanup_fails:
        assert result.terminal_event.terminal_state.value == "failed"
        assert "retained generator cleanup failed" in str(
            result.terminal_event.failures
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("cleanup_fails", [False, True])
async def test_retained_async_generator_awaits_close_on_early_session_stop(
    cleanup_fails: bool,
) -> None:
    signal = SignalSpec.text(role="transcript")
    closed: list[bool] = []

    async def values():
        try:
            yield SourceEmission.text("events", "last", signal=signal)
            pytest.fail("closing the source must not advance its async generator")
        finally:
            await asyncio.sleep(0)
            closed.append(True)
            if cleanup_fails:
                raise RuntimeError("retained async generator cleanup failed")

    from pocketstation.aio.source_authoring import _AsyncIteratorDriver

    retained = values()
    entered = asyncio.Event()

    class PausedIterator(_AsyncIteratorDriver):
        sent = False

        async def next(self, cancellation):
            if not self.sent:
                self.sent = True
                return await super().next(cancellation)
            entered.set()
            await asyncio.Event().wait()
            return None

    async def create(_configuration):
        return PausedIterator(retained)

    provider = pks_aio.SourceProvider.with_driver(
        text_manifest("io.pocketstation.source.retained-async.v1"), create
    )
    session = pks_aio.Session()
    output = session.register_source(provider).declare().output("events")
    subscription = session.subscribe(output, signal=signal)
    running = await session.start()
    value = await running.signals(subscription).read(timeout_s=1)
    assert value.payload == "last"
    await asyncio.wait_for(entered.wait(), 1)
    result = await running.stop()
    assert result.success is not cleanup_fails
    assert closed == [True]
    assert retained.ag_frame is None
    if cleanup_fails:
        assert result.terminal_event.terminal_state.value == "failed"
        assert "retained async generator cleanup failed" in str(
            result.terminal_event.failures
        )


class RecordingDriver(SourceDriver):
    def __init__(self, signal: SignalSpec) -> None:
        self.signal = signal
        self.prepared: SourcePrepareContext | None = None
        self.closed = Event()
        self.sent = False

    def prepare(self, context: SourcePrepareContext) -> None:
        self.prepared = context

    def next(self, cancellation: SourceCancellation) -> SourceEmission | None:
        assert not cancellation.cancelled
        if self.sent:
            return None
        self.sent = True
        return SourceEmission.text("events", "ready", signal=self.signal)

    def close(self) -> None:
        self.closed.set()


class RecordingFactory:
    def __init__(self, driver: RecordingDriver) -> None:
        self.driver = driver
        self.configurations: list[dict[str, str]] = []

    def validate_config(self, configuration) -> None:
        if configuration.get("mode") != "strict":
            raise ValueError("mode must be strict")

    def create(self, configuration) -> RecordingDriver:
        self.configurations.append(dict(configuration))
        return self.driver


class FactoryWithoutValidator:
    def __init__(self, driver: SourceDriver) -> None:
        self.driver = driver

    def create(self, _configuration) -> SourceDriver:
        return self.driver


def test_driver_source_preparation_validation_and_exact_close() -> None:
    signal = SignalSpec.text()
    driver = RecordingDriver(signal)
    provider = SourceProvider.with_driver(
        text_manifest("io.pocketstation.source.python-driver-test.v1"),
        RecordingFactory(driver),
    )
    session = Session()
    registered = session.register_source(provider)

    instance = registered.declare(SourceConfiguration({"mode": "strict"}))
    subscription = session.subscribe(instance.output("events"), signal=signal)
    session_id = session.id
    with session.start() as running:
        value = running.signals(subscription).read(timeout_s=1.0)
        assert isinstance(value, SignalEnvelope)

    assert driver.prepared is not None
    assert driver.prepared.session_id == session_id
    assert driver.prepared.source_id == instance.source_id
    assert driver.prepared.outputs[0].output_port == "events"
    assert driver.closed.wait(1.0)


def test_source_factory_does_not_require_a_noop_validator() -> None:
    signal = SignalSpec.text()
    driver = RecordingDriver(signal)
    session = Session()
    instance = session.register_source(
        SourceProvider.with_driver(
            text_manifest("io.pocketstation.source.no-validator-test.v1"),
            FactoryWithoutValidator(driver),
        )
    ).declare()
    subscription = session.subscribe(instance.output("events"), signal=signal)

    with session.start() as running:
        assert isinstance(
            running.signals(subscription).read(timeout_s=1.0), SignalEnvelope
        )

    assert driver.closed.wait(1.0)


def test_source_manifest_rejects_pcm_and_points_to_audio_input() -> None:
    with pytest.raises(Exception, match=r"Session\.audio_input"):
        SourceManifest(
            "io.pocketstation.source.invalid-audio-test.v1",
            outputs=(
                PortSpec(
                    "audio",
                    PortDirection.OUTPUT,
                    SignalSpec.audio(),
                    MediaCaps.audio(),
                ),
            ),
        )


@pytest.mark.parametrize("discard", [False, True])
def test_final_source_signal_precedes_eof_and_explicit_close_discards(discard) -> None:
    signal = SignalSpec.text(TextFormat.UTF8, role="transcript")

    @source(text_manifest("io.pocketstation.source.final-signal.v1"))
    def accepted(_configuration):
        for text in ("first", "middle", "final"):
            yield SourceEmission.text("events", text, signal=signal)

    session = Session()
    output = session.register_source(accepted).declare().output("events")
    subscription = session.subscribe(output, signal=signal)
    running = session.start()
    stream = running.signals(subscription)
    try:
        first = stream.read(timeout_s=1)
        assert first.payload == "first"
        if discard:
            stream.close()
            assert stream.poll() is STREAM_EOF
        else:
            assert stream.read(timeout_s=1).payload == "middle"
            final = stream.read(timeout_s=1)
            assert final.payload == "final"
            assert final.lineage.stream_id == output.stream_id
            assert final.lineage.sequence_number == 2
            assert stream.read(timeout_s=1) is STREAM_EOF
            assert stream.poll() is STREAM_EOF
    finally:
        assert running.stop().success


@pytest.mark.parametrize("operation", ["cancel", "close"])
@pytest.mark.parametrize("read_before_discard", [False, True])
def test_cancel_after_stop_discards_unread_signal_receipt(
    operation,
    read_before_discard,
) -> None:
    driver = BufferedDriver()
    session = Session()
    output = (
        session.register_source(
            SourceProvider.with_driver(
                text_manifest("io.pocketstation.source.cancel-receipt.v1"),
                FactoryWithoutValidator(driver),
            )
        )
        .declare()
        .output("events")
    )
    subscription = session.subscribe(output, signal=driver.signal)
    running = session.start()
    if read_before_discard:
        running.signals(subscription)
    assert driver.next_entered.wait(1)
    assert running.stop().success
    assert driver.drain_calls == 4

    getattr(running, operation)()

    assert running.signals(subscription).poll() is STREAM_EOF
    assert running._native.poll_signal(subscription._native).status == "closed"


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["cancel", "aclose"])
@pytest.mark.parametrize("read_before_discard", [False, True])
async def test_async_cancel_after_stop_discards_every_native_signal_receipt(
    operation,
    read_before_discard,
) -> None:
    driver = BufferedDriver()
    entered = asyncio.Event()

    class AsyncDriver(pks_aio.SourceDriver):
        async def next(self, cancellation):
            entered.set()
            await asyncio.Event().wait()

        async def drain(self):
            return driver.drain()

    async def create(_configuration):
        return AsyncDriver()

    session = pks_aio.Session()
    output = (
        session.register_source(
            pks_aio.SourceProvider.with_driver(
                text_manifest("io.pocketstation.source.async-cancel-receipt.v1"), create
            )
        )
        .declare()
        .output("events")
    )
    subscription = session.subscribe(output, signal=driver.signal)
    running = await session.start()
    if read_before_discard:
        running.signals(subscription)
    await asyncio.wait_for(entered.wait(), 1)
    assert (await running.stop()).success
    assert driver.drain_calls == 4

    await getattr(running, operation)()

    assert await running.signals(subscription).poll() is STREAM_EOF
    assert running._native.poll_signal(subscription._native).status == "closed"


@pytest.mark.asyncio
async def test_async_iterable_source_runs_on_the_owning_event_loop() -> None:
    signal = SignalSpec.text(role="async-source")
    manifest = SourceManifest(
        "io.pocketstation.source.python-async-test.v1",
        outputs=(
            PortSpec(
                "events",
                PortDirection.OUTPUT,
                signal,
                MediaCaps.text(),
            ),
        ),
    )

    @pks_aio.source(manifest)
    async def events(_configuration):
        yield SourceEmission.text("events", "async", signal=signal)

    session = pks_aio.Session()
    registered = session.register_source(events)
    instance = registered.declare()
    subscription = session.subscribe(instance.output("events"), signal=signal)

    async with await session.start() as running:
        value = await running.signals(subscription).read(timeout_s=1.0)

    assert isinstance(value, SignalEnvelope)
    assert value.payload == "async"
    assert value.lineage is not None


class BufferedDriver(SourceDriver):
    """Three accepted events, with live acquisition blocked until interruption."""

    def __init__(self, *, failure: str | None = None) -> None:
        self.signal = SignalSpec.text(TextFormat.UTF8, role="transcript")
        self.pending = deque(
            SourceEmission.text("events", text, signal=self.signal)
            for text in ("first", "second", "third")
        )
        self.failure = failure
        self.next_entered = Event()
        self.drain_calls = 0
        self.close_calls = 0

    def next(self, cancellation: SourceCancellation) -> None:
        self.next_entered.set()
        interrupted = Event()
        while not cancellation.cancelled:
            interrupted.wait(0.001)

    def drain(self) -> SourceEmission | None:
        self.drain_calls += 1
        if self.failure == "drain":
            raise RuntimeError("accepted input drain failed")
        return self.pending.popleft() if self.pending else None

    def close(self) -> None:
        self.close_calls += 1
        if self.failure == "close":
            raise RuntimeError("source close failed")


@pytest.mark.parametrize("cancel", [False, True])
def test_buffered_source_drains_accepted_events_only_on_graceful_stop(cancel) -> None:
    driver = BufferedDriver()
    session = Session()
    instance = session.register_source(
        SourceProvider.with_driver(
            text_manifest("io.pocketstation.source.buffered-stop.v1"),
            FactoryWithoutValidator(driver),
        )
    ).declare()
    output = instance.output("events")
    subscription = session.subscribe(output, signal=driver.signal)
    running = session.start()
    stream = running.signals(subscription)
    assert driver.next_entered.wait(1.0)

    result = running.cancel() if cancel else running.stop()

    assert result.success
    assert driver.close_calls == 1
    assert driver.drain_calls == (0 if cancel else 4)
    if cancel:
        assert len(driver.pending) == 3
    else:
        values = [stream.read(timeout_s=0) for _ in range(3)]
        assert [value.payload for value in values] == ["first", "second", "third"]
        for sequence, value in enumerate(values):
            assert value.lineage.source_id == instance.source_id
            assert value.lineage.stream_id == output.stream_id
            assert value.lineage.sequence_number == sequence
        assert stream.poll() is STREAM_EOF


@pytest.mark.parametrize("failure", ["drain", "close"])
def test_source_finalization_failures_reach_stop_and_terminal_event(failure) -> None:
    driver = BufferedDriver(failure=failure)
    session = Session()
    output = (
        session.register_source(
            SourceProvider.with_driver(
                text_manifest("io.pocketstation.source.finalization-failure.v1"),
                FactoryWithoutValidator(driver),
            )
        )
        .declare()
        .output("events")
    )
    session.subscribe(output, signal=driver.signal)
    running = session.start()
    assert driver.next_entered.wait(1.0)

    result = running.stop()

    assert not result.success
    assert result.runtime_failures_total == 1
    assert result.terminal_event is not None
    assert result.terminal_event.terminal_state.value == "failed"
    assert result.terminal_event.failures_total == 1
    assert driver.close_calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
@pytest.mark.parametrize("failure", [None, "drain", "close"])
async def test_async_source_interrupts_pending_next_and_drains_without_cancellation(
    cancel,
    failure,
) -> None:
    driver = BufferedDriver(failure=failure)
    entered = asyncio.Event()

    class AsyncBufferedDriver(pks_aio.SourceDriver):
        async def next(self, cancellation):
            entered.set()
            await asyncio.Event().wait()

        async def drain(self):
            return driver.drain()

        async def close(self):
            driver.close()

    async def create(_configuration):
        return AsyncBufferedDriver()

    session = pks_aio.Session()
    instance = session.register_source(
        pks_aio.SourceProvider.with_driver(
            text_manifest("io.pocketstation.source.async-buffered-stop.v1"), create
        )
    ).declare()
    output = instance.output("events")
    subscription = session.subscribe(output, signal=driver.signal)
    running = await session.start()
    stream = running.signals(subscription)
    await asyncio.wait_for(entered.wait(), 1.0)

    result = await asyncio.wait_for(running.cancel() if cancel else running.stop(), 2.0)

    failed = failure == "close" or (failure == "drain" and not cancel)
    assert result.success is not failed
    if failed:
        assert result.runtime_failures_total == 1
        assert result.terminal_event.terminal_state.value == "failed"
        assert result.terminal_event.failures_total == 1
    assert driver.close_calls == 1
    assert driver.drain_calls == (0 if cancel else 1 if failure == "drain" else 4)
    if not cancel and failure != "drain":
        values = [await stream.read(timeout_s=0) for _ in range(3)]
        assert [value.payload for value in values] == ["first", "second", "third"]
        for sequence, value in enumerate(values):
            assert value.lineage.source_id == instance.source_id
            assert value.lineage.stream_id == output.stream_id
            assert value.lineage.sequence_number == sequence
        assert await stream.poll() is STREAM_EOF


def test_sync_drain_is_optional_and_never_advances_an_iterable() -> None:
    from pocketstation.source_authoring import _IterableDriver, _NativeDriverAdapter

    class LegacyDriver:
        pass

    assert _NativeDriverAdapter(cast(SourceDriver, LegacyDriver())).drain() is None
    advanced = []

    def values():
        advanced.append(True)
        yield SourceEmission.text("events", "unexpected", signal=SignalSpec.text())

    assert _NativeDriverAdapter(_IterableDriver(values())).drain() is None
    assert advanced == []


@pytest.mark.asyncio
async def test_async_drain_is_optional_bounded_and_never_advances_an_iterable() -> None:
    from pocketstation.aio.source_authoring import _AsyncIteratorDriver, _DriverAdapter

    loop = asyncio.get_running_loop()
    deadlines = pks_aio.SourceDeadlines(close_s=0.01)

    class LegacyDriver:
        pass

    adapter = _DriverAdapter(
        cast(pks_aio.SourceDriver, LegacyDriver()), loop, deadlines
    )
    assert await asyncio.to_thread(adapter.drain) is None
    advanced = []

    async def values():
        advanced.append(True)
        yield SourceEmission.text("events", "unexpected", signal=SignalSpec.text())

    adapter = _DriverAdapter(_AsyncIteratorDriver(values()), loop, deadlines)
    assert await asyncio.to_thread(adapter.drain) is None
    assert advanced == []

    class BlockedDrain(pks_aio.SourceDriver):
        async def drain(self):
            await asyncio.Event().wait()

    adapter = _DriverAdapter(BlockedDrain(), loop, deadlines)
    with pytest.raises(TimeoutError, match="Source operation exceeded"):
        await asyncio.to_thread(adapter.drain)


@pytest.mark.asyncio
async def test_async_next_provider_cancellation_remains_an_error() -> None:
    from pocketstation.aio.source_authoring import _DriverAdapter

    class CancelledProvider(pks_aio.SourceDriver):
        async def next(self, cancellation):
            raise asyncio.CancelledError("provider independently cancelled")

    class NotCancelled:
        cancelled = False

    adapter = _DriverAdapter(
        CancelledProvider(), asyncio.get_running_loop(), pks_aio.SourceDeadlines()
    )
    with pytest.raises(asyncio.CancelledError):
        await asyncio.to_thread(adapter.next, cast(SourceCancellation, NotCancelled()))


@pytest.mark.asyncio
async def test_async_next_cancellation_cleanup_finishes_before_drain() -> None:
    from pocketstation.aio.source_authoring import _DriverAdapter

    entered = asyncio.Event()
    cleanup_entered = asyncio.Event()
    release_cleanup = asyncio.Event()
    cleanup_finished = asyncio.Event()

    class Interruption:
        cancelled = False

    cancellation = Interruption()

    class Driver(pks_aio.SourceDriver):
        async def next(self, cancellation):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleanup_entered.set()
                await release_cleanup.wait()
                cleanup_finished.set()

        async def drain(self):
            assert cleanup_finished.is_set(), "drain overlapped next cleanup"

    adapter = _DriverAdapter(
        Driver(), asyncio.get_running_loop(), pks_aio.SourceDeadlines(next_s=1)
    )

    def worker():
        assert adapter.next(cast(SourceCancellation, cancellation)) is None
        return adapter.drain()

    work = asyncio.create_task(asyncio.to_thread(worker))
    try:
        await asyncio.wait_for(entered.wait(), 1)
        cancellation.cancelled = True
        await asyncio.wait_for(cleanup_entered.wait(), 1)
        # The release barrier deliberately keeps next alive. Drain must not run.
        with pytest.raises(TimeoutError):
            await asyncio.wait_for(asyncio.shield(work), 0.05)
    finally:
        release_cleanup.set()
    assert await asyncio.wait_for(work, 1) is None


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [RuntimeError, TimeoutError])
async def test_async_next_cancellation_cleanup_error_remains_a_failure(
    error_type,
) -> None:
    from pocketstation.aio.source_authoring import _DriverAdapter

    entered = asyncio.Event()

    class Interruption:
        cancelled = False

    cancellation = Interruption()

    class Driver(pks_aio.SourceDriver):
        async def next(self, cancellation):
            entered.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError as error:
                raise error_type("provider cleanup failed") from error

    adapter = _DriverAdapter(
        Driver(), asyncio.get_running_loop(), pks_aio.SourceDeadlines(next_s=1)
    )
    work = asyncio.create_task(
        asyncio.to_thread(adapter.next, cast(SourceCancellation, cancellation))
    )
    await asyncio.wait_for(entered.wait(), 1)
    cancellation.cancelled = True
    with pytest.raises(error_type, match="provider cleanup failed"):
        await asyncio.wait_for(work, 1)


@pytest.mark.asyncio
@pytest.mark.parametrize("requested_interruption", [False, True])
async def test_async_source_deadline_refuses_close_until_callback_cleanup_finishes(
    requested_interruption,
) -> None:
    from pocketstation.aio.source_authoring import _DriverAdapter

    entered = asyncio.Event()
    cleanup_entered = asyncio.Event()
    release_cleanup = asyncio.Event()
    closed = []

    class Interruption:
        cancelled = False

    cancellation = Interruption()

    class Driver(pks_aio.SourceDriver):
        async def next(self, cancellation):
            entered.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleanup_entered.set()
                await release_cleanup.wait()

        async def close(self):
            closed.append(True)

    adapter = _DriverAdapter(
        Driver(), asyncio.get_running_loop(), pks_aio.SourceDeadlines(next_s=0.1)
    )
    work = asyncio.create_task(
        asyncio.to_thread(adapter.next, cast(SourceCancellation, cancellation))
    )
    try:
        await asyncio.wait_for(entered.wait(), 1)
        cancellation.cancelled = requested_interruption
        with pytest.raises(TimeoutError, match="cleanup may be incomplete"):
            await asyncio.wait_for(work, 1)
        await asyncio.wait_for(cleanup_entered.wait(), 1)
        with pytest.raises(
            RuntimeError, match="previous operation cleanup is incomplete"
        ):
            await asyncio.to_thread(adapter.close)
        assert closed == []
    finally:
        release_cleanup.set()
        if adapter._operation.result is not None:
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wrap_future(adapter._operation.result)

    await asyncio.to_thread(adapter.close)
    assert closed == [True]
