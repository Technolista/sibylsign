"""Tests for semantic UI kit icon archetypes."""

import xml.etree.ElementTree as ET
from sibylsign.generator import generate_svg

SVG_NS = "http://www.w3.org/2000/svg"


def _all_primitives(svg_root):
    """Yield every shape element in the SVG."""
    for tag in ("rect", "circle", "path", "polygon", "polyline", "line"):
        for el in svg_root.iter(f"{{{SVG_NS}}}{tag}"):
            yield tag, el


def test_button_primary_semantic_render() -> None:
    svg = generate_svg("button-primary", size=32)
    root = ET.fromstring(svg)
    # Filled primary: container has rx/ry via path -> at least one path element
    elements = list(_all_primitives(root))
    assert any(tag == "path" for tag, _ in elements)


def test_toggle_switch_semantic_render() -> None:
    svg = generate_svg("toggle-active", size=32)
    root = ET.fromstring(svg)
    # Filled toggle: pill path with cutout -> at least one path
    elements = list(_all_primitives(root))
    assert any(tag == "path" for tag, _ in elements)


def test_checkbox_semantic_render() -> None:
    svg = generate_svg("checkbox-outline", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1
