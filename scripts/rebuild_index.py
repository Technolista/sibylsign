#!/usr/bin/env python3
"""Rebuild the global index.json from the on-disk icon files.

The batch generator overwrites `index.json` per category, so the final
file only contains the last category's entries. This script walks the
filesystem and rebuilds a unified index in one pass — much faster than
regenerating all 262k files.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sibylsign.index import IconIndex, build_entry, write_index  # noqa: E402

VALID_SIZES = (32, 64)
VALID_FORMATS = ("svg", "png")


def main() -> int:
    index = IconIndex()
    for fmt in VALID_FORMATS:
        for size in VALID_SIZES:
            base = ROOT / fmt / str(size)
            if not base.exists():
                continue
            for category_dir in sorted(base.iterdir()):
                if not category_dir.is_dir():
                    continue
                category = category_dir.name
                for icon_file in sorted(category_dir.iterdir()):
                    if not icon_file.is_file():
                        continue
                    stem = icon_file.stem
                    index.add(build_entry(
                        concept=stem,
                        category=category,
                        size=size,
                        fmt=fmt,
                    ))
    write_index(ROOT / "index.json", index)
    print(f"Rebuilt index: {index.count} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
