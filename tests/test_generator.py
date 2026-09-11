"""Tests for the SVG icon generator (T3).

The generator is the canonical seam for the project: any icon the batch
pipeline produces must come through `generate_svg(concept)`. These tests
assert the public interface (output is well-formed SVG, renders, and is
distinguishable across concepts) rather than internal composition details.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from sibylsign.generator import generate_svg, save_svg, SVGColor

SVG_NS = "http://www.w3.org/2000/svg"


def test_generator_module_importable() -> None:
    """The generator module exists and exposes `generate_svg`."""
    from sibylsign import generator
    assert callable(generator.generate_svg)


def test_generate_svg_returns_string() -> None:
    """`generate_svg` returns an SVG document as a string."""
    svg = generate_svg(concept="circle", size=32)
    assert isinstance(svg, str)
    assert svg.startswith("<?xml") or "<svg" in svg


def test_generate_svg_is_well_formed_xml() -> None:
    """The generated SVG parses as XML and contains the expected root element."""
    svg = generate_svg(concept="square", size=32)
    root = ET.fromstring(svg)
    assert root.tag == f"{{{SVG_NS}}}svg"
    assert root.get("width") == "32"
    assert root.get("height") == "32"


def test_generate_svg_default_color_is_black() -> None:
    """The default color is solid black (no transparency, no grayscale)."""
    svg = generate_svg(concept="triangle", size=32)
    root = ET.fromstring(svg)
    # Find any element with a fill attribute and assert it resolves to black.
    fills = [
        el.get("fill")
        for el in root.iter()
        if el.get("fill") is not None and el.get("fill") != "none"
    ]
    assert fills, "generated SVG should contain filled shapes"
    for fill in fills:
        normalised = fill.strip().lower()
        assert normalised in {"black", "#000", "#000000", "rgb(0,0,0)", "#000000ff"}


def test_generate_svg_rejects_invalid_size() -> None:
    """Only the agreed-upon sizes (32 and 64) are supported."""
    with pytest.raises(ValueError):
        generate_svg(concept="circle", size=16)


def test_generate_svg_is_deterministic_per_concept() -> None:
    """Same concept yields identical SVG output (a property of the generator)."""
    a = generate_svg(concept="dog", size=32)
    b = generate_svg(concept="dog", size=32)
    assert a == b


def test_generate_svg_differs_across_concepts() -> None:
    """Different concepts produce different SVGs."""
    a = generate_svg(concept="dog", size=32)
    b = generate_svg(concept="cat", size=32)
    assert a != b


def test_generate_svg_supports_64_size() -> None:
    """The 64×64 size is also valid."""
    svg = generate_svg(concept="star", size=64)
    root = ET.fromstring(svg)
    assert root.get("width") == "64"
    assert root.get("height") == "64"


def test_save_svg_writes_file(tmp_path: Path) -> None:
    """`save_svg` writes the SVG to disk at the requested path."""
    out = tmp_path / "icon.svg"
    save_svg(out, concept="heart", size=32)
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "<svg" in text


def test_save_svg_creates_parent_directories(tmp_path: Path) -> None:
    """`save_svg` creates any missing parent directories before writing."""
    out = tmp_path / "deep" / "nested" / "dir" / "icon.svg"
    save_svg(out, concept="circle", size=32)
    assert out.exists()


def test_svg_color_enum_has_black() -> None:
    """`SVGColor` exposes a black member matching the project's mono-color rule."""
    assert SVGColor.BLACK.value.lower() in {"black", "#000", "#000000"}
