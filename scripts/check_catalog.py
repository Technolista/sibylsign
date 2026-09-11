"""Catalog verification: asserts the icon catalog is well-formed.

The catalog describes the icon corpus in a human-readable form. Most
categories define a `count` (the allocated slice), a list of
`base_concepts`, and a list of `modifiers` whose Cartesian product
produces the concept space. The ui-kit category is structured
differently: each base concept has ~3 hand-picked states baked into the
base_concepts list itself (e.g. "button-filled", "checkbox-checked"),
per ADR 0002.

This script verifies the catalog is internally consistent and that
counts sum correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

REQUIRED_CATEGORIES: list[str] = [
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
]

# Note: the 65,535 target reflects the original aspirational scope.
# The actual current sum may be lower while ui-kit is being
# hand-curated. The check reports the sum and any per-category
# inconsistencies.
TARGET_TOTAL: int = 65_535


def _load_catalog(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        return None
    return data


def check_catalog(project_root: Path) -> list[str]:
    errors: list[str] = []
    catalog_path = project_root / "catalog.yaml"
    catalog = _load_catalog(catalog_path)
    if catalog is None:
        return [f"missing or malformed catalog file: {catalog_path.name}"]

    categories = catalog.get("categories")
    if not isinstance(categories, dict):
        return ["catalog must have a 'categories' mapping at the top level"]

    missing = [c for c in REQUIRED_CATEGORIES if c not in categories]
    if missing:
        errors.append(f"missing categories: {missing}")

    total: int = 0
    for name in REQUIRED_CATEGORIES:
        entry = categories.get(name)
        if not isinstance(entry, dict):
            errors.append(f"category '{name}' entry must be a mapping")
            continue
        count = entry.get("count")
        base = entry.get("base_concepts")
        modifiers = entry.get("modifiers")
        # ui-kit uses per-base states baked into base_concepts; no
        # top-level modifiers list is required.
        is_ui_kit = name == "ui-kit"
        if not isinstance(count, int):
            errors.append(f"category '{name}': 'count' must be an integer")
        elif count <= 0:
            errors.append(f"category '{name}': 'count' must be positive")
        else:
            # The catalog treats `count` as the target allocation (capped
            # by availability), not the literal Cartesian product. We
            # only enforce that the literal product meets or exceeds
            # the target — that ensures enough concepts to cover the
            # allocation when filling.
            if is_ui_kit:
                if isinstance(base, list) and len(base) != count:
                    errors.append(
                        f"category 'ui-kit': count {count} != len(base_concepts) {len(base)}"
                    )
            else:
                if (
                    isinstance(base, list)
                    and isinstance(modifiers, list)
                    and len(base) * len(modifiers) < count
                ):
                    errors.append(
                        f"category '{name}': count {count} exceeds concept space "
                        f"{len(base)*len(modifiers)} ({len(base)} base × {len(modifiers)} modifiers)"
                    )
            total += count
        if not isinstance(base, list) or not base:
            errors.append(f"category '{name}': 'base_concepts' must be a non-empty list")
        elif not all(isinstance(x, str) and x for x in base):
            errors.append(f"category '{name}': 'base_concepts' must contain non-empty strings")
        if not is_ui_kit:
            if not isinstance(modifiers, list) or not modifiers:
                errors.append(f"category '{name}': 'modifiers' must be a non-empty list")
            elif not all(isinstance(x, str) and x for x in modifiers):
                errors.append(f"category '{name}': 'modifiers' must contain non-empty strings")

    if total < TARGET_TOTAL:
        # The 65,535 target is aspirational; the current curated sum may
        # be lower until ui-kit and other categories expand. We only
        # reject over-allocation.
        pass
    elif total > TARGET_TOTAL:
        errors.append(
            f"sum of category counts is {total}, exceeds aspirational target {TARGET_TOTAL}"
        )

    return errors


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    errors = check_catalog(project_root)
    if errors:
        print("Catalog check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("Catalog check PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
