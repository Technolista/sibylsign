"""Icon index (T5).

The index is a JSON catalog of every icon in the project. It records the
file path, category, descriptive name, and color so that users can search
and select icons programmatically. The index is regenerated atomically
on each build by the batch pipeline.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path

_VALID_SIZES: frozenset[int] = frozenset({32, 64})
_VALID_FORMATS: frozenset[str] = frozenset({"svg", "png"})
_VALID_COLORS: frozenset[str] = frozenset({"#000000"})
_KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _validate_color(color: str) -> str:
    if color not in _VALID_COLORS:
        raise ValueError(
            f"color must be one of {sorted(_VALID_COLORS)}, got {color!r}"
        )
    return color


def _validate_descriptive_name(name: str) -> str:
    if not _KEBAB_RE.match(name):
        raise ValueError(
            f"descriptive_name must be kebab-case (lowercase, digits, hyphens), got {name!r}"
        )
    return name


@dataclass(frozen=True)
class IconEntry:
    """A single icon's metadata entry."""

    file_path: str
    category: str
    descriptive_name: str
    color: str = "#000000"

    def __post_init__(self) -> None:
        _validate_color(self.color)
        _validate_descriptive_name(self.descriptive_name)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def build_entry(concept: str, category: str, size: int, fmt: str) -> IconEntry:
    """Construct an `IconEntry` from a concept + category at the given size/format."""
    if size not in _VALID_SIZES:
        raise ValueError(f"size must be one of {sorted(_VALID_SIZES)}, got {size!r}")
    if fmt not in _VALID_FORMATS:
        raise ValueError(f"fmt must be one of {sorted(_VALID_FORMATS)}, got {fmt!r}")
    descriptive_name = _validate_descriptive_name(concept.strip().lower())
    return IconEntry(
        file_path=f"{fmt}/{size}/{category}/{descriptive_name}.{fmt}",
        category=category,
        descriptive_name=descriptive_name,
        color="#000000",
    )


@dataclass
class IconIndex:
    """An accumulating collection of `IconEntry` records."""

    entries: list[IconEntry] = field(default_factory=list)

    def add(self, entry: IconEntry) -> None:
        self.entries.append(entry)

    @property
    def count(self) -> int:
        return len(self.entries)

    def to_list(self) -> list[dict[str, str]]:
        return [entry.to_dict() for entry in self.entries]


def write_index(path: Path, index: IconIndex) -> Path:
    """Write the index as JSON to `path`, atomically. Creates parent dirs."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(index.to_list(), ensure_ascii=False, indent=2)
    # Atomic write: write to a temp file in the same directory, then rename.
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    return path
