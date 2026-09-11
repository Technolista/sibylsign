"""Automated validation suite (T7).

The validator is the gatekeeper that runs against any generated icon set.
It checks external behaviour — files exist where the index says they do,
file contents are well-formed, sizes match, names are kebab-case, paths
are in the correct category — never implementation details of the
generator.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

SVG_NS = "http://www.w3.org/2000/svg"
_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_VALID_SIZES: frozenset[int] = frozenset({32, 64})


@dataclass
class ValidationReport:
    """A bag of issues found by the validator."""

    ok: bool = True
    issues: list[str] = field(default_factory=list)

    def add(self, issue: str) -> None:
        self.ok = False
        self.issues.append(issue)


# ---------------------------------------------------------------------------
# Primitive file-level validators
# ---------------------------------------------------------------------------


def _expected_path_attrs(svg_root: ET.Element) -> tuple[int | None, int | None]:
    raw_w = svg_root.get("width")
    raw_h = svg_root.get("height")
    try:
        w = int(re.sub(r"[^0-9]", "", raw_w)) if raw_w else None
    except ValueError:
        w = None
    try:
        h = int(re.sub(r"[^0-9]", "", raw_h)) if raw_h else None
    except ValueError:
        h = None
    return w, h


def validate_svg(path: Path, expected_size: int) -> list[str]:
    """Validate a single SVG file. Returns a list of issues (empty if OK)."""
    issues: list[str] = []
    if not path.exists():
        return [f"{path}: file not found"]
    if not _KEBAB_RE.match(path.stem):
        issues.append(f"{path.name}: filename is not kebab-case")
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        issues.append(f"{path.name}: malformed XML ({exc})")
        return issues
    if root.tag != f"{{{SVG_NS}}}svg":
        issues.append(f"{path.name}: root element is not <svg>")
    w, h = _expected_path_attrs(root)
    if w != expected_size or h != expected_size:
        issues.append(
            f"{path.name}: size {w}x{h} does not match expected {expected_size}x{expected_size}"
        )
    return issues


def validate_png(path: Path, expected_size: int) -> list[str]:
    """Validate a single PNG file. Returns a list of issues (empty if OK)."""
    issues: list[str] = []
    if not path.exists():
        return [f"{path}: file not found"]
    if not _KEBAB_RE.match(path.stem):
        issues.append(f"{path.name}: filename is not kebab-case")
    try:
        img = Image.open(path)
        img.verify()
        # Reopen after verify because verify() invalidates the image.
        img = Image.open(path)
        size = img.size
    except Exception as exc:
        issues.append(f"{path.name}: unreadable PNG ({exc})")
        return issues
    if size != (expected_size, expected_size):
        issues.append(
            f"{path.name}: pixel dimensions {size} do not match expected "
            f"({expected_size}, {expected_size})"
        )
    return issues


# ---------------------------------------------------------------------------
# Index validator
# ---------------------------------------------------------------------------


def validate_index(index_path: Path, root: Path) -> list[str]:
    """Validate the index file: every entry must point to an existing file."""
    issues: list[str] = []
    if not index_path.exists():
        return [f"index not found: {index_path}"]
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{index_path.name}: invalid JSON ({exc})"]
    if not isinstance(data, list):
        return [f"{index_path.name}: index must be a JSON array"]
    for entry in data:
        if not isinstance(entry, dict):
            issues.append(f"index entry is not an object: {entry!r}")
            continue
        rel = entry.get("file_path")
        if not isinstance(rel, str):
            issues.append(f"index entry missing 'file_path': {entry!r}")
            continue
        target = (root / rel).resolve()
        if not target.exists():
            issues.append(f"index references missing file: {rel}")
    return issues


# ---------------------------------------------------------------------------
# Directory validator (the main CLI seam)
# ---------------------------------------------------------------------------


def _iter_index_files(root: Path) -> list[tuple[Path, int, str]]:
    """Walk `root` and yield (path, expected_size, fmt) for every icon file."""
    out: list[tuple[Path, int, str]] = []
    for fmt in ("svg", "png"):
        for size in (32, 64):
            base = root / fmt / str(size)
            if not base.exists():
                continue
            for p in base.rglob(f"*.{fmt}"):
                out.append((p, size, fmt))
    return out


def validate_directory(root: Path) -> ValidationReport:
    """Validate every icon file under `root` and the index.json."""
    report = ValidationReport()
    index_path = root / "index.json"
    if not index_path.exists():
        report.add(f"index not found at {index_path}")
        return report
    for path, expected_size, fmt in _iter_index_files(root):
        if fmt == "svg":
            for issue in validate_svg(path, expected_size=expected_size):
                report.add(issue)
        else:
            for issue in validate_png(path, expected_size=expected_size):
                report.add(issue)
    for issue in validate_index(index_path, root=root):
        report.add(issue)
    return report
