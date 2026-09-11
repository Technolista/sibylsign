#!/usr/bin/env python3
"""Batch icon generator CLI.

Usage:
    python3 scripts/generate.py <category>
    python3 scripts/generate.py all

Reads `catalog.yaml` at the project root and emits icons into the
project's `svg/` and `png/` directories along with an `index.json`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from the repo root without installing the package.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sibylsign.pipeline import generate_category  # noqa: E402


CATEGORIES: tuple[str, ...] = (
    "ui-kit",
    "animals",
    "food-drink",
    "transportation",
    "tools",
    "weather",
    "communication",
    "clothing",
    "sports",
    "nature",
    "symbols",
    "icons-special",
)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate sibylsign icons for a category")
    parser.add_argument("category", help=f"one of: all or {', '.join(CATEGORIES)}")
    args = parser.parse_args(argv)

    catalog_path = ROOT / "catalog.yaml"
    output_dir = ROOT

    if args.category == "all":
        targets = CATEGORIES
    elif args.category in CATEGORIES:
        targets = (args.category,)
    else:
        parser.error(f"unknown category: {args.category!r}")

    for cat in targets:
        print(f"Generating {cat} ...", flush=True)
        n = generate_category(
            catalog=catalog_path,
            category=cat,
            output_dir=output_dir,
        )
        print(f"  {cat}: {n} icons", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
