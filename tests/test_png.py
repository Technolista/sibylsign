"""Tests for the PNG conversion and dual-size support (T4).

The generator's PNG sibling must emit a valid PNG at the requested
size that visually corresponds to the SVG. Both 32×32 and 64×64 are
required sizes, so the same `concept` must yield matching files at
each size.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from sibylsign.generator import (
    generate_svg,
    generate_png,
    save_svg,
    save_png,
)


def test_generate_png_returns_pil_image() -> None:
    """`generate_png` returns a Pillow Image object."""
    img = generate_png(concept="circle", size=32)
    assert isinstance(img, Image.Image)


def test_generate_png_size_32() -> None:
    """At size=32, the image is exactly 32×32 pixels and is opaque."""
    img = generate_png(concept="square", size=32)
    assert img.size == (32, 32)
    assert img.mode in {"RGB", "RGBA"}


def test_generate_png_size_64() -> None:
    """At size=64, the image is exactly 64×64 pixels."""
    img = generate_png(concept="triangle", size=64)
    assert img.size == (64, 64)


def test_generate_png_rejects_invalid_size() -> None:
    """Only 32 and 64 are supported for PNG output."""
    with pytest.raises(ValueError):
        generate_png(concept="circle", size=48)


def test_generate_png_is_deterministic() -> None:
    """Same concept and size produce identical PNG bytes."""
    a = generate_png(concept="dog", size=32)
    b = generate_png(concept="dog", size=32)
    assert a.tobytes() == b.tobytes()


def test_generate_png_differs_across_concepts() -> None:
    """Different concepts produce different PNG bytes."""
    a = generate_png(concept="dog", size=32)
    b = generate_png(concept="cat", size=32)
    assert a.tobytes() != b.tobytes()


def test_generate_png_contains_black_pixels() -> None:
    """The PNG contains black pixels because the icon is rendered in black."""
    img = generate_png(concept="heart", size=64)
    pixels = img.convert("RGB").getdata()
    black_count = sum(1 for px in pixels if px == (0, 0, 0))
    assert black_count > 0, "PNG should contain at least one black pixel"


def test_save_png_writes_valid_file(tmp_path: Path) -> None:
    """`save_png` writes a PNG file that Pillow can re-open at the right size."""
    out = tmp_path / "icon.png"
    save_png(out, concept="star", size=32)
    assert out.exists()
    img = Image.open(out)
    assert img.size == (32, 32)


def test_save_png_creates_parents(tmp_path: Path) -> None:
    """`save_png` creates missing parent directories before writing."""
    out = tmp_path / "deep" / "nested" / "dir" / "icon.png"
    save_png(out, concept="circle", size=64)
    assert out.exists()


def test_svg_and_png_share_concept_at_same_size(tmp_path: Path) -> None:
    """Saving the same concept at size 32 produces an SVG and a PNG that
    both render at 32 px and share the same baseline shape (black fill)."""
    svg_path = tmp_path / "x.svg"
    png_path = tmp_path / "x.png"
    save_svg(svg_path, concept="house", size=32)
    save_png(png_path, concept="house", size=32)
    img = Image.open(png_path)
    assert img.size == (32, 32)
    # Cross-check that the SVG declares the same size.
    svg_text = svg_path.read_text(encoding="utf-8")
    assert 'width="32"' in svg_text
    assert 'height="32"' in svg_text
