from __future__ import annotations

import inspect
import sys
import threading
from collections.abc import Sequence
from dataclasses import FrozenInstanceError

import pocketstation as pks
import pocketstation._native as native
import pocketstation.aio as aio
import pocketstation.aio.sources as aio_sources
import pytest
from pocketstation.errors import CaptureError, SessionDeclarationError
from pocketstation.graph import SourceOutput
from pocketstation.sources import (
    ObservedProcessInstance,
    Platform,
    SourceKind,
    StableSourceId,
    _native_process_set_members,
)

MAX_U64 = (1 << 64) - 1


def member(
    process_id: int = 42,
    start_ns: int = MAX_U64,
    *,
    platform: Platform = Platform.MACOS,
    key: str = "fixture-identity",
) -> ObservedProcessInstance:
    return ObservedProcessInstance(
        process_id,
        StableSourceId(platform, SourceKind.APPLICATION, key, None),
        start_ns,
    )


@pytest.mark.parametrize("value", [False, True, 0, -1, 1.0, "1", 1 << 31, 1 << 32])
def test_given_invalid_process_id_when_observed_then_rejects_input(
    value: object,
) -> None:
    with pytest.raises(SessionDeclarationError) as failure:
        member(value)  # type: ignore[arg-type]
    assert failure.value.code == "session.invalid_process_set"


@pytest.mark.parametrize("value", [False, True, 0, -1, 1.0, "1", 1 << 64])
def test_given_invalid_start_time_when_observed_then_rejects_input(
    value: object,
) -> None:
    with pytest.raises(SessionDeclarationError) as failure:
        member(start_ns=value)  # type: ignore[arg-type]
    assert failure.value.code == "session.invalid_process_set"


@pytest.mark.parametrize(
    "identity",
    [
        None,
        StableSourceId(Platform.MACOS, SourceKind.INPUT_DEVICE, "mic", None),
        StableSourceId(Platform.MACOS, SourceKind.APPLICATION, " ", None),
        StableSourceId("macos", SourceKind.APPLICATION, "app", None),
    ],
)
def test_given_invalid_identity_when_observed_then_rejects_input(
    identity: object,
) -> None:
    with pytest.raises(SessionDeclarationError) as failure:
        ObservedProcessInstance(42, identity, 123)  # type: ignore[arg-type]
    assert failure.value.code == "session.invalid_process_set"


def test_given_identity_when_observed_then_copies_frozen_values() -> None:
    identity = StableSourceId(Platform.MACOS, SourceKind.APPLICATION, "app", None)
    observed = ObservedProcessInstance(42, identity, MAX_U64)
    assert observed.stable_id == identity
    assert observed.stable_id is not identity
    assert observed.process_start_time_ns == MAX_U64
    with pytest.raises(FrozenInstanceError):
        observed.process_id = 43  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        observed.stable_id.stable_key = "changed"  # type: ignore[misc]


def test_given_mutable_identity_subclass_when_observed_then_freezes_base_copy() -> None:
    class MutableIdentity(StableSourceId):
        def __setattr__(self, name: str, value: object) -> None:
            object.__setattr__(self, name, value)

    identity = MutableIdentity(Platform.MACOS, SourceKind.APPLICATION, "app", None)
    observed = ObservedProcessInstance(42, identity, MAX_U64)
    identity.stable_key = "changed"
    assert type(observed.stable_id) is StableSourceId
    assert observed.stable_id.stable_key == "app"
    with pytest.raises(FrozenInstanceError):
        observed.stable_id.stable_key = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("value", [[], True, False, 0, -1, 1.0, "1", 1 << 64])
def test_given_invalid_optional_source_id_when_observed_then_rejects_input(
    value: object,
) -> None:
    identity = StableSourceId(Platform.MACOS, SourceKind.APPLICATION, "app", value)  # type: ignore[arg-type]
    with pytest.raises(SessionDeclarationError) as failure:
        ObservedProcessInstance(42, identity, MAX_U64)
    assert failure.value.code == "session.invalid_process_set"


@pytest.mark.parametrize(
    "selected",
    [
        [],
        [member(i + 1) for i in range(33)],
        [member(), member()],
        [member(), member(start_ns=1, key="other")],
        [member(), member(43, platform=Platform.LINUX)],
        [None],
        (item for item in ()),
    ],
)
def test_given_invalid_selection_when_declared_then_rejects_before_native_work(
    selected: object,
) -> None:
    with pytest.raises(SessionDeclarationError) as failure:
        _native_process_set_members(selected)  # type: ignore[arg-type]
    assert failure.value.code == "session.invalid_process_set"


def test_given_modified_observation_when_declared_then_revalidates_input() -> None:
    selected = member()
    object.__setattr__(selected, "stable_id", None)
    with pytest.raises(SessionDeclarationError) as failure:
        _native_process_set_members([selected])
    assert failure.value.code == "session.invalid_process_set"


def test_given_legacy_native_when_discovering_then_reports_unsupported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delattr(native, "discover_process_instances", raising=False)
    with pytest.raises(CaptureError) as failure:
        pks.discover_process_instances()
    assert failure.value.code == "capture.unsupported"
    assert callable(pks.discover_sources)


def test_given_legacy_native_when_declaring_then_reports_unsupported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delattr(native, "ObservedProcessInstance", raising=False)
    with pytest.raises(CaptureError) as failure:
        pks.Session(channels=2).capture_process_set([member()])
    assert failure.value.code == "capture.unsupported"


@pytest.mark.asyncio
async def test_given_async_discovery_when_awaited_then_runs_shared_policy_off_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event_loop_thread = threading.get_ident()
    selected = (member(),)

    def discover() -> tuple[ObservedProcessInstance, ...]:
        assert threading.get_ident() != event_loop_thread
        return selected

    monkeypatch.setattr(aio_sources, "_discover_process_instances", discover)
    assert await aio.discover_process_instances() is selected
    assert not inspect.iscoroutinefunction(aio.Session.capture_process_set)


def test_given_native_observation_when_projected_then_preserves_frozen_u64() -> None:
    observed = native.ObservedProcessInstance(42, "macos", "app", MAX_U64)
    assert observed.process_id == 42
    assert observed.process_start_time_ns == MAX_U64
    assert type(observed.process_start_time_ns) is int
    assert observed.kind == "application"
    projected = ObservedProcessInstance._from_native(observed)
    assert projected.stable_id.source_id == observed.source_id
    assert projected.stable_id.stable_key == "app"
    assert projected.process_start_time_ns == MAX_U64
    with pytest.raises(AttributeError):
        observed.process_start_time_ns = 1


@pytest.mark.parametrize("value", [False, True, 0, -1, 1.0, "1", 1 << 31])
def test_given_native_invalid_process_id_when_constructed_then_rejects_input(
    value: object,
) -> None:
    with pytest.raises(ValueError, match=r"\[session.invalid_process_set\]"):
        native.ObservedProcessInstance(value, "macos", "app", 123)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [False, True, 0, -1, 1.0, "1", 1 << 64])
def test_given_native_invalid_start_time_when_constructed_then_rejects_input(
    value: object,
) -> None:
    with pytest.raises(ValueError, match=r"\[session.invalid_process_set\]"):
        native.ObservedProcessInstance(42, "macos", "app", value)  # type: ignore[arg-type]


def test_given_native_selection_when_copied_then_freezes_canonical_snapshot() -> None:
    original = [member(43, 11), member(42, MAX_U64)]
    selected = _native_process_set_members(original)
    original.clear()
    assert [item.process_id for item in selected] == [42, 43]
    assert [item.process_start_time_ns for item in selected] == [MAX_U64, 11]


def test_given_native_changing_length_when_copied_then_reads_validated_count() -> None:
    class ChangingLength(Sequence[ObservedProcessInstance]):
        length_reads = 0
        item_reads = 0

        def __len__(self) -> int:
            self.length_reads += 1
            return 1 if self.length_reads == 1 else 1_000_000_000

        def __getitem__(self, index: int) -> ObservedProcessInstance:
            assert index == 0
            self.item_reads += 1
            return member()

    selection = ChangingLength()
    selected = _native_process_set_members(selection)
    assert selection.length_reads == 1
    assert selection.item_reads == 1
    assert len(selected) == 1


def test_given_native_discovery_when_projected_then_preserves_frozen_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed = native.ObservedProcessInstance(42, "macos", "app", MAX_U64)
    monkeypatch.setattr(native, "discover_process_instances", lambda: [observed])
    assert pks.discover_process_instances() == (
        ObservedProcessInstance._from_native(observed),
    )


@pytest.mark.parametrize("session_type", [pks.Session, aio.Session])
def test_given_native_selection_when_declared_then_returns_routable_output(
    session_type: type,
) -> None:
    session = session_type(channels=2)
    if sys.platform != "darwin":
        with pytest.raises(CaptureError) as failure:
            session.capture_process_set([member()])
        assert failure.value.code == "capture.unsupported"
        return
    output = session.capture_process_set([member(43, 12), member(42, MAX_U64)])
    assert isinstance(output, SourceOutput)
    assert output.session_id == session.id
    assert output.output_port == "audio"
    assert int(output.source_id) > 0
    assert int(output.stream_id) > 0
    output.send(session.polled_audio())
    other = session_type(channels=2)
    with pytest.raises(SessionDeclarationError) as failure:
        output.send(other.polled_audio())
    assert failure.value.code == "session.foreign_endpoint"


def test_given_native_invalid_set_when_declared_then_rejects_without_capture() -> None:
    observed = native.ObservedProcessInstance(42, "macos", "app", MAX_U64)
    session = native.Session(channels=2)
    for selected in ([], [observed, observed], [observed] * 33):
        with pytest.raises(ValueError, match=r"\[session.invalid_process_set\]"):
            session.capture_process_set(selected)


def test_given_native_started_session_when_declared_then_preserves_frozen_error() -> (
    None
):
    session = pks.Session(channels=2)
    generated = session.audio_input("no-device-input")
    generated.output.send(session.polled_audio())
    with session.start():
        with pytest.raises(SessionDeclarationError) as failure:
            session.capture_process_set([member()])
        assert failure.value.code == "session.draft_frozen"
