"""Tests for the index file generation (T5).

The index is a JSON catalog of every icon in the project. It records
the file path, category, descriptive name, and color so that users can
search and select icons programmatically. The index is regenerated
atomically on each build.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sibylsign.index import IconEntry, IconIndex, build_entry, write_index


def test_icon_entry_required_fields() -> None:
    """`IconEntry` carries file_path, category, descriptive_name, and color."""
    entry = IconEntry(
        file_path="svg/32/animals/dog.svg",
        category="animals",
        descriptive_name="dog",
        color="#000000",
    )
    assert entry.file_path == "svg/32/animals/dog.svg"
    assert entry.category == "animals"
    assert entry.descriptive_name == "dog"
    assert entry.color == "#000000"


def test_icon_entry_rejects_invalid_color() -> None:
    """Only the project's mono-color palette (black) is allowed."""
    with pytest.raises(ValueError):
        IconEntry(
            file_path="svg/32/animals/dog.svg",
            category="animals",
            descriptive_name="dog",
            color="#ffffff",
        )


def test_icon_entry_kebab_case_name() -> None:
    """Descriptive names must be kebab-case (lowercase, hyphens, no spaces)."""
    with pytest.raises(ValueError):
        IconEntry(
            file_path="svg/32/animals/dog.svg",
            category="animals",
            descriptive_name="Dog Silhouette",
            color="#000000",
        )


def test_icon_entry_to_dict() -> None:
    """`IconEntry.to_dict()` produces a JSON-serialisable mapping."""
    entry = IconEntry(
        file_path="svg/32/animals/dog.svg",
        category="animals",
        descriptive_name="dog",
        color="#000000",
    )
    data = entry.to_dict()
    assert data["file_path"] == "svg/32/animals/dog.svg"
    assert data["category"] == "animals"
    assert data["descriptive_name"] == "dog"
    assert data["color"] == "#000000"


def test_build_entry_constructs_paths() -> None:
    """`build_entry` produces an IconEntry from a concept + category at the given size/format."""
    entry = build_entry(concept="dog", category="animals", size=32, fmt="svg")
    assert entry.file_path == "svg/32/animals/dog.svg"
    assert entry.category == "animals"
    assert entry.descriptive_name == "dog"


def test_build_entry_png_format() -> None:
    """`build_entry` handles the png format."""
    entry = build_entry(concept="cat", category="animals", size=64, fmt="png")
    assert entry.file_path == "png/64/animals/cat.png"


def test_build_entry_rejects_unsupported_format() -> None:
    """`build_entry` rejects formats other than svg/png."""
    with pytest.raises(ValueError):
        build_entry(concept="dog", category="animals", size=32, fmt="jpg")


def test_build_entry_rejects_unsupported_size() -> None:
    """`build_entry` rejects sizes other than 32/64."""
    with pytest.raises(ValueError):
        build_entry(concept="dog", category="animals", size=48, fmt="svg")


def test_icon_index_add_and_count() -> None:
    """`IconIndex` accumulates entries and reports a total count."""
    idx = IconIndex()
    idx.add(IconEntry(
        file_path="svg/32/animals/dog.svg",
        category="animals",
        descriptive_name="dog",
        color="#000000",
    ))
    assert idx.count == 1


def test_icon_index_empty() -> None:
    """A fresh index has zero entries and serialises to an empty list."""
    idx = IconIndex()
    assert idx.count == 0
    assert idx.to_list() == []


def test_write_index_writes_valid_json(tmp_path: Path) -> None:
    """`write_index` writes a JSON file parseable by standard tooling."""
    idx = IconIndex()
    idx.add(IconEntry(
        file_path="svg/32/animals/dog.svg",
        category="animals",
        descriptive_name="dog",
        color="#000000",
    ))
    out = tmp_path / "index.json"
    write_index(out, idx)
    text = out.read_text(encoding="utf-8")
    data = json.loads(text)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["file_path"] == "svg/32/animals/dog.svg"


def test_write_index_is_atomic(tmp_path: Path) -> None:
    """`write_index` writes atomically: no partial file remains on success."""
    idx = IconIndex()
    idx.add(IconEntry(
        file_path="svg/32/animals/dog.svg",
        category="animals",
        descriptive_name="dog",
        color="#000000",
    ))
    out = tmp_path / "index.json"
    write_index(out, idx)
    assert out.exists()
    assert out.stat().st_size > 0


def test_write_index_creates_parents(tmp_path: Path) -> None:
    """`write_index` creates missing parent directories."""
    out = tmp_path / "deep" / "nested" / "index.json"
    idx = IconIndex()
    idx.add(IconEntry(
        file_path="svg/32/animals/dog.svg",
        category="animals",
        descriptive_name="dog",
        color="#000000",
    ))
    write_index(out, idx)
    assert out.exists()
