"""Tests for the batch generation pipeline (T6).

The pipeline is the canonical way to generate icons: it reads the
catalog for a category and emits SVGs (32 and 64), PNGs (32 and 64),
and a fresh index.json entry for each concept. This module's tests
verify the public surface (entries produced, files written, count
matches the catalog) rather than internal composition details.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sibylsign.catalog import load_catalog
from sibylsign.pipeline import generate_category


def _make_workspace(tmp_path: Path) -> tuple[Path, Path]:
    """Create a small catalog on disk and return (catalog_path, output_dir)."""
    catalog_path = tmp_path / "catalog.yaml"
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    return catalog_path, output_dir


def _write_minimal_catalog(path: Path, categories: dict) -> None:
    import yaml
    path.write_text(yaml.safe_dump(categories, allow_unicode=True), encoding="utf-8")


def test_generate_category_returns_count(tmp_path: Path) -> None:
    """`generate_category` returns the number of icons produced."""
    catalog_path, output_dir = _make_workspace(tmp_path)
    _write_minimal_catalog(
        catalog_path,
        {
            "categories": {
                "ui-kit": {
                    "count": 6,
                    "base_concepts": ["button", "input", "checkbox"],
                    "modifiers": ["primary", "secondary"],
                }
            }
        },
    )
    count = generate_category(
        catalog="catalog.yaml",
        category="ui-kit",
        output_dir=output_dir,
        catalog_dir=tmp_path,
    )
    assert count == 6


def test_generate_category_writes_svg_and_png_at_both_sizes(tmp_path: Path) -> None:
    """`generate_category` writes SVG and PNG files at 32 and 64 for each concept."""
    catalog_path, output_dir = _make_workspace(tmp_path)
    _write_minimal_catalog(
        catalog_path,
        {
            "categories": {
                "ui-kit": {
                    "count": 2,
                    "base_concepts": ["button", "input"],
                    "modifiers": ["primary"],
                }
            }
        },
    )
    generate_category(
        catalog=catalog_path,
        category="ui-kit",
        output_dir=output_dir,
        catalog_dir=tmp_path,
    )
    for name in ("button-primary", "input-primary"):
        for fmt in ("svg", "png"):
            for size in (32, 64):
                p = output_dir / fmt / str(size) / "ui-kit" / f"{name}.{fmt}"
                assert p.exists(), f"missing: {p}"


def test_generate_category_writes_index_json(tmp_path: Path) -> None:
    """`generate_category` writes an index.json describing every produced file."""
    catalog_path, output_dir = _make_workspace(tmp_path)
    _write_minimal_catalog(
        catalog_path,
        {
            "categories": {
                "ui-kit": {
                    "count": 3,
                    "base_concepts": ["button", "input"],
                    "modifiers": ["primary", "secondary"],
                }
            }
        },
    )
    generate_category(
        catalog=catalog_path,
        category="ui-kit",
        output_dir=output_dir,
        catalog_dir=tmp_path,
    )
    index_path = output_dir / "index.json"
    assert index_path.exists()
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    # 3 concepts × (2 sizes × 2 formats) = 12 index entries.
    assert len(data) == 12


def test_generate_category_index_has_metadata_for_each_format(tmp_path: Path) -> None:
    """`generate_category` records entries for both svg and png at both sizes."""
    catalog_path, output_dir = _make_workspace(tmp_path)
    _write_minimal_catalog(
        catalog_path,
        {
            "categories": {
                "ui-kit": {
                    "count": 1,
                    "base_concepts": ["button"],
                    "modifiers": ["primary"],
                }
            }
        },
    )
    generate_category(
        catalog=catalog_path,
        category="ui-kit",
        output_dir=output_dir,
        catalog_dir=tmp_path,
    )
    data = json.loads((output_dir / "index.json").read_text(encoding="utf-8"))
    file_paths = {entry["file_path"] for entry in data}
    expected = {
        "svg/32/ui-kit/button-primary.svg",
        "svg/64/ui-kit/button-primary.svg",
        "png/32/ui-kit/button-primary.png",
        "png/64/ui-kit/button-primary.png",
    }
    assert expected.issubset(file_paths)


def test_generate_category_rejects_unknown_category(tmp_path: Path) -> None:
    """`generate_category` raises if the category is not in the catalog."""
    catalog_path, output_dir = _make_workspace(tmp_path)
    _write_minimal_catalog(
        catalog_path,
        {
            "categories": {
                "ui-kit": {
                    "count": 1,
                    "base_concepts": ["button"],
                    "modifiers": ["primary"],
                }
            }
        },
    )
    with pytest.raises(ValueError):
        generate_category(
            catalog=catalog_path,
            category="unknown",
            output_dir=output_dir,
            catalog_dir=tmp_path,
        )


def test_load_catalog_helper_reads_yaml(tmp_path: Path) -> None:
    """`load_catalog` reads a YAML file and returns the categories mapping."""
    import yaml
    p = tmp_path / "catalog.yaml"
    p.write_text(yaml.safe_dump({"categories": {"x": {"count": 1}}}), encoding="utf-8")
    cat = load_catalog(p)
    assert "x" in cat
