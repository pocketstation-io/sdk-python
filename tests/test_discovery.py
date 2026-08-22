from __future__ import annotations

from dataclasses import FrozenInstanceError

import pocketstation._api as pocketstation
import pytest
from pocketstation._api import SourceKind, SourceQuery


def test_discovery_returns_an_immutable_typed_native_snapshot() -> None:
    sources = pocketstation.discover_sources()

    assert isinstance(sources, tuple)
    for source in sources:
        assert source.stable_id.stable_key
        assert source.stable_id.source_id is not None
        assert source.sample_rate_hz > 0
        assert source.channel_count > 0
        with pytest.raises(FrozenInstanceError):
            source.name = "changed"


def test_discovery_query_executes_in_native_and_preserves_exact_identity() -> None:
    sources = pocketstation.discover_sources()
    if not sources:
        pytest.skip("this build exposes no native discovery sources")
    expected = sources[0]

    result = pocketstation.discover_sources(
        SourceQuery.stable_key(expected.stable_id.stable_key)
    )

    assert result
    assert all(
        item.stable_id.stable_key == expected.stable_id.stable_key for item in result
    )


def test_kind_query_and_capability_query_are_typed() -> None:
    applications = pocketstation.discover_sources(
        SourceQuery.kind(SourceKind.APPLICATION)
    )

    assert all(item.stable_id.kind is SourceKind.APPLICATION for item in applications)
    assert isinstance(pocketstation.application_capture_available(), bool)


@pytest.mark.asyncio
async def test_async_discovery_shares_the_synchronous_native_policy() -> None:
    synchronous = pocketstation.discover_sources(
        SourceQuery.kind(SourceKind.SYSTEM_MIX)
    )
    asynchronous = await pocketstation.aio.discover_sources(
        SourceQuery.kind(SourceKind.SYSTEM_MIX)
    )

    assert asynchronous == synchronous


@pytest.mark.parametrize("builder", [SourceQuery.application, SourceQuery.stable_key])
def test_query_rejects_empty_values_before_native_work(builder) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        builder(" ")
