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
    CaptureError,
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
    SessionDeclarationError,
    Source,
    SourceIdentityStrength,
    SourceKind,
    SourceQuery,
    SourceSelectorKind,
    SourceState,
    StableSourceId,
    discover_sources,
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
    system_audio = Source.system_audio()
    microphone = Source.microphone_default()

    assert application.kind is SourceKind.APPLICATION
    assert application.selector_kind is SourceSelectorKind.APPLICATION_NAME
    assert application.selector_value == "PocketStation Fixture"
    assert system_audio.kind is SourceKind.SYSTEM_MIX
    assert system_audio.selector_kind is SourceSelectorKind.SYSTEM_MIX
    assert system_audio.selector_value is None
    assert microphone.kind is SourceKind.INPUT_DEVICE
    assert microphone.selector_kind is SourceSelectorKind.MICROPHONE_DEFAULT
    with pytest.raises(FrozenInstanceError):
        application.selector_value = "changed"


def test_invalid_source_selectors_keep_typed_failure_code() -> None:
    declarations = (
        lambda: Source.application(" "),
        lambda: Source.application(None),  # type: ignore[arg-type]
        lambda: Source.application_bundle_id(" "),
        lambda: Source.application_process_id(0),
        lambda: Source.application_process_id(-1),
        lambda: Source.application_process_id(1 << 32),
        lambda: Source.application_process_id(True),
        lambda: Source.application_process_id("1"),  # type: ignore[arg-type]
        lambda: Source.application_process_id(1.0),  # type: ignore[arg-type]
        lambda: Source.application_stable_id(Platform.MACOS, " "),
        lambda: Source.application_process_instance(0, Platform.MACOS, "app"),
        lambda: Source.application_process_instance(1 << 32, Platform.MACOS, "app"),
        lambda: Source.application_process_instance(1, Platform.MACOS, " "),
        lambda: Source.microphone_id(" "),
        lambda: SourceQuery.application(" "),
        lambda: SourceQuery.application(None),  # type: ignore[arg-type]
        lambda: SourceQuery.kind("application"),  # type: ignore[arg-type]
        lambda: SourceQuery.stable_key(" "),
    )

    for declare_source in declarations:
        with pytest.raises(SessionDeclarationError) as failure:
            declare_source()
        assert failure.value.code == "session.invalid_selector"


def test_discovery_rejects_forged_or_untyped_queries_before_native_work() -> None:
    invalid_queries = (
        object(),
        {"type": "all"},
        SourceQuery("any", "unexpected"),
        SourceQuery("playing", "unexpected"),
        SourceQuery("application", None),
        SourceQuery("stable-key", " "),
        SourceQuery("kind", "camera"),
        SourceQuery("camera", None),
    )

    for query in invalid_queries:
        with pytest.raises(SessionDeclarationError) as failure:
            discover_sources(query)  # type: ignore[arg-type]
        assert failure.value.code == "session.invalid_selector"


def test_process_identifier_boundaries_preserve_exact_selector_identity() -> None:
    for process_id in (1, (1 << 32) - 1):
        selected = Source.application_process_id(process_id)
        assert selected.selector_kind is SourceSelectorKind.APPLICATION_PROCESS_ID
        assert selected.selector_value == process_id


def test_authorization_rejects_invalid_values_before_native_access() -> None:
    discovered = _discovered(SourceKind.APPLICATION)
    invalid_values = (
        (
            {"os_permission": "allowed"},
            "capture.invalid_permission_observation",
        ),
        (
            {"application_policy": "allowed"},
            "capture.invalid_application_policy",
        ),
        (
            {"session_grant": "granted-by-explicit-selection"},
            "capture.invalid_session_grant",
        ),
        ({"permission_epoch": 0}, "capture.invalid_permission_epoch"),
        ({"permission_epoch": -1}, "capture.invalid_integer"),
        ({"permission_epoch": 1 << 64}, "capture.invalid_integer"),
        ({"permission_epoch": True}, "capture.invalid_integer"),
        ({"permission_epoch": 1.0}, "capture.invalid_integer"),
    )

    for arguments, code in invalid_values:
        with pytest.raises(CaptureError) as failure:
            discovered.authorization_before_open(**arguments)  # type: ignore[arg-type]
        assert failure.value.code == code


def test_authorization_defaults_and_unsigned_boundaries_reach_native_exactly() -> None:
    calls: list[tuple[str, str, str, int]] = []

    def authorize(
        os_permission: str,
        application_policy: str,
        session_grant: str,
        permission_epoch: int,
    ) -> SimpleNamespace:
        calls.append(
            (
                os_permission,
                application_policy,
                session_grant,
                permission_epoch,
            )
        )
        return SimpleNamespace(
            capability="available",
            os_permission=os_permission,
            application_policy=application_policy,
            session_grant=session_grant,
            capture_scope="exact-application",
            scope_stable_id="fixture:application",
            identity_strength="platform-stable-id",
            permission_epoch=permission_epoch,
            observed_at_ns=10,
            open_outcome="not-attempted",
        )

    discovered = replace(
        _discovered(SourceKind.APPLICATION),
        _native=SimpleNamespace(authorization_before_open=authorize),
    )

    default_snapshot = discovered.authorization_before_open()
    maximum_snapshot = discovered.authorization_before_open(
        permission_epoch=(1 << 64) - 1
    )

    assert default_snapshot.permission_epoch == 1
    assert default_snapshot.observed_at_ns == 10
    assert maximum_snapshot.permission_epoch == (1 << 64) - 1
    assert calls == [
        ("not-observable", "not-observable", "not-evaluated", 1),
        ("not-observable", "not-observable", "not-evaluated", (1 << 64) - 1),
    ]


def test_discovered_application_uses_exact_process_and_stable_identity() -> None:
    selected = Source.from_discovered(_discovered(SourceKind.APPLICATION))

    assert selected.selector_kind is SourceSelectorKind.APPLICATION_PROCESS_INSTANCE
    assert selected.kind is SourceKind.APPLICATION


def test_from_discovered_rejects_untyped_or_malformed_identity() -> None:
    discovered = _discovered(SourceKind.APPLICATION)
    invalid_sources = (
        None,
        object(),
        replace(discovered, stable_id=None),  # type: ignore[arg-type]
        replace(
            discovered,
            stable_id=replace(discovered.stable_id, platform="macos"),  # type: ignore[arg-type]
        ),
        replace(
            discovered,
            stable_id=replace(discovered.stable_id, kind="camera"),  # type: ignore[arg-type]
        ),
        replace(
            discovered,
            stable_id=replace(discovered.stable_id, stable_key=" "),
        ),
        replace(
            discovered,
            stable_id=replace(discovered.stable_id, source_id=True),
        ),
        replace(
            discovered,
            stable_id=replace(discovered.stable_id, source_id=0),
        ),
        replace(
            discovered,
            stable_id=replace(discovered.stable_id, source_id=1 << 64),
        ),
    )

    for source in invalid_sources:
        with pytest.raises(SessionDeclarationError) as failure:
            Source.from_discovered(source)  # type: ignore[arg-type]
        assert failure.value.code == "session.invalid_selector"


def test_no_pid_application_retains_discovery_identity_as_selector_metadata() -> None:
    discovered = replace(_discovered(SourceKind.APPLICATION), process_id=None)

    selected = Source.from_discovered(discovered)

    assert selected.selector_kind is SourceSelectorKind.APPLICATION_STABLE_ID
    assert selected.selector_value == discovered.stable_id
    assert isinstance(selected.selector_value, StableSourceId)
    assert selected.selector_value.source_id == 42


def test_discovered_input_device_lowers_to_microphone_id() -> None:
    selected = Source.from_discovered(_discovered(SourceKind.INPUT_DEVICE))

    assert selected.selector_kind is SourceSelectorKind.MICROPHONE_ID
    assert selected.selector_value == "device-42"


def test_empty_discovered_device_uid_is_invalid_instead_of_falling_back() -> None:
    discovered = replace(_discovered(SourceKind.INPUT_DEVICE), device_uid="")

    with pytest.raises(PocketStationError) as failure:
        Source.from_discovered(discovered)

    assert failure.value.code == "session.invalid_selector"


def test_discovered_system_mix_lowers_to_system_audio() -> None:
    selected = Source.from_discovered(_discovered(SourceKind.SYSTEM_MIX))

    assert selected.selector_kind is SourceSelectorKind.SYSTEM_MIX
    assert selected.kind is SourceKind.SYSTEM_MIX


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
