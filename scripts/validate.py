#!/usr/bin/env python3
"""Validation CLI.

Usage:
    python3 scripts/validate.py

Walks the project's `svg/` and `png/` directories, validates every icon
file against the project's contracts (well-formed, correct size, kebab-case
filename) and verifies that `index.json` references match reality. Exits
non-zero on any issue.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sibylsign.validation import validate_directory  # noqa: E402


def main() -> int:
    report = validate_directory(ROOT)
    if report.ok:
        print("Validation PASSED")
        return 0
    print("Validation FAILED:")
    for issue in report.issues:
        print(f"  - {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
