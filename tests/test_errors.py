from __future__ import annotations

import pytest
from pocketstation.errors import (
    CaptureError,
    ConnectorRuntimeError,
    GraphError,
    OperatorError,
    SessionCompileDiagnostic,
    SessionDeclarationError,
    SessionRuntimeError,
    SessionStartError,
    SourceError,
    _normalize_native_error,
)


@pytest.mark.parametrize(
    ("encoded", "expected"),
    [
        ("[session.invalid_route] wrong owner", SessionDeclarationError),
        ("[session.endpoint_start_failed] refused", SessionStartError),
        ("[session.missing_metrics_snapshot] unavailable", SessionRuntimeError),
        ("[capture.permission_denied] denied", CaptureError),
        ("[graph.invalid_contract] incompatible", GraphError),
        ("[source.invalid_contract] invalid", SourceError),
        ("[operator.registration_failed] duplicate", OperatorError),
        ("[connector.registration_failed] duplicate", ConnectorRuntimeError),
    ],
)
def test_native_codes_map_to_stable_failure_families(
    encoded: str,
    expected: type[Exception],
) -> None:
    error = _normalize_native_error(RuntimeError(encoded))

    assert isinstance(error, expected)
    assert error.code == encoded[1 : encoded.index("]")]


def test_native_compile_diagnostic_is_projected_without_message_parsing() -> None:
    native_error = RuntimeError("[session.compile_failed] graph rejected")
    native_error._pocketstation_compile_code = "compile.graph.media_mismatch"  # type: ignore[attr-defined]
    native_error._pocketstation_compile_edge_index = 7  # type: ignore[attr-defined]
    native_error._pocketstation_compile_expected = "audio/f32/mono"  # type: ignore[attr-defined]
    native_error._pocketstation_compile_actual = "audio/f32/stereo"  # type: ignore[attr-defined]

    error = _normalize_native_error(native_error)

    assert isinstance(error, SessionStartError)
    assert error.diagnostic == SessionCompileDiagnostic(
        code="compile.graph.media_mismatch",
        edge_index=7,
        expected="audio/f32/mono",
        actual="audio/f32/stereo",
    )
