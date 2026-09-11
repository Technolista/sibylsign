"""Tests for semantic UI kit icon archetypes."""

import xml.etree.ElementTree as ET
from sibylsign.generator import generate_svg

SVG_NS = "http://www.w3.org/2000/svg"


def test_button_primary_semantic_render() -> None:
    svg = generate_svg("button-primary", size=32)
    root = ET.fromstring(svg)
    # Check that root contains a rect with rx/ry
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1
    assert "rx" in rects[0].attrib


def test_toggle_switch_semantic_render() -> None:
    svg = generate_svg("toggle-active", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1
    assert len(circles) >= 1


def test_checkbox_semantic_render() -> None:
    svg = generate_svg("checkbox-outline", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1
