"""Independent test peer for the frozen PKSS 1.0 process contract."""

from __future__ import annotations

import struct
import sys
import time
from typing import BinaryIO

MAGIC = b"PKSS"
HEADER_BYTES = 52
KINDS = {
    "signal": 1,
    "ready": 2,
    "cancel": 4,
    "close": 5,
    "hello": 6,
    "manifest": 7,
    "configure": 8,
    "closed": 10,
}


def read_exact(stream: BinaryIO, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            raise EOFError
        data.extend(chunk)
    return bytes(data)


def read_message(stream: BinaryIO) -> tuple[int, bytes]:
    size = struct.unpack("<I", read_exact(stream, 4))[0]
    frame = read_exact(stream, size)
    if len(frame) < HEADER_BYTES or frame[:4] != MAGIC:
        raise ValueError("bad PKSS frame")
    return frame[8], frame


def write_message(
    stream: BinaryIO,
    kind: int,
    payload: bytes = b"",
    *,
    signal: bytes = b"pks.sidecar.control.v1",
    source: bytes | None = None,
) -> None:
    if source is not None:
        frame = bytearray(source)
        frame[8] = kind
    else:
        header = (
            MAGIC
            + struct.pack("<HHBBHQQQ", 1, 0, kind, 0, 0, 0, 0, 0)
            + struct.pack("<IIII", len(signal), 0, 0, len(payload))
        )
        frame = bytearray(header + signal + payload)
    stream.write(struct.pack("<I", len(frame)) + frame)
    stream.flush()


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "healthy"
    reader = sys.stdin.buffer
    writer = sys.stdout.buffer
    kind, _ = read_message(reader)
    if kind != KINDS["hello"]:
        return 2
    write_message(writer, KINDS["hello"])
    if mode == "malformed":
        writer.write(struct.pack("<I", 4) + b"NOPE")
        writer.flush()
        return 3
    write_message(writer, KINDS["manifest"], b'{"ports":["signal"]}')
    kind, _ = read_message(reader)
    if kind != KINDS["configure"]:
        return 4
    write_message(writer, KINDS["ready"])
    if mode == "crash":
        return 17
    if mode == "saturated":
        time.sleep(0.25)
    while True:
        kind, frame = read_message(reader)
        if kind == KINDS["signal"]:
            write_message(writer, KINDS["signal"], source=frame)
        elif kind in (KINDS["close"], KINDS["cancel"]):
            if mode == "hang":
                time.sleep(30)
                return 18
            write_message(writer, KINDS["closed"])
            return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BrokenPipeError, EOFError):
        raise SystemExit(0) from None
