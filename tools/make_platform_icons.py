"""Builds icon.ico (Windows) and icon.icns (macOS) from the PNGs made by tools/make_icon.py.

    uv run python tools/make_icon.py && uv run python tools/make_platform_icons.py

No imaging library needed: both containers accept PNG-compressed images, so this only assembles bytes.
Output: packaging/icons/icon.ico, icon.icns and icon.png (Linux, 512 px).
"""

from __future__ import annotations

import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "tenhut" / "assets" / "icons"
OUT = ROOT / "packaging" / "icons"


def png(size: int) -> bytes:
    return (SRC / f"icon-{size}.png").read_bytes()


def make_ico(path: Path, sizes=(16, 24, 32, 48, 64, 128, 256)) -> None:
    """ICO with PNG entries (Windows Vista+). A width/height byte of 0 means 256."""
    images = [(s, png(s)) for s in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, blobs = b"", b""
    for size, data in images:
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset + len(blobs))
        blobs += data
    path.write_bytes(header + entries + blobs)


def make_icns(path: Path) -> None:
    """ICNS with PNG chunks: icp4=16, icp5=32, icp6=64, ic07=128, ic08=256, ic09=512, ic10=1024."""
    chunks = b""
    for kind, size in (
        ("icp4", 16),
        ("icp5", 32),
        ("icp6", 64),
        ("ic07", 128),
        ("ic08", 256),
        ("ic09", 512),
        ("ic10", 1024),
    ):
        data = png(size)
        chunks += kind.encode() + struct.pack(">I", 8 + len(data)) + data
    path.write_bytes(b"icns" + struct.pack(">I", 8 + len(chunks)) + chunks)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_ico(OUT / "icon.ico")
    make_icns(OUT / "icon.icns")
    shutil.copyfile(SRC / "icon-512.png", OUT / "icon.png")
    for f in sorted(OUT.iterdir()):
        print(f"{f.name:12s} {f.stat().st_size:>9,d} bytes")


if __name__ == "__main__":
    main()
