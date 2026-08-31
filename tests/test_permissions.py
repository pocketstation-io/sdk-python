from __future__ import annotations

import sys

import pocketstation._api as pocketstation
import pytest
from pocketstation._api import (
    CapturePermissionLifecycle,
    CapturePermissionTransitionKind,
    PermissionObservation,
)
from pocketstation.aio.sources import (
    microphone_permission_observation as async_microphone_permission_observation,
)


def test_permission_observation_is_typed_and_has_no_prompt_api() -> None:
    observation = pocketstation.microphone_permission_observation()

    assert isinstance(observation, PermissionObservation)
    assert "request_microphone_permission" not in pocketstation.__all__
    assert "prompt_microphone_permission" not in pocketstation.__all__


def test_permission_states_do_not_collapse_to_a_boolean() -> None:
    assert {item.value for item in PermissionObservation} == {
        "allowed",
        "denied",
        "restricted",
        "not-determined",
        "revoked",
        "not-observable",
        "not-applicable",
    }
    assert not issubclass(PermissionObservation, bool)


def test_permission_lifecycle_preserves_transitions_and_epochs() -> None:
    lifecycle = CapturePermissionLifecycle(PermissionObservation.ALLOWED)

    assert lifecycle.current is PermissionObservation.ALLOWED
    assert lifecycle.permission_epoch == 1
    assert lifecycle.observe(PermissionObservation.ALLOWED) is None

    revoked = lifecycle.observe(PermissionObservation.REVOKED)
    assert revoked is not None
    assert revoked.kind is CapturePermissionTransitionKind.REVOKED
    assert revoked.previous is PermissionObservation.ALLOWED
    assert revoked.current is PermissionObservation.REVOKED
    assert revoked.permission_epoch == 2
    assert lifecycle.permission_epoch == 2

    changed = lifecycle.observe(PermissionObservation.NOT_DETERMINED)
    assert changed is not None
    assert changed.kind is CapturePermissionTransitionKind.CHANGED
    assert changed.permission_epoch == 3


def test_linux_truth_is_not_reinterpreted_as_allowed_or_denied() -> None:
    if sys.platform != "linux":
        pytest.skip("Linux-specific platform contract")
    assert (
        pocketstation.microphone_permission_observation()
        is PermissionObservation.NOT_OBSERVABLE
    )


def test_windows_binding_fails_closed_until_safe_core_query_is_available() -> None:
    if sys.platform != "win32":
        pytest.skip("Windows-specific platform contract")
    assert (
        pocketstation.microphone_permission_observation()
        is PermissionObservation.NOT_OBSERVABLE
    )


@pytest.mark.asyncio
async def test_async_permission_observation_shares_native_policy() -> None:
    assert (
        await async_microphone_permission_observation()
        is pocketstation.microphone_permission_observation()
    )
