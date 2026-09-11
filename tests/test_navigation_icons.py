"""Tests for navigation UI kit icon archetypes."""

import xml.etree.ElementTree as ET
from sibylsign.generator import generate_svg

SVG_NS = "http://www.w3.org/2000/svg"


def test_menu_semantic_render() -> None:
    svg = generate_svg("menu-default", size=32)
    root = ET.fromstring(svg)
    # Three horizontal bars expected
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 3


def test_dropdown_open_semantic_render() -> None:
    svg = generate_svg("dropdown-open", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 2


def test_tab_active_semantic_render() -> None:
    svg = generate_svg("tab-active", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1


def test_pagination_semantic_render() -> None:
    svg = generate_svg("pagination-default", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    assert len(circles) >= 2


def test_breadcrumb_active_semantic_render() -> None:
    svg = generate_svg("breadcrumb-active", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 3


def test_navbar_semantic_render() -> None:
    svg = generate_svg("navbar-default", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1


def test_sidebar_active_semantic_render() -> None:
    svg = generate_svg("sidebar-active", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1


def test_stepper_active_semantic_render() -> None:
    svg = generate_svg("stepper-active", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    assert len(circles) >= 2


def test_wizard_default_semantic_render() -> None:
    svg = generate_svg("wizard-default", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1


def test_step_completed_semantic_render() -> None:
    svg = generate_svg("step-completed", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    assert len(circles) >= 1
