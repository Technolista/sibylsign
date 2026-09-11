"""Batch generation pipeline (T6).

`generate_category` is the canonical entry point for producing the
icons in a single category. It reads the catalog, enumerates concepts
per the category's base_concepts × modifiers, and writes:

  - svg/32/<category>/<concept>.svg
  - svg/64/<category>/<concept>.svg
  - png/32/<category>/<concept>.png
  - png/64/<category>/<concept>.png

It also produces an `index.json` containing one entry per (format, size,
concept) tuple.
"""

from __future__ import annotations

from pathlib import Path

from .catalog import get_category, load_catalog, concept_names
from .generator import save_png, save_svg
from .index import IconIndex, build_entry, write_index


_SUPPORTED_SIZES: tuple[int, ...] = (32, 64)
_SUPPORTED_FORMATS: tuple[str, ...] = ("svg", "png")


def generate_category(
    catalog: Path | str,
    category: str,
    output_dir: Path | str,
    *,
    catalog_dir: Path | str | None = None,
) -> int:
    """Generate all icons for a single category.

    Args:
        catalog: path to the catalog YAML, or a name resolved relative
            to `catalog_dir` if provided.
        category: the category name (must exist in the catalog).
        output_dir: root directory under which `svg/`, `png/`, and
            `index.json` are written.
        catalog_dir: optional base directory for resolving `catalog`.

    Returns:
        The number of icons (concepts) generated.
    """
    catalog_path = Path(catalog)
    if not catalog_path.is_absolute() and catalog_dir is not None:
        catalog_path = Path(catalog_dir) / catalog_path
    catalog_data = load_catalog(catalog_path)
    entry = get_category(catalog_data, category)
    names = concept_names(entry)

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    index = IconIndex()
    for name in names:
        for size in _SUPPORTED_SIZES:
            for fmt in _SUPPORTED_FORMATS:
                target = output_root / fmt / str(size) / category / f"{name}.{fmt}"
                if fmt == "svg":
                    save_svg(target, concept=name, size=size)
                else:
                    save_png(target, concept=name, size=size)
                index.add(build_entry(concept=name, category=category, size=size, fmt=fmt))

    write_index(output_root / "index.json", index)
    return len(names)
