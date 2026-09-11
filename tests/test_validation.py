"""Tests for the automated validation suite (T7).

The validator is the gatekeeper that runs against any generated icon
set. It checks external behaviour (files exist where the index says
they do, file contents are well-formed, sizes match, names are
kebab-case, paths are in the correct category) — never implementation
details of the generator.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

from sibylsign.validation import (
    ValidationReport,
    validate_directory,
    validate_index,
    validate_png,
    validate_svg,
)


# ---------------------------------------------------------------------------
# Helper: build a tiny synthetic icon set on disk.
# ---------------------------------------------------------------------------


def _write_svg(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    svg = (
        f'<?xml version="1.0" encoding="utf-8"?>'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">'
        f'<rect width="{size}" height="{size}" fill="#000000"/>'
        f'</svg>'
    )
    path.write_text(svg, encoding="utf-8")


def _write_png(path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.save(path, format="PNG")


def _build_icon_set(root: Path) -> None:
    """Build a tiny icon set: 1 category × 1 concept × 2 sizes × 2 formats."""
    _write_svg(root / "svg" / "32" / "ui-kit" / "button-primary.svg", 32)
    _write_svg(root / "svg" / "64" / "ui-kit" / "button-primary.svg", 64)
    _write_png(root / "png" / "32" / "ui-kit" / "button-primary.png", 32)
    _write_png(root / "png" / "64" / "ui-kit" / "button-primary.png", 64)
    index = [
        {"file_path": "svg/32/ui-kit/button-primary.svg", "category": "ui-kit",
         "descriptive_name": "button-primary", "color": "#000000"},
        {"file_path": "svg/64/ui-kit/button-primary.svg", "category": "ui-kit",
         "descriptive_name": "button-primary", "color": "#000000"},
        {"file_path": "png/32/ui-kit/button-primary.png", "category": "ui-kit",
         "descriptive_name": "button-primary", "color": "#000000"},
        {"file_path": "png/64/ui-kit/button-primary.png", "category": "ui-kit",
         "descriptive_name": "button-primary", "color": "#000000"},
    ]
    (root / "index.json").write_text(json.dumps(index), encoding="utf-8")


# ---------------------------------------------------------------------------
# Primitive validators
# ---------------------------------------------------------------------------


def test_validate_svg_passes_for_valid_svg(tmp_path: Path) -> None:
    """`validate_svg` returns a list of issues (empty for valid SVG)."""
    svg = tmp_path / "ok.svg"
    _write_svg(svg, 32)
    assert validate_svg(svg, expected_size=32) == []


def test_validate_svg_rejects_malformed(tmp_path: Path) -> None:
    """Malformed XML is reported as an issue."""
    svg = tmp_path / "bad.svg"
    svg.write_text("<svg><rect></svg>", encoding="utf-8")  # unclosed rect
    issues = validate_svg(svg, expected_size=32)
    assert issues, "malformed SVG should produce at least one issue"


def test_validate_svg_rejects_wrong_size(tmp_path: Path) -> None:
    """SVG width/height not matching the expected size is flagged."""
    svg = tmp_path / "wrong.svg"
    _write_svg(svg, 32)
    issues = validate_svg(svg, expected_size=64)
    assert any("size" in i.lower() for i in issues)


def test_validate_svg_rejects_non_kebab_case(tmp_path: Path) -> None:
    """Filenames that aren't kebab-case are flagged."""
    svg = tmp_path / "BadName.svg"
    _write_svg(svg, 32)
    issues = validate_svg(svg, expected_size=32)
    assert any("kebab" in i.lower() or "case" in i.lower() for i in issues)


def test_validate_png_passes_for_valid_png(tmp_path: Path) -> None:
    """`validate_png` returns an empty list for a correct PNG."""
    png = tmp_path / "ok.png"
    _write_png(png, 32)
    assert validate_png(png, expected_size=32) == []


def test_validate_png_rejects_wrong_size(tmp_path: Path) -> None:
    """PNG whose pixel dimensions don't match the expected size is flagged."""
    png = tmp_path / "wrong.png"
    _write_png(png, 32)
    issues = validate_png(png, expected_size=64)
    assert any("size" in i.lower() or "dimension" in i.lower() for i in issues)


# ---------------------------------------------------------------------------
# Index validator
# ---------------------------------------------------------------------------


def test_validate_index_passes_when_files_exist(tmp_path: Path) -> None:
    """`validate_index` returns no issues when every index entry has a file."""
    _build_icon_set(tmp_path)
    index_path = tmp_path / "index.json"
    assert validate_index(index_path, root=tmp_path) == []


def test_validate_index_flags_missing_files(tmp_path: Path) -> None:
    """`validate_index` flags entries whose files are missing."""
    _build_icon_set(tmp_path)
    index_path = tmp_path / "index.json"
    # Delete one of the icon files but keep its entry in the index.
    (tmp_path / "svg" / "32" / "ui-kit" / "button-primary.svg").unlink()
    issues = validate_index(index_path, root=tmp_path)
    assert any("missing" in i.lower() or "not found" in i.lower() for i in issues)


def test_validate_index_rejects_malformed_json(tmp_path: Path) -> None:
    """Malformed index.json is reported."""
    index_path = tmp_path / "index.json"
    index_path.write_text("not json", encoding="utf-8")
    issues = validate_index(index_path, root=tmp_path)
    assert any("json" in i.lower() or "parse" in i.lower() for i in issues)


# ---------------------------------------------------------------------------
# Directory validator (the main CLI seam)
# ---------------------------------------------------------------------------


def test_validate_directory_passes_for_clean_set(tmp_path: Path) -> None:
    """`validate_directory` reports zero issues for a well-formed icon set."""
    _build_icon_set(tmp_path)
    report = validate_directory(tmp_path)
    assert report.ok, f"expected ok=True, issues={report.issues}"


def test_validate_directory_flags_missing_png(tmp_path: Path) -> None:
    """`validate_directory` reports missing PNG files for indexed entries."""
    _build_icon_set(tmp_path)
    (tmp_path / "png" / "32" / "ui-kit" / "button-primary.png").unlink()
    report = validate_directory(tmp_path)
    assert not report.ok
    assert any("png/32" in i for i in report.issues)


def test_validate_directory_rejects_no_index(tmp_path: Path) -> None:
    """`validate_directory` reports failure when index.json is absent."""
    _build_icon_set(tmp_path)
    (tmp_path / "index.json").unlink()
    report = validate_directory(tmp_path)
    assert not report.ok


def test_validation_report_serialises() -> None:
    """`ValidationReport` exposes counts and issues for inspection."""
    report = ValidationReport(ok=False, issues=["example"])
    assert report.ok is False
    assert report.issues == ["example"]
