"""Catalog loader (T6 helper).

Loads the project's `catalog.yaml` and exposes the categories mapping.
Used by the batch pipeline to enumerate base_concepts × modifiers and
derive concept names.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_catalog(path: Path) -> dict[str, Any]:
    """Load a catalog YAML file and return its `categories` mapping.

    The catalog file has shape `{"metadata": {...}, "categories": {...}}`.
    This function returns just the inner categories mapping so callers can
    iterate `cat.items()` directly.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"catalog at {path} must be a YAML mapping at the top level")
    categories = data.get("categories")
    if not isinstance(categories, dict):
        raise ValueError(f"catalog at {path} must define a 'categories' mapping")
    return categories


def get_category(categories: dict[str, Any], name: str) -> dict[str, Any]:
    """Return a single category entry or raise ValueError."""
    entry = categories.get(name)
    if not isinstance(entry, dict):
        raise ValueError(f"category {name!r} not found in catalog")
    return entry


def concept_names(entry: dict[str, Any]) -> list[str]:
    """Enumerate concept names by combining base_concepts and modifiers.

    Generates `base × modifier` pairs up to the entry's declared `count`.
    Names are kebab-case and collision-free (suffix `-2`, `-3`, ... if
    a duplicate would otherwise arise).
    """
    base = list(entry["base_concepts"])
    modifiers = list(entry["modifiers"])
    count = int(entry["count"])
    names: list[str] = []
    seen: set[str] = set()
    # Cartesian product, in deterministic order, until we have `count` names.
    for b in base:
        for m in modifiers:
            name = f"{b}-{m}"
            if name in seen:
                suffix = 2
                while f"{name}-{suffix}" in seen:
                    suffix += 1
                name = f"{name}-{suffix}"
            seen.add(name)
            names.append(name)
            if len(names) >= count:
                return names
    # If we still need more (capacity < count), pad with sequential suffixes.
    if len(names) < count:
        i = 0
        while len(names) < count:
            candidate = f"extra-{i}"
            while candidate in seen:
                i += 1
                candidate = f"extra-{i}"
            seen.add(candidate)
            names.append(candidate)
            i += 1
    return names
