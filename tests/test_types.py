"""Stable exception contract tests."""

import pytest

from pocketstation import PocketStationError


def test_given_pocketstation_error_when_raised_then_code_set():
    with pytest.raises(PocketStationError) as exc_info:
        raise PocketStationError("connection failed", "network_error")
    assert exc_info.value.code == "network_error"
    assert "connection failed" in str(exc_info.value)
