"""Native isolation with finite, deliberately blocking provider fixtures."""

from __future__ import annotations

import asyncio
import threading
from array import array

import pocketstation.aio as aio
import pytest
from pocketstation.graph import PortSpec, SignalSpec
from pocketstation.operator_authoring import (
    OperatorEmission,
    OperatorManifest,
    OperatorNode,
    OperatorProvider,
)

TEXT = SignalSpec.text()


class Factory:
    def __init__(self, node):
        self.node = node

    def create(self, configuration):
        return self.node


class Node(OperatorNode):
    def __init__(self, entered, release=None):
        self.entered = entered
        self.release = release
        self.calls = []
        self.active = False
        self.concurrent = False

    def process(self, port, envelope):
        self.concurrent |= self.active
        self.active = True
        self.calls.append("process")
        self.entered.set()
        if self.release is not None:
            if not self.release.wait(2):
                raise RuntimeError("bounded test release missing")
        self.active = False
        return (OperatorEmission.text("completed", signal=TEXT),)

    def cancel(self):
        self.concurrent |= self.active
        self.calls.append("cancel")

    def close(self):
        self.concurrent |= self.active
        self.calls.append("close")


@pytest.mark.asyncio
async def test_blocking_callback_does_not_stall_another_operator(tmp_path):
    session = aio.Session(recording_root=tmp_path)
    audio = session.audio_input("input", frame_samples_per_channel=480)
    release = threading.Event()
    entered = threading.Event()
    slow = Node(entered, release)
    fast = Node(threading.Event())
    subscriptions = []
    for name, node in [("slow", slow), ("fast", fast)]:
        manifest = OperatorManifest(
            "test.callback." + name,
            inputs=(PortSpec.input("audio", SignalSpec.audio()),),
            outputs=(PortSpec.output("text", TEXT),),
        )
        operator = session.register_operator(
            OperatorProvider.with_node(manifest, Factory(node))
        ).declare()
        audio.output.connect(operator.input("audio"))
        subscriptions.append(session.subscribe(operator.output("text"), signal=TEXT))
    running = await session.start()
    try:
        await audio.write(array("f", [0.1] * 480))
        assert await asyncio.to_thread(entered.wait, 1)
        # The slow callback is still blocked. Another Operator must be runnable.
        result = await running.signals(subscriptions[1]).read(timeout_s=0.25)
        assert result is not None and result.payload == "completed"
    finally:
        release.set()
        await audio.close()
        result = await running.stop()
    assert result.success
    assert not slow.concurrent and not fast.concurrent
    assert slow.calls[-1] == "close" and slow.calls.count("close") == 1


@pytest.mark.asyncio
async def test_timeout_never_overlaps_cancel_or_close_with_blocked_callback(tmp_path):
    entered, release, closed = threading.Event(), threading.Event(), threading.Event()

    class TimedNode(Node):
        def close(self):
            super().close()
            closed.set()

    node = TimedNode(entered, release)
    session = aio.Session(recording_root=tmp_path)
    audio = session.audio_input("input", frame_samples_per_channel=480)
    manifest = OperatorManifest(
        "test.callback.timeout",
        inputs=(PortSpec.input("audio", SignalSpec.audio()),),
        outputs=(PortSpec.output("text", TEXT),),
        process_timeout_ms=30,
    )
    operator = session.register_operator(
        OperatorProvider.with_node(manifest, Factory(node))
    ).declare()
    audio.output.connect(operator.input("audio"))
    session.subscribe(operator.output("text"), signal=TEXT)
    running = await session.start()
    try:
        await audio.write(array("f", [0.1] * 480))
        assert await asyncio.to_thread(entered.wait, 1)
        await asyncio.sleep(0.12)  # exceeds process + cancel deadlines, deliberately
        await audio.close()
        outcome = await running.stop()
        assert not outcome.success
        assert not node.concurrent
        assert "close" not in node.calls  # cannot claim cleanup before callback returns
    finally:
        release.set()
        await running.aclose()
    assert await asyncio.to_thread(closed.wait, 1)
    assert not node.concurrent
    assert node.calls[-1] == "close" and node.calls.count("close") == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("explicit_close", [False, True])
async def test_session_stop_retains_bounded_signals_until_read_or_explicit_close(
    tmp_path, explicit_close
):
    from pocketstation._api import EndOfStream

    class Tail(Node):
        def flush(self):
            return (OperatorEmission.text("tail", signal=TEXT),)

    entered = threading.Event()
    node = Tail(entered)
    session = aio.Session(recording_root=tmp_path)
    audio = session.audio_input("input", frame_samples_per_channel=480)
    operator = session.register_operator(
        OperatorProvider.with_node(
            OperatorManifest(
                "test.receipt.tail",
                inputs=(PortSpec.input("audio", SignalSpec.audio()),),
                outputs=(PortSpec.output("text", TEXT),),
            ),
            Factory(node),
        )
    ).declare()
    audio.output.connect(operator.input("audio"))
    subscription = session.subscribe(operator.output("text"), signal=TEXT)
    running = await session.start()
    stream = running.signals(subscription)
    await audio.write(array("f", [0.1] * 480))
    assert await asyncio.to_thread(entered.wait, 1)
    await audio.close()
    outcome = await running.stop()
    assert outcome.success
    if explicit_close:
        await stream.aclose()
    values = []
    while True:
        item = await stream.read(timeout_s=1)
        if isinstance(item, EndOfStream):
            break
        assert item is not None
        values.append(item.payload)
    assert values == ([] if explicit_close else ["completed", "tail"])
