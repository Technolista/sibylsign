"""SVG icon generator.

Public seam for T3. The generator takes a concept string and a target
size (32 or 64) and produces a well-formed, mono-color-black SVG that
is distinguishable across concepts but deterministic for the same
concept.
"""

from __future__ import annotations

import enum
import hashlib
import io
from pathlib import Path

import cairosvg
import svgwrite
from PIL import Image


class SVGColor(enum.Enum):
    """The project's mono-color palette. Currently only black."""

    BLACK = "#000000"


_VALID_SIZES: frozenset[int] = frozenset({32, 64})


def _validate_size(size: int) -> int:
    if size not in _VALID_SIZES:
        raise ValueError(
            f"size must be one of {sorted(_VALID_SIZES)}, got {size!r}"
        )
    return size


def _normalise_concept(concept: str) -> str:
    return concept.strip().lower()


def _seeded_shape_plan(concept: str, size: int) -> list[dict]:
    """Return a deterministic shape plan derived from the concept string.

    The plan is computed from a SHA-256 digest of the concept, so the
    same concept always produces the same plan and different concepts
    diverge into different shape compositions. The first layer is
    always a filled shape (circle, square, or triangle) so that every
    icon contains a visible mono-color mark.
    """
    digest = hashlib.sha256(f"{concept}|{size}".encode("utf-8")).digest()
    filled_pool = ["circle", "square", "triangle"]
    any_pool = ["circle", "square", "triangle", "line", "arc"]
    layers: list[dict] = []
    base_kind = filled_pool[digest[0] % len(filled_pool)]
    layers.append({
        "kind": base_kind,
        "cx": digest[4] % size,
        "cy": digest[5] % size,
        "r": max(2, digest[6] % max(2, size // 3)),
        "i": 0,
    })
    extra = digest[1] % 3  # 0..2 additional layers
    for i in range(extra):
        kind = any_pool[digest[2 + i] % len(any_pool)]
        cx = digest[8 + 2 * i] % size
        cy = digest[9 + 2 * i] % size
        r = max(2, digest[10 + i] % max(2, size // 4))
        layers.append({"kind": kind, "cx": cx, "cy": cy, "r": r, "i": i + 1})
    return layers


def _draw_shape(drawing: svgwrite.Drawing, shape: dict, size: int) -> None:
    color = SVGColor.BLACK.value
    cx, cy, r = shape["cx"], shape["cy"], shape["r"]
    kind = shape["kind"]
    if kind == "circle":
        drawing.add(drawing.circle(center=(cx, cy), r=r, fill=color))
    elif kind == "square":
        s = max(2, r)
        drawing.add(drawing.rect(insert=(cx - s // 2, cy - s // 2), size=(s, s), fill=color))
    elif kind == "triangle":
        # Equilateral triangle inscribed around (cx, cy)
        p1 = (cx, cy - r)
        p2 = (cx - r, cy + r)
        p3 = (cx + r, cy + r)
        drawing.add(drawing.polygon(points=[p1, p2, p3], fill=color))
    elif kind == "line":
        x1, y1 = cx, cy
        x2 = (cx + r) % size
        y2 = (cy + r) % size
        drawing.add(drawing.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=max(1, size // 32)))
    elif kind == "arc":
        rx = max(2, r)
        ry = max(2, r // 2 + 1)
        drawing.add(
            drawing.path(
                d=f"M {cx - rx},{cy} a {rx},{ry} 0 1 0 {2 * rx},0",
                fill="none",
                stroke=color,
                stroke_width=max(1, size // 32),
            )
        )


def generate_svg(concept: str, size: int = 32, color: SVGColor = SVGColor.BLACK) -> str:
    """Generate a mono-color-black SVG for the given concept.

    Args:
        concept: a short kebab-case identifier for the icon (e.g. "dog").
        size: target pixel size. Must be 32 or 64.
        color: the mono-color fill. Defaults to black.

    Returns:
        A well-formed SVG document as a string.
    """
    _validate_size(size)
    normalised = _normalise_concept(concept)
    drawing = svgwrite.Drawing(size=(size, size))
    drawing.viewbox(0, 0, size, size)
    for shape in _seeded_shape_plan(normalised, size):
        _draw_shape(drawing, shape, size)
    return drawing.tostring()


def save_svg(path: Path, concept: str, size: int = 32, color: SVGColor = SVGColor.BLACK) -> Path:
    """Generate and save an SVG to `path`. Creates parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_svg(concept=concept, size=size, color=color), encoding="utf-8")
    return path


def generate_png(concept: str, size: int = 32, color: SVGColor = SVGColor.BLACK) -> Image.Image:
    """Generate a Pillow Image for the given concept at the requested size.

    The PNG is rendered from the same SVG the generator produces, ensuring
    visual correspondence with the SVG output. Only 32 and 64 are valid
    sizes.
    """
    _validate_size(size)
    svg_text = generate_svg(concept=concept, size=size, color=color)
    png_bytes = cairosvg.svg2png(
        bytestring=svg_text.encode("utf-8"),
        output_width=size,
        output_height=size,
    )
    return Image.open(io.BytesIO(png_bytes)).copy()


def save_png(path: Path, concept: str, size: int = 32, color: SVGColor = SVGColor.BLACK) -> Path:
    """Generate and save a PNG to `path`. Creates parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = generate_png(concept=concept, size=size, color=color)
    # Convert to RGB for a compact, opaque PNG without alpha.
    img.convert("RGB").save(path, format="PNG")
    return path
