"""Tests for feedback UI kit icon archetypes."""

import xml.etree.ElementTree as ET
from sibylsign.generator import generate_svg

SVG_NS = "http://www.w3.org/2000/svg"


def _shapes(root):
    """Return all shape elements (path, rect, circle, polygon, polyline, line)."""
    out = []
    for tag in ("rect", "circle", "path", "polygon", "polyline", "line"):
        for el in root.iter(f"{{{SVG_NS}}}{tag}"):
            out.append((tag, el))
    return out


def test_alert_semantic_render() -> None:
    svg = generate_svg("alert-default", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 2


def test_badge_active_semantic_render() -> None:
    svg = generate_svg("badge-active", size=32)
    root = ET.fromstring(svg)
    shapes = _shapes(root)
    # Active badge: filled outer circle with hollow center => path
    assert any(t == "path" for t, _ in shapes)


def test_toast_active_semantic_render() -> None:
    svg = generate_svg("toast-active", size=32)
    root = ET.fromstring(svg)
    shapes = _shapes(root)
    # Active toast: bottom panel is a path with cutouts
    assert any(t == "path" for t, _ in shapes)


def test_spinner_default_semantic_render() -> None:
    svg = generate_svg("spinner-default", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    assert len(circles) >= 4


def test_progress_bar_active_semantic_render() -> None:
    svg = generate_svg("progress-bar-active", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 2


def test_skeleton_default_semantic_render() -> None:
    svg = generate_svg("skeleton-default", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 3


def test_placeholder_default_semantic_render() -> None:
    svg = generate_svg("placeholder-default", size=32)
    root = ET.fromstring(svg)
    lines = [el for el in root.iter(f"{{{SVG_NS}}}line")]
    assert len(lines) >= 3


def test_loader_default_semantic_render() -> None:
    svg = generate_svg("loader-default", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    assert len(circles) >= 3


def test_indicator_active_semantic_render() -> None:
    svg = generate_svg("indicator-active", size=32)
    root = ET.fromstring(svg)
    shapes = _shapes(root)
    # Active indicator: filled circle with hollow ring => path
    assert any(t == "path" for t, _ in shapes)


def test_counter_default_semantic_render() -> None:
    svg = generate_svg("counter-default", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1


def test_notification_default_semantic_render() -> None:
    svg = generate_svg("notification-default", size=32)
    root = ET.fromstring(svg)
    paths = [el for el in root.iter(f"{{{SVG_NS}}}path")]
    assert len(paths) >= 1


def test_callout_default_semantic_render() -> None:
    svg = generate_svg("callout-default", size=32)
    root = ET.fromstring(svg)
    rects = [el for el in root.iter(f"{{{SVG_NS}}}rect")]
    assert len(rects) >= 1


def test_error_filled_semantic_render() -> None:
    svg = generate_svg("error-filled", size=32)
    root = ET.fromstring(svg)
    shapes = _shapes(root)
    # Filled error: triangle path with exclamation cutouts
    assert any(t == "path" for t, _ in shapes)


def test_warning_default_semantic_render() -> None:
    svg = generate_svg("warning-default", size=32)
    root = ET.fromstring(svg)
    polys = [el for el in root.iter(f"{{{SVG_NS}}}polygon")]
    assert len(polys) >= 1


def test_info_default_semantic_render() -> None:
    svg = generate_svg("info-default", size=32)
    root = ET.fromstring(svg)
    circles = [el for el in root.iter(f"{{{SVG_NS}}}circle")]
    assert len(circles) >= 1


def test_success_filled_semantic_render() -> None:
    svg = generate_svg("success-filled", size=32)
    root = ET.fromstring(svg)
    shapes = _shapes(root)
    # Filled success: circle path with check cutout
    assert any(t == "path" for t, _ in shapes)
