from __future__ import annotations

import pytest

from tests.qualification.runtime_resources import _percentile


@pytest.mark.parametrize(
    ("percentile", "expected"),
    [(0, 1), (1, 1), (50, 2), (95, 4), (99, 4), (100, 4)],
)
def test_nearest_rank_percentile_is_deterministic(
    percentile: int,
    expected: int,
) -> None:
    assert _percentile([4, 1, 3, 2], percentile) == expected


def test_percentile_rejects_empty_or_invalid_input() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        _percentile([], 50)
    with pytest.raises(ValueError, match="between 0 and 100"):
        _percentile([1], 101)
