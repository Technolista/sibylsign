"""Bootstrap verification: asserts the project skeleton is complete.

This script is the public seam that verifies T1 acceptance criteria. A
developer can run it after cloning the repo to confirm the scaffold is
present and well-formed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    ".gitignore",
    "requirements.txt",
]

REQUIRED_DIRS = [
    "svg",
    "png",
    "docs",
]

REQUIRED_PYTHON_DEPS = ["svgwrite", "cairosvg", "Pillow"]


def check_required_files(project_root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (project_root / rel).exists():
            errors.append(f"missing required file: {rel}")
    return errors


def check_required_dirs(project_root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_DIRS:
        path = project_root / rel
        if not path.exists():
            errors.append(f"missing required directory: {rel}")
        elif not path.is_dir():
            errors.append(f"expected directory, got non-directory: {rel}")
    return errors


def check_python_dependencies(project_root: Path) -> list[str]:
    errors: list[str] = []
    req_path = project_root / "requirements.txt"
    if not req_path.exists():
        return errors  # already reported by check_required_files
    text = req_path.read_text(encoding="utf-8")
    declared = {line.strip().lower() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")}
    # Normalise: many requirement files include extras like "Pillow>=10.0".
    declared_names = {name.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split("<")[0].split(">")[0].strip().lower() for name in declared}
    for dep in REQUIRED_PYTHON_DEPS:
        if dep.lower() not in declared_names:
            errors.append(f"required dependency not declared in requirements.txt: {dep}")
    return errors


def check_mit_license(project_root: Path) -> list[str]:
    errors: list[str] = []
    license_path = project_root / "LICENSE"
    if not license_path.exists():
        return errors  # already reported
    text = license_path.read_text(encoding="utf-8").lower()
    if "mit license" not in text and "permission is hereby granted, free of charge" not in text:
        errors.append("LICENSE does not appear to contain the MIT license text")
    return errors


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    all_errors: list[str] = []
    all_errors += check_required_files(project_root)
    all_errors += check_required_dirs(project_root)
    all_errors += check_python_dependencies(project_root)
    all_errors += check_mit_license(project_root)
    if all_errors:
        print("Bootstrap check FAILED:")
        for err in all_errors:
            print(f"  - {err}")
        return 1
    print("Bootstrap check PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
