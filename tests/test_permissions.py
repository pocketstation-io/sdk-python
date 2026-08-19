from __future__ import annotations

import sys

import pytest

import pocketstation
from pocketstation import PermissionObservation


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


def test_linux_truth_is_not_reinterpreted_as_allowed_or_denied() -> None:
    if sys.platform != "linux":
        pytest.skip("Linux-specific platform contract")
    assert (
        pocketstation.microphone_permission_observation()
        is PermissionObservation.NOT_OBSERVABLE
    )


@pytest.mark.asyncio
async def test_async_permission_observation_shares_native_policy() -> None:
    assert (
        await pocketstation.aio.microphone_permission_observation()
        is pocketstation.microphone_permission_observation()
    )
