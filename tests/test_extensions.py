from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import FrozenInstanceError
from pathlib import Path

import pocketstation._api as pks
import pocketstation.aio._api as aio
import pytest

SOURCE_ID = "dev.pocketstation.source.fixture.v1"
OPERATOR_ID = "dev.pocketstation.fixture.operator.v1"
ENDPOINT_ID = "dev.pocketstation.fixture.endpoint.v1"


@pytest.fixture(scope="module")
def native_extension_library(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, Path]:
    directory = tmp_path_factory.mktemp("native-extension")
    marker = directory / "lifecycle.log"
    suffix = (
        ".dll"
        if sys.platform == "win32"
        else ".dylib"
        if sys.platform == "darwin"
        else ".so"
    )
    prefix = "" if sys.platform == "win32" else "lib"
    library = directory / f"{prefix}pks_python_fixture{suffix}"
    source = Path(__file__).with_name("fixtures") / "native_extension_plugin.rs"
    environment = os.environ.copy()
    environment["PKS_FIXTURE_MARKER"] = str(marker)
    subprocess.run(
        [
            "rustc",
            "--crate-type=cdylib",
            "--edition=2021",
            "-C",
            "debuginfo=0",
            str(source),
            "-o",
            str(library),
        ],
        check=True,
        env=environment,
        capture_output=True,
        text=True,
    )
    return library, marker


def port(
    name: str,
    direction: pks.ExtensionPortDirection,
) -> pks.ExtensionPort:
    return pks.ExtensionPort(
        name=name,
        direction=direction,
        signal_id="pks.signal.text.utf8.v1",
        semantic_role="transcript",
        schema="text/plain; charset=utf-8",
    )


def test_linked_native_extension_abi_is_authoritative() -> None:
    current = pks.ExtensionAbiVersion.current()

    assert current.abi_major == 1
    assert current.abi_minor == 2
    assert current.struct_size_bytes == 8
    current.require_compatible()


@pytest.mark.parametrize(
    ("kind", "ports"),
    [
        (
            pks.ExtensionKind.SOURCE,
            (port("output", pks.ExtensionPortDirection.OUTPUT),),
        ),
        (
            pks.ExtensionKind.OPERATOR,
            (
                port("input", pks.ExtensionPortDirection.INPUT),
                port("output", pks.ExtensionPortDirection.OUTPUT),
            ),
        ),
        (
            pks.ExtensionKind.ENDPOINT,
            (port("input", pks.ExtensionPortDirection.INPUT),),
        ),
    ],
)
def test_complete_descriptor_is_validated_by_native_abi(
    kind: pks.ExtensionKind,
    ports: tuple[pks.ExtensionPort, ...],
) -> None:
    descriptor = pks.ExtensionDescriptor(
        extension_id=f"io.pocketstation.python.test.{kind.value}.v1",
        kind=kind,
        ports=ports,
        revision=2,
        generation=3,
    )

    assert descriptor.abi_major == 1
    assert descriptor.abi_minor == 2
    assert descriptor.revision == 2
    assert descriptor.generation == 3


def test_native_validator_rejects_duplicate_ports() -> None:
    duplicate = port("signal", pks.ExtensionPortDirection.INPUT)

    with pytest.raises(pks.ExtensionError) as caught:
        pks.ExtensionDescriptor(
            extension_id="io.pocketstation.python.test.operator.v1",
            kind=pks.ExtensionKind.OPERATOR,
            ports=(
                duplicate,
                duplicate,
                port("output", pks.ExtensionPortDirection.OUTPUT),
            ),
        )

    assert caught.value.code == "extension.invalid_descriptor"


def test_native_validator_rejects_incompatible_versions() -> None:
    with pytest.raises(pks.ExtensionError) as major:
        pks.ExtensionAbiVersion(8, 2, 0).require_compatible()
    with pytest.raises(pks.ExtensionError) as minor:
        pks.ExtensionAbiVersion(8, 1, 3).require_compatible()

    assert major.value.code == "extension.unsupported_abi_major"
    assert minor.value.code == "extension.unsupported_abi_minor"


def test_descriptor_is_an_immutable_contract_not_a_python_callback() -> None:
    descriptor = pks.ExtensionDescriptor(
        extension_id="io.pocketstation.python.test.endpoint.v1",
        kind=pks.ExtensionKind.ENDPOINT,
        ports=(port("input", pks.ExtensionPortDirection.INPUT),),
    )

    with pytest.raises(FrozenInstanceError):
        descriptor.revision = 9  # type: ignore[misc]
    assert not hasattr(descriptor, "callback")
    assert not hasattr(descriptor, "execute")


def test_async_namespace_uses_the_same_descriptor_types() -> None:
    assert aio.ExtensionDescriptor is pks.ExtensionDescriptor
    assert aio.ExtensionAbiVersion is pks.ExtensionAbiVersion


def test_relative_native_library_path_is_rejected_by_core() -> None:
    with pytest.raises(pks.ExtensionError) as failure:
        pks.Session().load_native_extension_library("fixture-extension")

    assert failure.value.code == "extension.path_not_absolute"


def test_native_library_receipt_is_typed_and_immutable(
    native_extension_library: tuple[Path, Path],
) -> None:
    library, _ = native_extension_library
    receipt = pks.Session().load_native_extension_library(library)

    assert receipt.canonical_path == library.resolve()
    assert receipt.registrations == (
        pks.NativeExtensionRegistration(SOURCE_ID, pks.ExtensionKind.SOURCE, 1, 1),
        pks.NativeExtensionRegistration(
            OPERATOR_ID,
            pks.ExtensionKind.OPERATOR,
            1,
            1,
        ),
        pks.NativeExtensionRegistration(
            ENDPOINT_ID,
            pks.ExtensionKind.ENDPOINT,
            1,
            1,
        ),
    )
    with pytest.raises(FrozenInstanceError):
        receipt.canonical_path = Path("changed")  # type: ignore[misc]


def test_loaded_native_source_operator_and_endpoint_execute_in_one_session(
    native_extension_library: tuple[Path, Path],
) -> None:
    library, marker = native_extension_library
    session = pks.Session()
    session.load_native_extension_library(library)
    source = session.source(SOURCE_ID)
    operator = session.operator(pks.Operator(OPERATOR_ID))
    source.output("out").connect(operator.input("in"))
    endpoint = session.endpoint(pks.EndpointDescriptor(ENDPOINT_ID, ENDPOINT_ID))
    operator.output("out").send(endpoint, input_port="in")

    with session.start():
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if marker.exists() and "consume:hello" in marker.read_text():
                break
            time.sleep(0.01)

    assert "consume:hello" in marker.read_text()


def test_duplicate_native_library_import_is_transactional(
    native_extension_library: tuple[Path, Path],
) -> None:
    library, _ = native_extension_library
    session = pks.Session()
    session.load_native_extension_library(library)

    with pytest.raises(pks.ExtensionError) as failure:
        session.load_native_extension_library(library)

    assert failure.value.code == "extension.duplicate_registration"


def test_async_session_uses_the_same_native_library_declaration(
    native_extension_library: tuple[Path, Path],
) -> None:
    library, _ = native_extension_library
    receipt = aio.Session().load_native_extension_library(library)

    assert receipt.canonical_path == library.resolve()
    assert [registration.kind for registration in receipt.registrations] == [
        pks.ExtensionKind.SOURCE,
        pks.ExtensionKind.OPERATOR,
        pks.ExtensionKind.ENDPOINT,
    ]
