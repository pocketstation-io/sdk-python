from __future__ import annotations

from array import array
from dataclasses import FrozenInstanceError, replace
from types import SimpleNamespace

import pytest
from pocketstation._api import (
    ApplicationPolicyObservation,
    AudioInputBufferError,
    AudioInputClosedError,
    AudioInputConfig,
    AudioInputFullError,
    CaptureCapabilityState,
    CaptureOpenOutcome,
    CaptureScopeKind,
    CaptureSessionGrant,
    DiscoveredSource,
    PermissionObservation,
    Platform,
    PocketStationError,
    ProcessTreeScope,
    SelectorPersistenceScope,
    Session,
    Source,
    SourceIdentityStrength,
    SourceKind,
    SourceSelectorKind,
    SourceState,
    StableSourceId,
)


def _discovered(kind: SourceKind) -> DiscoveredSource:
    return DiscoveredSource(
        stable_id=StableSourceId(
            platform=Platform.MACOS,
            kind=kind,
            stable_key=f"fixture:{kind.value}",
            source_id=42,
        ),
        name="Fixture",
        process_id=123 if kind is SourceKind.APPLICATION else None,
        application_id="io.pocketstation.fixture"
        if kind is SourceKind.APPLICATION
        else None,
        device_uid="device-42" if kind is SourceKind.INPUT_DEVICE else None,
        state=SourceState.AVAILABLE,
        sample_rate_hz=48_000,
        channel_count=2,
        identity_strength=SourceIdentityStrength.PLATFORM_STABLE_ID,
        selector_persistence_scope=SelectorPersistenceScope.PLATFORM_IDENTITY,
        process_tree_scope=ProcessTreeScope.NOT_APPLICABLE,
    )


def test_source_declarations_are_immutable_and_descriptive() -> None:
    application = Source.application("PocketStation Fixture")
    microphone = Source.microphone_default()

    assert application.kind is SourceKind.APPLICATION
    assert application.selector_kind is SourceSelectorKind.APPLICATION_NAME
    assert application.selector_value == "PocketStation Fixture"
    assert microphone.kind is SourceKind.INPUT_DEVICE
    assert microphone.selector_kind is SourceSelectorKind.MICROPHONE_DEFAULT
    with pytest.raises(FrozenInstanceError):
        application.selector_value = "changed"


def test_discovered_application_uses_exact_process_and_stable_identity() -> None:
    selected = Source.from_discovered(_discovered(SourceKind.APPLICATION))

    assert selected.selector_kind is SourceSelectorKind.APPLICATION_PROCESS_INSTANCE
    assert selected.kind is SourceKind.APPLICATION


def test_discovered_input_device_lowers_to_microphone_id() -> None:
    selected = Source.from_discovered(_discovered(SourceKind.INPUT_DEVICE))

    assert selected.selector_kind is SourceSelectorKind.MICROPHONE_ID
    assert selected.selector_value == "device-42"


def test_discovered_source_projects_typed_pre_open_authorization_evidence() -> None:
    native_snapshot = SimpleNamespace(
        capability="available",
        os_permission="allowed",
        application_policy="allowed",
        session_grant="granted-by-explicit-selection",
        capture_scope="exact-application",
        scope_stable_id="fixture:application",
        identity_strength="platform-stable-id",
        permission_epoch=4,
        observed_at_ns=10,
        open_outcome="not-attempted",
    )
    discovered = replace(
        _discovered(SourceKind.APPLICATION),
        _native=SimpleNamespace(
            authorization_before_open=lambda *_args: native_snapshot
        ),
    )

    snapshot = discovered.authorization_before_open(
        os_permission=PermissionObservation.ALLOWED,
        application_policy=ApplicationPolicyObservation.ALLOWED,
        session_grant=CaptureSessionGrant.GRANTED_BY_EXPLICIT_SELECTION,
        permission_epoch=4,
    )

    assert snapshot.capability is CaptureCapabilityState.AVAILABLE
    assert snapshot.capture_scope is CaptureScopeKind.EXACT_APPLICATION
    assert snapshot.open_outcome is CaptureOpenOutcome.NOT_ATTEMPTED
    assert snapshot.permission_epoch == 4


def test_discovery_does_not_fabricate_output_device_session_source() -> None:
    with pytest.raises(PocketStationError) as failure:
        Source.from_discovered(_discovered(SourceKind.OUTPUT_DEVICE))
    assert failure.value.code == "source.unsupported_session_kind"


def test_stable_identity_accepts_typed_platform_without_losing_selector_truth() -> None:
    selected = Source.application_stable_id(Platform.LINUX, "pw-app:42")

    assert selected.selector_kind is SourceSelectorKind.APPLICATION_STABLE_ID
    assert isinstance(selected.selector_value, StableSourceId)
    assert selected.selector_value.platform is Platform.LINUX
    assert selected.selector_value.source_id is None


def test_application_owned_pcm_uses_the_canonical_source_and_recording_path(
    tmp_path,
) -> None:
    session = Session(recording_root=tmp_path)
    audio = session.audio_input(
        "playback",
        capacity_frames=2,
        frame_samples_per_channel=4,
    )
    audio.output.send(session.polled_audio())
    audio.output.record("playback")

    running = session.start()
    audio.write(array("f", [0.25, -0.25, 0.5, -0.5]), discontinuity=True)
    frame = running.audio.read(timeout_s=1.0)
    stop = running.stop()

    assert frame is not None
    assert frame.source_id == audio.source_id
    assert frame.stream_id == audio.stream_id
    assert frame.sequence_number == 0
    assert not hasattr(frame, "sequence_num")
    assert frame.discontinuity_epoch == 1
    assert list(frame.samples.cast("f")) == pytest.approx([0.25, -0.25, 0.5, -0.5])
    assert audio.observations().accepted_total == 1
    assert stop.success
    assert stop.recording is not None
    assert stop.recording.complete
    assert [stem.stem_name for stem in stop.recording.stems] == ["playback"]


def test_audio_input_reports_invalid_full_and_closed_without_blocking() -> None:
    session = Session()
    source = session.pcm_source(
        AudioInputConfig(
            name="generated",
            capacity_frames=1,
            frame_samples_per_channel=4,
        )
    )

    with pytest.raises(AudioInputBufferError) as invalid:
        source.try_write(array("f", [0.0, 1.0]))
    assert invalid.value.code == "audio_input.invalid_buffer"

    source.try_write(array("f", [0.0, 0.0, 0.0, 0.0]))
    with pytest.raises(AudioInputFullError) as full:
        source.try_write(array("f", [1.0, 1.0, 1.0, 1.0]))
    assert full.value.code == "audio_input.full"

    source.close()
    with pytest.raises(AudioInputClosedError) as closed:
        source.try_write(array("f", [0.0, 0.0, 0.0, 0.0]))
    assert closed.value.code == "audio_input.closed"
    observations = source.observations()
    assert observations.accepted_total == 1
    assert observations.full_total == 1
    assert observations.invalid_total == 1
    assert observations.closed


def test_audio_input_write_waits_finitely_without_hiding_nonblocking_try_write() -> (
    None
):
    session = Session()
    audio = session.audio_input(
        "generated",
        capacity_frames=1,
        frame_samples_per_channel=4,
    )
    samples = array("f", [0.0, 0.0, 0.0, 0.0])
    audio.try_write(samples)

    with pytest.raises(AudioInputFullError) as full:
        audio.write(samples, timeout_s=0.005)

    assert full.value.code == "audio_input.full"
    assert audio.observations().full_total > 0


@pytest.mark.parametrize("timeout", [True, -0.1, 60.1])
def test_audio_input_write_rejects_invalid_timeouts(timeout: object) -> None:
    audio = Session().audio_input("generated", frame_samples_per_channel=4)

    with pytest.raises((TypeError, ValueError)):
        audio.write(array("f", [0.0] * 4), timeout_s=timeout)  # type: ignore[arg-type]
