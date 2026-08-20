"""Dependency-free executor for PocketStation notebooks without IPython magic."""

from __future__ import annotations

import argparse
import ast
import asyncio
import inspect
import json
from collections.abc import Awaitable
from pathlib import Path
from typing import Any


def execute(path: Path) -> None:
    notebook = json.loads(path.read_text())
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise ValueError("expected a version 4 notebook with a cells array")
    namespace: dict[str, object] = {"__name__": "__notebook__"}
    for index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source")
        if not isinstance(source, list) or not all(
            isinstance(line, str) for line in source
        ):
            raise ValueError(f"code cell {index} has invalid source")
        code = compile(
            "".join(source),
            f"{path}#cell-{index}",
            "exec",
            flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
        )
        result = eval(code, namespace)
        if inspect.isawaitable(result):
            asyncio.run(_await_result(result))


async def _await_result(result: Awaitable[Any]) -> Any:
    return await result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    arguments = parser.parse_args()
    execute(arguments.notebook)


if __name__ == "__main__":
    main()
