"""UI-Kit Semantic Icon Design & Rendering Engine.

This module provides handcrafted archetypes and modifier rules for UI kit
concepts so that every generated icon is visually recognizable, properly
aligned, padded within the canvas (no clipping), and distinct.

All icons render as solid black on transparent background. Filled variants
that would traditionally use a contrasting white inner mark instead use SVG
`evenodd` paths to create actual cutouts so the icons stay monochromatic.
"""

from __future__ import annotations

import math
from typing import Callable, Sequence
import svgwrite

# Canvas dimensions & grid rules
# For size=32: padding=3px, content box [3, 3] to [29, 29] (26x26)
# For size=64: scaled 2x


# -------------------------------------------------------------------------
# Path / cutout helpers (monochrome, transparent background)
# -------------------------------------------------------------------------

def _rect_d(x: float, y: float, w: float, h: float) -> str:
    return f"M {x},{y} h {w} v {h} h {-w} Z"


def _circle_d(cx: float, cy: float, r: float) -> str:
    return (
        f"M {cx - r},{cy} "
        f"a {r},{r} 0 1,0 {2 * r},0 "
        f"a {r},{r} 0 1,0 {-2 * r},0 Z"
    )


def _add_evenodd(dwg: svgwrite.Drawing, subpaths: Sequence[str], color: str) -> svgwrite.path.Path:
    """Create a single path that combines outer subpath(s) with inner cutout(s)
    using `fill-rule="evenodd"` so the inner shapes become real holes.
    """
    d = " ".join(subpaths)
    p = dwg.path(d=d, fill=color)
    p["fill-rule"] = "evenodd"
    dwg.add(p)
    return p


def _add_rect_with_rect_holes(
    dwg: svgwrite.Drawing,
    x: float,
    y: float,
    w: float,
    h: float,
    color: str,
    holes: Sequence[tuple[float, float, float, float]] = (),
    rx: float = 0.0,
) -> svgwrite.path.Path:
    """Rectangle with rectangular holes via evenodd path."""
    if rx > 0:
        outer_d = (
            f"M {x + rx},{y} "
            f"h {w - 2 * rx} "
            f"a {rx},{rx} 0 0,1 {rx},{rx} "
            f"v {h - 2 * rx} "
            f"a {rx},{rx} 0 0,1 {-rx},{rx} "
            f"h {-(w - 2 * rx)} "
            f"a {rx},{rx} 0 0,1 {-rx},{-rx} "
            f"v {-(h - 2 * rx)} "
            f"a {rx},{rx} 0 0,1 {rx},{-rx} Z"
        )
    else:
        outer_d = _rect_d(x, y, w, h)
    subpaths = [outer_d]
    for (hx, hy, hw, hh) in holes:
        subpaths.append(_rect_d(hx, hy, hw, hh))
    return _add_evenodd(dwg, subpaths, color)


def _add_circle_with_circle_holes(
    dwg: svgwrite.Drawing,
    cx: float,
    cy: float,
    r: float,
    color: str,
    holes: Sequence[tuple[float, float, float]] = (),
) -> svgwrite.path.Path:
    """Circle with circular cutouts via evenodd path."""
    subpaths = [_circle_d(cx, cy, r)]
    for (icx, icy, ir) in holes:
        subpaths.append(_circle_d(icx, icy, ir))
    return _add_evenodd(dwg, subpaths, color)


def _add_polygon_with_polygon_holes(
    dwg: svgwrite.Drawing,
    outer: Sequence[tuple[float, float]],
    color: str,
    holes: Sequence[Sequence[tuple[float, float]]] = (),
) -> svgwrite.path.Path:
    """Polygon with polygonal cutouts via evenodd path."""
    outer_d = "M " + " L ".join(f"{x},{y}" for x, y in outer) + " Z"
    subpaths = [outer_d]
    for hole in holes:
        hole_d = "M " + " L ".join(f"{x},{y}" for x, y in hole) + " Z"
        subpaths.append(hole_d)
    return _add_evenodd(dwg, subpaths, color)


def _add_checkmark_hole_subpath(
    cx: float, cy: float, s: float, thickness: float
) -> str:
    """Build a closed subpath shaped like a checkmark so it can cut a hole.

    The checkmark is a thin parallelogram stroked along the V path.
    """
    p1 = (cx - 5 * s, cy)
    p2 = (cx - 1.5 * s, cy + 4 * s)
    p3 = (cx + 5 * s, cy - 4 * s)
    off = thickness / 2
    # Build a closed polygon by offsetting each segment perpendicular to its direction.
    a = (p1[0], p1[1] - off)
    b = (p2[0] - off, p2[1] - off)
    c = (p3[0] + off, p3[1] - off)
    d = (p3[0], p3[1] + off)
    e = (p2[0] + off, p2[1] + off)
    f = (p1[0], p1[1] + off)
    pts = [a, b, c, d, e, f]
    return "M " + " L ".join(f"{x},{y}" for x, y in pts) + " Z"


def _add_exclamation_hole_subpath(
    cx: float, cy: float, s: float, bar_w: float, dot_r: float
) -> tuple[str, str]:
    """Build two closed subpaths (bar + dot) for an exclamation cutout."""
    bar_h = 5 * s
    bar_x = cx - bar_w / 2
    bar_y = cy - 4 * s
    bar_subpath = _rect_d(bar_x, bar_y, bar_w, bar_h)
    # Dot: small circle
    dot_subpath = _circle_d(cx, cy + 6 * s, dot_r)
    return bar_subpath, dot_subpath


def _add_i_mark_hole_subpaths(
    cx: float, cy: float, s: float, dot_r: float, bar_w: float, bar_h: float
) -> tuple[str, str]:
    """Build two closed subpaths (top dot + lower bar) for an 'i' cutout."""
    dot = _circle_d(cx, cy - 4 * s, dot_r)
    bar = _rect_d(cx - bar_w / 2, cy - 1 * s, bar_w, bar_h)
    return dot, bar


# -------------------------------------------------------------------------
# Concept parsing
# -------------------------------------------------------------------------

def _parse_concept(concept: str) -> tuple[str, str]:
    """Parse a concept name like 'button-primary' into (base, modifier)."""
    parts = concept.strip().lower().split("-")
    multi_word_bases = {
        "icon-button", "progress-bar", "header-cell", "tree-view",
        "breadcrumb-1", "checkbox-1", "radio-1", "toggle-1", "input-1",
        "file-upload", "file-download", "drag-handle", "resize-handle",
        "circle-1", "square-1", "triangle-1", "diamond-1", "stopwatch-1", "timer-1"
    }
    for mwb in multi_word_bases:
        if concept.startswith(mwb + "-"):
            return mwb, concept[len(mwb) + 1:]
    if len(parts) >= 2:
        return parts[0], "-".join(parts[1:])
    return parts[0], "default"


# -------------------------------------------------------------------------
# Archetype Renderers (Controls)
# -------------------------------------------------------------------------

def render_button(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    filled = modifier in {"filled", "primary", "secondary", "tertiary", "active", "pressed", "selected"}
    rx = 2 * s if modifier in {"square", "dense"} else 6 * s if modifier in {"rounded", "pill"} else 4 * s
    w = 26 * s
    h = 16 * s
    x = (size - w) / 2
    y = (size - h) / 2

    if filled:
        holes: list[tuple[float, float, float, float]] = []
        if modifier not in {"empty"}:
            label_w = 12 * s if modifier in {"small", "compact"} else 16 * s
            label_x = (size - label_w) / 2
            label_y = size / 2 - 1 * s
            holes.append((label_x, label_y, label_w, 2 * s))
            if modifier in {"with-icon", "secondary"}:
                holes.append((x + 3 * s, size / 2 - 1.5 * s, 3 * s, 3 * s))
        _add_rect_with_rect_holes(dwg, x, y, w, h, color, holes=holes, rx=rx)
        if modifier == "loading":
            dwg.add(dwg.circle(center=(size / 2, size / 2), r=3 * s, fill="none", stroke=color, stroke_width=1.5 * s, stroke_dasharray=f"{3*s},{2*s}"))
    else:
        sw = 2.5 * s if modifier in {"thick", "prominent"} else 1 * s if modifier in {"thin", "minimal"} else 1.8 * s
        if modifier != "borderless":
            dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=sw))
        label_w = 12 * s if modifier in {"small", "compact"} else 16 * s
        dwg.add(dwg.line(start=((size - label_w) / 2, size / 2), end=((size + label_w) / 2, size / 2), stroke=color, stroke_width=2 * s))
        if modifier == "with-icon":
            dwg.add(dwg.circle(center=(x + 4 * s, size / 2), r=1.5 * s, fill="none", stroke=color, stroke_width=1 * s))
            dwg.add(dwg.line(start=(x + 7 * s, size / 2), end=(x + 12 * s, size / 2), stroke=color, stroke_width=1 * s))

    if modifier in {"disabled", "muted"}:
        dwg.add(dwg.line(start=(x + 2 * s, y + h - 2 * s), end=(x + w - 2 * s, y + 2 * s), stroke=color, stroke_width=1.5 * s))


def render_input(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w = 26 * s
    h = 14 * s
    x = (size - w) / 2
    y = (size - h) / 2
    rx = 2 * s if modifier != "square" else 0

    sw = 2.5 * s if modifier in {"focused", "active", "thick"} else 1.5 * s
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=sw))

    if modifier in {"focused", "active"}:
        dwg.add(dwg.line(start=(x + 5 * s, y + 3 * s), end=(x + 5 * s, y + h - 3 * s), stroke=color, stroke_width=1.5 * s))
    elif modifier in {"filled", "primary"}:
        dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + 16 * s, size / 2), stroke=color, stroke_width=2 * s))
    elif modifier == "with-icon":
        dwg.add(dwg.circle(center=(x + 4.5 * s, size / 2), r=2 * s, fill="none", stroke=color, stroke_width=1 * s))
        dwg.add(dwg.line(start=(x + 9 * s, size / 2), end=(x + 18 * s, size / 2), stroke=color, stroke_width=1.5 * s))
    elif modifier in {"disabled", "muted"}:
        dwg.add(dwg.line(start=(x, y + h), end=(x + w, y), stroke=color, stroke_width=1.2 * s))
    else:
        dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + 12 * s, size / 2), stroke=color, stroke_width=1.5 * s, stroke_dasharray=f"{2*s},{2*s}"))


def render_checkbox(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    box_size = 18 * s
    x = (size - box_size) / 2
    y = (size - box_size) / 2
    rx = 3 * s if modifier in {"rounded", "default"} else 0

    is_checked = modifier in {"checked", "selected", "active", "filled", "primary", "success"}
    if is_checked:
        # Filled square with a check-mark cutout via evenodd
        outer = [
            (x, y),
            (x + box_size, y),
            (x + box_size, y + box_size),
            (x, y + box_size),
        ]
        # Build the check mark as a thin polygon hole
        cx_c = x + box_size / 2
        cy_c = y + box_size / 2 + 1 * s
        check_d = _add_checkmark_hole_subpath(cx_c, cy_c, s * 0.9, 2.5 * s)
        subpaths = ["M " + " L ".join(f"{px},{py}" for px, py in outer) + " Z", check_d]
        _add_evenodd(dwg, subpaths, color)
    else:
        dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=2 * s))
        if modifier == "intermediate":
            dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + box_size - 4 * s, size / 2), stroke=color, stroke_width=2 * s))


def render_radio(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    r = 10 * s
    cx, cy = size / 2, size / 2
    is_selected = modifier in {"selected", "active", "checked", "filled", "primary", "on"}

    if is_selected:
        # Filled outer circle with a hollow inner circle (transparent ring)
        _add_circle_with_circle_holes(dwg, cx, cy, r, color, holes=[(cx, cy, 3.5 * s)])
    else:
        dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=2 * s))
        if modifier in {"hover", "focused"}:
            dwg.add(dwg.circle(center=(cx, cy), r=3 * s, fill=color))


def render_toggle(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w = 26 * s
    h = 14 * s
    x = (size - w) / 2
    y = (size - h) / 2
    r = h / 2

    is_on = modifier in {"active", "checked", "filled", "primary", "selected", "open", "expanded"}

    if is_on:
        # Filled pill with knob-shaped hole on the right side
        knob_cx = x + w - r
        knob_cy = y + r
        knob_r = r - 2 * s
        # Build a rounded pill subpath manually for evenodd
        pill_outer = (
            f"M {x + r},{y} "
            f"h {w - 2 * r} "
            f"a {r},{r} 0 0,1 0,{h} "
            f"h {-(w - 2 * r)} "
            f"a {r},{r} 0 0,1 0,{-h} Z"
        )
        knob_hole = _circle_d(knob_cx, knob_cy, knob_r)
        _add_evenodd(dwg, [pill_outer, knob_hole], color)
    else:
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=r, ry=r, fill="none", stroke=color, stroke_width=2 * s))
        dwg.add(dwg.circle(center=(x + r, y + r), r=r - 3 * s, fill=color))


def render_slider(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    is_vertical = modifier in {"vertical", "stacked"}

    if is_vertical:
        x_bar = size / 2
        dwg.add(dwg.line(start=(x_bar, 4 * s), end=(x_bar, size - 4 * s), stroke=color, stroke_width=2.5 * s))
        pos_y = 10 * s if modifier in {"active", "high", "primary"} else size / 2
        dwg.add(dwg.circle(center=(x_bar, pos_y), r=4.5 * s, fill=color))
    else:
        y_bar = size / 2
        dwg.add(dwg.line(start=(4 * s, y_bar), end=(size - 4 * s, y_bar), stroke=color, stroke_width=2.5 * s))
        pos_x = size - 10 * s if modifier in {"active", "high", "primary"} else 10 * s if modifier in {"low", "minimal"} else size / 2
        dwg.add(dwg.circle(center=(pos_x, y_bar), r=4.5 * s, fill=color))


def render_switch(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    render_toggle(dwg, size, modifier, color)


def render_knob(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 10 * s
    dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=2 * s))

    angle_deg = 45 if modifier in {"high", "active", "max"} else 225 if modifier in {"low", "min"} else 135
    rad = math.radians(angle_deg)
    px = cx + (r - 2 * s) * math.cos(rad)
    py = cy + (r - 2 * s) * math.sin(rad)
    dwg.add(dwg.line(start=(cx, cy), end=(px, py), stroke=color, stroke_width=2 * s))


def render_dial(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 11 * s
    dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=1.5 * s))
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        x1 = cx + (r - 1 * s) * math.cos(rad)
        y1 = cy + (r - 1 * s) * math.sin(rad)
        x2 = cx + (r - 3 * s) * math.cos(rad)
        y2 = cy + (r - 3 * s) * math.sin(rad)
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.circle(center=(cx, cy), r=2 * s, fill=color))
    dwg.add(dwg.line(start=(cx, cy), end=(cx + 6 * s, cy - 4 * s), stroke=color, stroke_width=1.8 * s))


def render_wheel(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 11 * s
    dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=2 * s))
    dwg.add(dwg.circle(center=(cx, cy), r=3.5 * s, fill=color))
    for deg in range(0, 360, 60):
        rad = math.radians(deg)
        x1 = cx + 3.5 * s * math.cos(rad)
        y1 = cy + 3.5 * s * math.sin(rad)
        x2 = cx + r * math.cos(rad)
        y2 = cy + r * math.sin(rad)
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=1.5 * s))


def render_select(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w = 26 * s
    h = 14 * s
    x, y = (size - w) / 2, (size - h) / 2
    rx = 2 * s
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=1.5 * s))
    dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + 14 * s, size / 2), stroke=color, stroke_width=1.5 * s))
    cx_caret = x + w - 5 * s
    cy_caret = size / 2
    dwg.add(dwg.polyline(points=[
        (cx_caret - 2.5 * s, cy_caret - 1.5 * s),
        (cx_caret, cy_caret + 1.5 * s),
        (cx_caret + 2.5 * s, cy_caret - 1.5 * s)
    ], fill="none", stroke=color, stroke_width=1.5 * s))


def render_textarea(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w = 26 * s
    h = 22 * s
    x, y = (size - w) / 2, (size - h) / 2
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 5 * s), end=(x + w - 4 * s, y + 5 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 9.5 * s), end=(x + w - 8 * s, y + 9.5 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 14 * s), end=(x + 12 * s, y + 14 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + w - 3 * s, y + h - 6 * s), end=(x + w - 6 * s, y + h - 3 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(x + w - 2 * s, y + h - 3.5 * s), end=(x + w - 3.5 * s, y + h - 2 * s), stroke=color, stroke_width=1 * s))


def render_drag_handle(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    dx = 3.5 * s
    dy = 4.5 * s
    r = 1.6 * s
    for col in (-dx, dx):
        for row in (-dy, 0, dy):
            dwg.add(dwg.circle(center=(cx + col, cy + row), r=r, fill=color))


def render_resize_handle(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    if modifier in {"horizontal"}:
        dwg.add(dwg.line(start=(cx - 8 * s, cy), end=(cx + 8 * s, cy), stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[(cx - 5 * s, cy - 3 * s), (cx - 8 * s, cy), (cx - 5 * s, cy + 3 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
        dwg.add(dwg.polyline(points=[(cx + 5 * s, cy - 3 * s), (cx + 8 * s, cy), (cx + 5 * s, cy + 3 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
    elif modifier in {"vertical"}:
        dwg.add(dwg.line(start=(cx, cy - 8 * s), end=(cx, cy + 8 * s), stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[(cx - 3 * s, cy - 5 * s), (cx, cy - 8 * s), (cx + 3 * s, cy - 5 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
        dwg.add(dwg.polyline(points=[(cx - 3 * s, cy + 5 * s), (cx, cy + 8 * s), (cx + 3 * s, cy + 5 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
    else:
        dwg.add(dwg.line(start=(cx - 7 * s, cy - 7 * s), end=(cx + 7 * s, cy + 7 * s), stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[(cx - 7 * s, cy - 2 * s), (cx - 7 * s, cy - 7 * s), (cx - 2 * s, cy - 7 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
        dwg.add(dwg.polyline(points=[(cx + 7 * s, cy + 2 * s), (cx + 7 * s, cy + 7 * s), (cx + 2 * s, cy + 7 * s)], fill="none", stroke=color, stroke_width=1.8 * s))


def render_splitter(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    if modifier in {"horizontal"}:
        dwg.add(dwg.rect(insert=(4 * s, 4 * s), size=(24 * s, 10 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
        dwg.add(dwg.rect(insert=(4 * s, 18 * s), size=(24 * s, 10 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
        dwg.add(dwg.line(start=(11 * s, 16 * s), end=(21 * s, 16 * s), stroke=color, stroke_width=2 * s))
    else:
        dwg.add(dwg.rect(insert=(4 * s, 4 * s), size=(10 * s, 24 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
        dwg.add(dwg.rect(insert=(18 * s, 4 * s), size=(10 * s, 24 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
        dwg.add(dwg.line(start=(16 * s, 11 * s), end=(16 * s, 21 * s), stroke=color, stroke_width=2 * s))


# -------------------------------------------------------------------------
# Archetype Renderers (Navigation)
# -------------------------------------------------------------------------

def render_menu(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    if modifier in {"vertical", "stacked"}:
        gap = 5 * s
        for r_off in (-gap, 0, gap):
            dwg.add(dwg.rect(insert=(cx - 9 * s, cy + r_off - 1 * s), size=(18 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))
    elif modifier in {"dots"}:
        gap = 5 * s
        for r_off in (-gap, 0, gap):
            dwg.add(dwg.circle(center=(cx, cy + r_off), r=2 * s, fill=color))
    else:
        gap = 4 * s
        for r_off in (-gap, 0, gap):
            dwg.add(dwg.rect(insert=(4 * s, cy + r_off - 1 * s), size=(24 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))


def render_dropdown(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w, h = 26 * s, 14 * s
    x, y = (size - w) / 2, (size - h) / 2
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + 14 * s, size / 2), stroke=color, stroke_width=1.5 * s))
    cx_c = x + w - 5 * s
    cy_c = size / 2
    if modifier in {"open", "expanded", "active"}:
        dwg.add(dwg.polyline(points=[
            (cx_c - 2.5 * s, cy_c + 1.5 * s),
            (cx_c, cy_c - 1.5 * s),
            (cx_c + 2.5 * s, cy_c + 1.5 * s),
        ], fill="none", stroke=color, stroke_width=1.5 * s))
        if modifier in {"open", "expanded"}:
            dwg.add(dwg.rect(insert=(x, y + h + 2 * s), size=(w, 10 * s), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1 * s))
            dwg.add(dwg.line(start=(x + 4 * s, y + h + 5 * s), end=(x + 18 * s, y + h + 5 * s), stroke=color, stroke_width=1 * s))
    else:
        dwg.add(dwg.polyline(points=[
            (cx_c - 2.5 * s, cy_c - 1.5 * s),
            (cx_c, cy_c + 1.5 * s),
            (cx_c + 2.5 * s, cy_c - 1.5 * s),
        ], fill="none", stroke=color, stroke_width=1.5 * s))


def render_tab(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    if modifier in {"vertical"}:
        col_w = 10 * s
        col_x = 4 * s
        for i, h in enumerate((6 * s, 6 * s, 6 * s, 6 * s)):
            ry = 4 * s + i * 7 * s
            is_active = i == 1
            if is_active:
                # Filled active tab with horizontal indicator cutout
                holes = [(col_x + 2 * s, ry + h / 2 - 0.6 * s, 6 * s, 1.2 * s)]
                _add_rect_with_rect_holes(dwg, col_x - 1 * s, ry, col_w + 2 * s, h, color, holes=holes, rx=2 * s)
            else:
                dwg.add(dwg.rect(insert=(col_x, ry), size=(col_w, h), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1 * s))
    else:
        tab_w = 6 * s
        gap = 1 * s
        for i in range(4):
            tx = 3 * s + i * (tab_w + gap)
            ty = 6 * s
            is_active = (i == 1 and not modifier.endswith("right")) or (i == 3 and "right" in modifier) or (modifier in {"active"} and i == 2)
            if is_active or modifier in {"active", "selected", "primary"}:
                # Filled active tab with indicator cutout
                holes = [(tx + 2 * s, ty + 8 * s - 0.6 * s, tab_w - 4 * s, 1.2 * s)]
                _add_rect_with_rect_holes(dwg, tx, ty, tab_w, 16 * s, color, holes=holes, rx=2 * s)
            else:
                dwg.add(dwg.rect(insert=(tx, ty), size=(tab_w, 16 * s), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1 * s))
        dwg.add(dwg.line(start=(3 * s, 23 * s), end=(size - 3 * s, 23 * s), stroke=color, stroke_width=1 * s))


def render_pagination(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    dwg.add(dwg.polyline(points=[
        (6 * s, cy), (10 * s, cy - 4 * s), (10 * s, cy + 4 * s), (6 * s, cy),
    ], fill="none", stroke=color, stroke_width=1.5 * s, stroke_linejoin="round"))
    dot_r = 2 * s
    for i in range(4):
        cx_dot = 13 * s + i * 4 * s
        is_active = (i == 1 and modifier in {"active", "current", "selected", "primary"}) or (modifier == "page-3" and i == 2) or (modifier == "page-4" and i == 3)
        if is_active or (modifier in {"filled"}):
            dwg.add(dwg.circle(center=(cx_dot, cy), r=dot_r, fill=color))
        else:
            dwg.add(dwg.circle(center=(cx_dot, cy), r=dot_r, fill="none", stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.polyline(points=[
        (size - 6 * s, cy), (size - 10 * s, cy - 4 * s), (size - 10 * s, cy + 4 * s), (size - 6 * s, cy),
    ], fill="none", stroke=color, stroke_width=1.5 * s, stroke_linejoin="round"))


def render_breadcrumb(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    node_w = 6 * s
    node_h = 4 * s
    dwg.add(dwg.rect(insert=(3 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.polyline(points=[(10 * s, cy - 2 * s), (12 * s, cy), (10 * s, cy + 2 * s)], fill="none", stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.rect(insert=(13 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.polyline(points=[(20 * s, cy - 2 * s), (22 * s, cy), (20 * s, cy + 2 * s)], fill="none", stroke=color, stroke_width=1.2 * s))
    if modifier in {"active", "current", "selected", "primary", "filled"}:
        dwg.add(dwg.rect(insert=(23 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill=color))
    else:
        dwg.add(dwg.rect(insert=(23 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))


def render_navbar(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    bar_x, bar_y, bar_w, bar_h = 3 * s, 4 * s, 26 * s, 6 * s
    if modifier in {"filled", "primary", "active", "selected"}:
        # Filled bar with hamburger + nav-item cutouts
        holes: list[tuple[float, float, float, float]] = [
            (5 * s, 6 * s, 3 * s, 1 * s),
            (5 * s, 8 * s, 3 * s, 1 * s),
            (5 * s, 10 * s, 3 * s, 1 * s),
            (12 * s, 8 * s - 1.5 * s, 3 * s, 3 * s),  # logo dot
            (16 * s, 6 * s, 3 * s, 1 * s),
            (16 * s, 9 * s, 3 * s, 1 * s),
            (21 * s, 6 * s, 3 * s, 1 * s),
            (21 * s, 9 * s, 3 * s, 1 * s),
            (26 * s, 6 * s, 3 * s, 1 * s),
            (26 * s, 9 * s, 3 * s, 1 * s),
        ]
        _add_rect_with_rect_holes(dwg, bar_x, bar_y, bar_w, bar_h, color, holes=holes, rx=1.5 * s)
    else:
        dwg.add(dwg.rect(insert=(bar_x, bar_y), size=(bar_w, bar_h), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        # Hamburger
        for y in (6 * s, 8 * s, 10 * s):
            dwg.add(dwg.rect(insert=(5 * s, y), size=(3 * s, 1 * s), fill=color))
        dwg.add(dwg.circle(center=(12 * s, 8 * s), r=1.5 * s, fill=color))
        for x in (16 * s, 21 * s, 26 * s):
            dwg.add(dwg.rect(insert=(x, 6 * s), size=(3 * s, 1 * s), fill=color))
            dwg.add(dwg.rect(insert=(x, 9 * s), size=(3 * s, 1 * s), fill=color))
    # Bottom content area (always outlined)
    dwg.add(dwg.rect(insert=(3 * s, 14 * s), size=(26 * s, 14 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 19 * s), end=(26 * s, 19 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 22 * s), end=(20 * s, 22 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 25 * s), end=(24 * s, 25 * s), stroke=color, stroke_width=1 * s))


def render_sidebar(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    bar_x, bar_y, bar_w, bar_h = 3 * s, 3 * s, 8 * s, 26 * s
    if modifier in {"filled", "primary", "active", "selected"}:
        # Filled sidebar with rectangular cutouts for items
        holes: list[tuple[float, float, float, float]] = []
        for i, y in enumerate((6 * s, 10 * s, 14 * s, 18 * s, 22 * s)):
            is_active = (i == 1) or (modifier == "item-3" and i == 2)
            item_w = 7 * s if is_active else 5 * s
            item_x = 4.5 * s if not is_active else 3.5 * s
            holes.append((item_x, y, item_w, 2 * s))
        _add_rect_with_rect_holes(dwg, bar_x, bar_y, bar_w, bar_h, color, holes=holes, rx=1.5 * s)
    else:
        dwg.add(dwg.rect(insert=(bar_x, bar_y), size=(bar_w, bar_h), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        for i, y in enumerate((6 * s, 10 * s, 14 * s, 18 * s, 22 * s)):
            is_active = (i == 1) or (modifier == "item-3" and i == 2)
            if is_active:
                dwg.add(dwg.rect(insert=(3.5 * s, y), size=(7 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))
            else:
                dwg.add(dwg.rect(insert=(4.5 * s, y), size=(5 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))
    dwg.add(dwg.rect(insert=(13 * s, 3 * s), size=(16 * s, 26 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(15 * s, 8 * s), end=(27 * s, 8 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(15 * s, 13 * s), end=(27 * s, 13 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(15 * s, 18 * s), end=(22 * s, 18 * s), stroke=color, stroke_width=1 * s))


def render_footer(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    dwg.add(dwg.line(start=(6 * s, 6 * s), end=(26 * s, 6 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 10 * s), end=(26 * s, 10 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 14 * s), end=(20 * s, 14 * s), stroke=color, stroke_width=1 * s))
    bar_x, bar_y, bar_w, bar_h = 3 * s, 22 * s, 26 * s, 6 * s
    if modifier in {"filled", "primary", "active", "selected"}:
        # Filled footer bar with item cutouts
        holes = [(6 * s, 24 * s, 2 * s, 2 * s), (11 * s, 24 * s, 2 * s, 2 * s),
                 (16 * s, 24 * s, 2 * s, 2 * s), (21 * s, 24 * s, 2 * s, 2 * s),
                 (26 * s, 24 * s, 2 * s, 2 * s)]
        _add_rect_with_rect_holes(dwg, bar_x, bar_y, bar_w, bar_h, color, holes=holes, rx=1.5 * s)
    else:
        dwg.add(dwg.rect(insert=(bar_x, bar_y), size=(bar_w, bar_h), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        for x in (6 * s, 11 * s, 16 * s, 21 * s, 26 * s):
            dwg.add(dwg.rect(insert=(x, 24 * s), size=(2 * s, 2 * s), fill=color))


def render_header(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    bar_x, bar_y, bar_w, bar_h = 3 * s, 4 * s, 26 * s, 7 * s
    if modifier in {"filled", "primary", "active", "selected"}:
        # Filled header bar with hamburger + title pill + icons as cutouts
        holes = [
            (5 * s, 6 * s, 3 * s, 1 * s),
            (5 * s, 8 * s, 3 * s, 1 * s),
            (5 * s, 10 * s, 3 * s, 1 * s),
            (11 * s, 6 * s, 8 * s, 3 * s),
            # Right-side icons as small squares (holes)
            (24 * s - 1.5 * s, 8 * s - 1.5 * s, 3 * s, 3 * s),
            (27 * s - 1.5 * s, 8 * s - 1.5 * s, 3 * s, 3 * s),
        ]
        _add_rect_with_rect_holes(dwg, bar_x, bar_y, bar_w, bar_h, color, holes=holes, rx=1.5 * s)
    else:
        dwg.add(dwg.rect(insert=(bar_x, bar_y), size=(bar_w, bar_h), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        for y in (6 * s, 8 * s, 10 * s):
            dwg.add(dwg.rect(insert=(5 * s, y), size=(3 * s, 1 * s), fill=color))
        dwg.add(dwg.rect(insert=(11 * s, 6 * s), size=(8 * s, 3 * s), rx=1 * s, ry=1 * s, fill=color))
        dwg.add(dwg.circle(center=(24 * s, 8 * s), r=1.5 * s, fill=color))
        dwg.add(dwg.circle(center=(27 * s, 8 * s), r=1.5 * s, fill=color))
    dwg.add(dwg.line(start=(6 * s, 17 * s), end=(26 * s, 17 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 22 * s), end=(26 * s, 22 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 26 * s), end=(18 * s, 26 * s), stroke=color, stroke_width=1 * s))


def render_stepper(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    step_r = 4 * s
    spacing = 7 * s
    for i in range(4):
        cx_step = 4 * s + i * spacing
        is_done = i < 1 and modifier not in {"active", "current"}
        is_active = i == 1 and modifier in {"active", "current", "selected", "primary"}
        if is_done or modifier in {"completed", "filled"}:
            # Filled step circle with check-mark cutout
            outer_pts = [
                (cx_step - step_r, cy),
                (cx_step, cy - step_r),
                (cx_step + step_r, cy),
                (cx_step, cy + step_r),
            ]
            check_d = _add_checkmark_hole_subpath(cx_step, cy, s * 0.55, 1.5 * s)
            subpaths = ["M " + " L ".join(f"{px},{py}" for px, py in outer_pts) + " Z", check_d]
            _add_evenodd(dwg, subpaths, color)
        elif is_active:
            dwg.add(dwg.circle(center=(cx_step, cy), r=step_r, fill="none", stroke=color, stroke_width=2 * s))
            dwg.add(dwg.circle(center=(cx_step, cy), r=2 * s, fill=color))
        else:
            dwg.add(dwg.circle(center=(cx_step, cy), r=step_r, fill="none", stroke=color, stroke_width=1.2 * s))
        if i < 3:
            x1 = cx_step + step_r
            x2 = cx_step + spacing - step_r
            if is_done:
                dwg.add(dwg.line(start=(x1, cy), end=(x2, cy), stroke=color, stroke_width=1.5 * s))
            else:
                dwg.add(dwg.line(start=(x1, cy), end=(x2, cy), stroke=color, stroke_width=1 * s, stroke_dasharray=f"{2*s},{2*s}"))


def render_wizard(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    panel_w = 26 * s
    panel_h = 18 * s
    panel_x = (size - panel_w) / 2
    panel_y = (size - panel_h) / 2
    dwg.add(dwg.rect(insert=(panel_x, panel_y), size=(panel_w, panel_h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    # Title bar
    title_h = 5 * s
    dwg.add(dwg.rect(insert=(panel_x, panel_y), size=(panel_w, title_h), rx=2 * s, ry=2 * s, fill=color))
    dwg.add(dwg.rect(insert=(panel_x, panel_y + 2 * s), size=(panel_w, 3 * s), fill=color))
    cx_circle = panel_x + 6 * s
    cy_circle = panel_y + 12 * s
    dwg.add(dwg.circle(center=(cx_circle, cy_circle), r=4 * s, fill=color))
    # Number indicator as a small rect inside the circle
    dwg.add(dwg.rect(insert=(cx_circle - 2 * s, cy_circle - 0.5 * s), size=(4 * s, 1 * s), rx=0.5 * s, ry=0.5 * s, fill="none", stroke=color, stroke_width=1 * s))
    # Step description lines
    dwg.add(dwg.line(start=(cx_circle + 6 * s, cy_circle - 2 * s), end=(panel_x + panel_w - 3 * s, cy_circle - 2 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(cx_circle + 6 * s, cy_circle), end=(panel_x + panel_w - 8 * s, cy_circle), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(cx_circle + 6 * s, cy_circle + 2 * s), end=(panel_x + panel_w - 12 * s, cy_circle + 2 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.rect(insert=(panel_x + 4 * s, panel_y + panel_h - 5 * s), size=(6 * s, 3 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1 * s))
    dwg.add(dwg.rect(insert=(panel_x + panel_w - 10 * s, panel_y + panel_h - 5 * s), size=(6 * s, 3 * s), rx=1 * s, ry=1 * s, fill=color))


def render_step(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    is_done = modifier in {"completed", "done", "finished"}
    is_active = modifier in {"active", "current", "selected", "primary"}
    if is_done:
        # Filled circle with check cutout
        outer_pts = [
            (cx - 9 * s, cy),
            (cx, cy - 9 * s),
            (cx + 9 * s, cy),
            (cx, cy + 9 * s),
        ]
        check_d = _add_checkmark_hole_subpath(cx, cy, s, 2 * s)
        subpaths = ["M " + " L ".join(f"{px},{py}" for px, py in outer_pts) + " Z", check_d]
        _add_evenodd(dwg, subpaths, color)
    elif is_active:
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill="none", stroke=color, stroke_width=2.5 * s))
        dwg.add(dwg.circle(center=(cx, cy), r=4 * s, fill=color))
    else:
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        dwg.add(dwg.rect(insert=(cx - 4 * s, cy - 1 * s), size=(8 * s, 2 * s), fill=color))


# -------------------------------------------------------------------------
# Archetype Renderers (Feedback)
# -------------------------------------------------------------------------

def render_alert(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w, h = 26 * s, 14 * s
    x, y = (size - w) / 2, (size - h) / 2
    rx = 2 * s
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=1.5 * s))
    # Left accent stripe (filled)
    dwg.add(dwg.rect(insert=(x, y), size=(3 * s, h), rx=rx, ry=rx, fill=color))
    cx_e = x + 7 * s
    cy_e = size / 2
    dwg.add(dwg.rect(insert=(cx_e - 1 * s, cy_e - 4 * s), size=(2 * s, 5 * s), rx=1 * s, ry=1 * s, fill=color))
    dwg.add(dwg.circle(center=(cx_e, cy_e + 3 * s), r=1.2 * s, fill=color))
    dwg.add(dwg.line(start=(x + 12 * s, y + 4 * s), end=(x + w - 3 * s, y + 4 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 12 * s, y + 7 * s), end=(x + w - 8 * s, y + 7 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 12 * s, y + 10 * s), end=(x + w - 5 * s, y + 10 * s), stroke=color, stroke_width=1.2 * s))


def render_badge(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    is_filled = modifier in {"filled", "primary", "active", "selected", "notification"}
    if is_filled:
        # Filled circle with hollow center
        _add_circle_with_circle_holes(dwg, cx, cy, 9 * s, color, holes=[(cx, cy, 4 * s)])
    else:
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill="none", stroke=color, stroke_width=2 * s))
        dwg.add(dwg.rect(insert=(cx - 4 * s, cy - 1 * s), size=(8 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))
    if modifier in {"notification", "active", "primary", "filled", "unread"}:
        nx = size - 6 * s
        ny = 6 * s
        dwg.add(dwg.circle(center=(nx, ny), r=3 * s, fill=color))


def render_toast(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w1, h1 = 24 * s, 10 * s
    x1, y1 = (size - w1) / 2, 6 * s
    dwg.add(dwg.rect(insert=(x1, y1), size=(w1, h1), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.circle(center=(x1 + 4 * s, y1 + h1 / 2), r=2 * s, fill=color))
    dwg.add(dwg.line(start=(x1 + 8 * s, y1 + 3 * s), end=(x1 + w1 - 3 * s, y1 + 3 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(x1 + 8 * s, y1 + h1 - 3 * s), end=(x1 + w1 - 8 * s, y1 + h1 - 3 * s), stroke=color, stroke_width=1 * s))
    if modifier in {"active", "primary", "filled", "selected"}:
        # Filled bottom toast with content cutouts
        x2, y2 = (size - w1) / 2, 16 * s
        holes = [
            (x2 + 2 * s, y2 + h1 / 2 - 2 * s, 4 * s, 4 * s),
            (x2 + 8 * s, y2 + 3 * s, w1 - 11 * s, 1 * s),
            (x2 + 8 * s, y2 + h1 - 3 * s, w1 - 16 * s, 1 * s),
        ]
        _add_rect_with_rect_holes(dwg, x2, y2, w1, h1, color, holes=holes, rx=1.5 * s)


def render_spinner(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 10 * s
    segments = 8
    for i in range(segments):
        ang = i * (360 / segments)
        rad = math.radians(ang - 90)
        x = cx + r * math.cos(rad)
        y = cy + r * math.sin(rad)
        rad1 = math.radians(ang - 80)
        rad2 = math.radians(ang - 100)
        x1 = cx + r * math.cos(rad1)
        y1 = cy + r * math.sin(rad1)
        x2 = cx + r * math.cos(rad2)
        y2 = cy + r * math.sin(rad2)
        if (i == 0 and modifier in {"active", "loading", "primary", "filled"}) or (modifier == "step-1" and i == 0):
            dwg.add(dwg.circle(center=(x, y), r=1.8 * s, fill=color))
            dwg.add(dwg.circle(center=(x1, y1), r=1.5 * s, fill=color))
            dwg.add(dwg.circle(center=(x2, y2), r=1.2 * s, fill=color))
        else:
            dwg.add(dwg.circle(center=(x, y), r=1.2 * s, fill=color))


def render_progress_bar(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    if modifier in {"vertical"}:
        x_bar = size / 2
        bar_w = 6 * s
        bar_h = 22 * s
        y_bar = 5 * s
        dwg.add(dwg.rect(insert=(x_bar - bar_w / 2, y_bar), size=(bar_w, bar_h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        fill_pct = 0.5
        if modifier in {"active", "primary", "filled"}:
            fill_pct = 0.6
        elif modifier in {"loading", "half"}:
            fill_pct = 0.5
        elif modifier == "complete":
            fill_pct = 1.0
        elif modifier == "quarter":
            fill_pct = 0.25
        elif modifier == "three-quarters":
            fill_pct = 0.75
        elif modifier == "minimal":
            fill_pct = 0.1
        dwg.add(dwg.rect(insert=(x_bar - bar_w / 2, y_bar + bar_h * (1 - fill_pct)), size=(bar_w, bar_h * fill_pct), rx=2 * s, ry=2 * s, fill=color))
    else:
        x_bar = 4 * s
        bar_w = 24 * s
        bar_h = 6 * s
        y_bar = (size - bar_h) / 2
        dwg.add(dwg.rect(insert=(x_bar, y_bar), size=(bar_w, bar_h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        fill_pct = 0.5
        if modifier in {"active", "primary", "filled", "loading"}:
            fill_pct = 0.6
        elif modifier == "complete":
            fill_pct = 1.0
        elif modifier == "quarter":
            fill_pct = 0.25
        elif modifier == "three-quarters":
            fill_pct = 0.75
        elif modifier == "minimal":
            fill_pct = 0.1
        dwg.add(dwg.rect(insert=(x_bar, y_bar), size=(bar_w * fill_pct, bar_h), rx=2 * s, ry=2 * s, fill=color))


def render_skeleton(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    bar_h = 4 * s
    gap = 4 * s
    bars = [(4 * s, 24 * s), (4 * s, 20 * s), (4 * s, 16 * s)]
    y = 4 * s
    for (bx, bw) in bars:
        dwg.add(dwg.rect(insert=(bx, y), size=(bw, bar_h), rx=2 * s, ry=2 * s, fill=color))
        y += bar_h + gap
    if modifier in {"avatar", "profile", "active"}:
        dwg.add(dwg.circle(center=(8 * s, 4 * s), r=4 * s, fill=color))


def render_placeholder(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w, h = 26 * s, 18 * s
    x, y = (size - w) / 2, (size - h) / 2
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    spacing = 5 * s
    diag_w = w + h
    diag_count = int(diag_w / spacing)
    for i in range(-2, diag_count + 2):
        x_start = x + i * spacing
        y_start = y + h
        x_end = x_start + h
        y_end = y
        if x_start < x:
            offset = x - x_start
            x_start = x
            y_start = y_start - offset
        if y_end > y:
            offset = y_end - y
            x_end = x_end - offset
            y_end = y
        dwg.add(dwg.line(start=(x_start, y_start), end=(x_end, y_end), stroke=color, stroke_width=0.8 * s))


def render_loader(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    if modifier in {"vertical", "bars"}:
        for i, x in enumerate((cx - 6 * s, cx, cx + 6 * s)):
            offset = -2 * s if i == 0 else 0 if i == 1 else 2 * s
            dwg.add(dwg.circle(center=(x, cy + offset), r=2 * s, fill=color))
    else:
        for i, y in enumerate((cy - 6 * s, cy, cy + 6 * s)):
            offset = -2 * s if i == 0 else 0 if i == 1 else 2 * s
            dwg.add(dwg.circle(center=(cx + offset, y), r=2 * s, fill=color))


def render_indicator(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    is_active = modifier in {"active", "online", "success", "selected", "primary", "filled"}
    if is_active:
        # Filled circle with hollow inner ring (transparent ring)
        _add_circle_with_circle_holes(dwg, cx, cy, 9 * s, color, holes=[(cx, cy, 5 * s)])
    else:
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill="none", stroke=color, stroke_width=2 * s))


def render_counter(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w, h = 20 * s, 12 * s
    x, y = (size - w) / 2, (size - h) / 2
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=h / 2, ry=h / 2, fill="none", stroke=color, stroke_width=1.5 * s))
    dwg.add(dwg.line(start=(x + 4 * s, size / 2 - 1 * s), end=(x + w - 4 * s, size / 2 - 1 * s), stroke=color, stroke_width=1.5 * s))
    dwg.add(dwg.line(start=(x + 4 * s, size / 2 + 1 * s), end=(x + w - 7 * s, size / 2 + 1 * s), stroke=color, stroke_width=1.5 * s))
    if modifier in {"notification", "active", "primary", "filled", "unread"}:
        nx = size - 6 * s
        ny = 6 * s
        dwg.add(dwg.circle(center=(nx, ny), r=3 * s, fill=color))


def render_notification(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    dwg.add(dwg.circle(center=(cx, 7 * s), r=1.5 * s, fill=color))
    bell_top = 8 * s
    bell_bottom_y = 22 * s
    bell_left_top = cx - 6 * s
    bell_right_top = cx + 6 * s
    bell_left_bot = cx - 9 * s
    bell_right_bot = cx + 9 * s
    bell_path = f"M {bell_left_top},{bell_top} L {bell_right_top},{bell_top} L {bell_right_bot},{bell_bottom_y} L {bell_left_bot},{bell_bottom_y} Z"
    dwg.add(dwg.path(d=bell_path, fill="none", stroke=color, stroke_width=2 * s, stroke_linejoin="round"))
    dwg.add(dwg.circle(center=(cx, bell_bottom_y + 2 * s), r=2 * s, fill=color))
    if modifier in {"active", "primary", "filled", "selected", "unread"}:
        nx = size - 6 * s
        ny = 6 * s
        dwg.add(dwg.circle(center=(nx, ny), r=3 * s, fill=color))


def render_callout(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    w, h = 24 * s, 16 * s
    x, y = 4 * s, 5 * s
    rx = 3 * s
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=1.8 * s))
    tail_path = f"M {x + 5 * s},{y + h} L {x + 5 * s},{y + h + 4 * s} L {x + 9 * s},{y + h} Z"
    dwg.add(dwg.path(d=tail_path, fill="none", stroke=color, stroke_width=1 * s, stroke_linejoin="round"))
    dwg.add(dwg.line(start=(x + 4 * s, y + 4 * s), end=(x + w - 4 * s, y + 4 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 8 * s), end=(x + w - 8 * s, y + 8 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 12 * s), end=(x + w - 12 * s, y + 12 * s), stroke=color, stroke_width=1.2 * s))


def render_error(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    p1 = (cx, cy - 10 * s)
    p2 = (cx - 11 * s, cy + 10 * s)
    p3 = (cx + 11 * s, cy + 10 * s)
    if modifier in {"filled", "primary", "active", "selected"}:
        bar_d, dot_d = _add_exclamation_hole_subpath(cx, cy, s, 2.5 * s, 1.5 * s)
        _add_polygon_with_polygon_holes(dwg, [p1, p2, p3], color, holes=[[(cx - 1.25 * s, cy - 4 * s), (cx + 1.25 * s, cy - 4 * s), (cx + 1.25 * s, cy + 3 * s), (cx - 1.25 * s, cy + 3 * s)], [(cx, cy + 6 * s - 1.5 * s), (cx + 1.5 * s, cy + 6 * s), (cx, cy + 6 * s + 1.5 * s), (cx - 1.5 * s, cy + 6 * s)]])
    else:
        dwg.add(dwg.polygon(points=[p1, p2, p3], fill="none", stroke=color, stroke_width=2 * s, stroke_linejoin="round"))
        dwg.add(dwg.line(start=(cx, cy - 4 * s), end=(cx, cy + 3 * s), stroke=color, stroke_width=2.5 * s, stroke_linecap="round"))
        dwg.add(dwg.circle(center=(cx, cy + 6 * s), r=1.5 * s, fill=color))


def render_warning(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    p1 = (cx, cy - 10 * s)
    p2 = (cx - 11 * s, cy + 10 * s)
    p3 = (cx + 11 * s, cy + 10 * s)
    if modifier in {"filled", "primary", "active", "selected"}:
        _add_polygon_with_polygon_holes(dwg, [p1, p2, p3], color, holes=[[(cx - 1.25 * s, cy - 4 * s), (cx + 1.25 * s, cy - 4 * s), (cx + 1.25 * s, cy + 3 * s), (cx - 1.25 * s, cy + 3 * s)], [(cx, cy + 6 * s - 1.5 * s), (cx + 1.5 * s, cy + 6 * s), (cx, cy + 6 * s + 1.5 * s), (cx - 1.5 * s, cy + 6 * s)]])
    else:
        dwg.add(dwg.polygon(points=[p1, p2, p3], fill="none", stroke=color, stroke_width=2 * s, stroke_linejoin="round"))
        dwg.add(dwg.line(start=(cx, cy - 4 * s), end=(cx, cy + 3 * s), stroke=color, stroke_width=2.5 * s, stroke_linecap="round"))
        dwg.add(dwg.circle(center=(cx, cy + 6 * s), r=1.5 * s, fill=color))


def render_info(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 10 * s
    if modifier in {"filled", "primary", "active", "selected"}:
        dot_d, bar_d = _add_i_mark_hole_subpaths(cx, cy, s, 1.5 * s, 3 * s, 7 * s)
        _add_circle_with_circle_holes(dwg, cx, cy, r, color, holes=[(cx, cy, 4 * s)])
        # Now overlay the i mark as cutout
        sub_d = " ".join([_circle_d(cx, cy - 4 * s, 1.5 * s), _rect_d(cx - 1.5 * s, cy - 1 * s, 3 * s, 7 * s)])
        d = " ".join([_circle_d(cx, cy, r), sub_d])
        p = dwg.path(d=d, fill=color)
        p["fill-rule"] = "evenodd"
        dwg.add(p)
    else:
        dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=2 * s))
        dwg.add(dwg.circle(center=(cx, cy - 4 * s), r=1.5 * s, fill=color))
        dwg.add(dwg.rect(insert=(cx - 1.5 * s, cy - 1 * s), size=(3 * s, 7 * s), rx=1 * s, ry=1 * s, fill=color))


def render_success(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 10 * s
    if modifier in {"filled", "primary", "active", "selected"}:
        # Filled circle with check-mark cutout
        check_d = _add_checkmark_hole_subpath(cx, cy, s, 2.5 * s)
        subpaths = [_circle_d(cx, cy, r), check_d]
        _add_evenodd(dwg, subpaths, color)
    else:
        dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[
            (cx - 5 * s, cy),
            (cx - 1 * s, cy + 4 * s),
            (cx + 5 * s, cy - 4 * s),
        ], fill="none", stroke=color, stroke_width=2.5 * s, stroke_linejoin="round", stroke_linecap="round"))


# Map archetype functions
ARCHETYPES: dict[str, Callable[[svgwrite.Drawing, int, str, str], None]] = {
    "button": render_button,
    "input": render_input,
    "input-1": render_input,
    "checkbox": render_checkbox,
    "checkbox-1": render_checkbox,
    "radio": render_radio,
    "radio-1": render_radio,
    "toggle": render_toggle,
    "toggle-1": render_toggle,
    "slider": render_slider,
    "switch": render_switch,
    "knob": render_knob,
    "dial": render_dial,
    "wheel": render_wheel,
    "select": render_select,
    "textarea": render_textarea,
    "drag-handle": render_drag_handle,
    "resize-handle": render_resize_handle,
    "splitter": render_splitter,
    "menu": render_menu,
    "dropdown": render_dropdown,
    "tab": render_tab,
    "pagination": render_pagination,
    "breadcrumb": render_breadcrumb,
    "breadcrumb-1": render_breadcrumb,
    "navbar": render_navbar,
    "sidebar": render_sidebar,
    "footer": render_footer,
    "header": render_header,
    "stepper": render_stepper,
    "wizard": render_wizard,
    "step": render_step,
    "alert": render_alert,
    "badge": render_badge,
    "toast": render_toast,
    "spinner": render_spinner,
    "progress-bar": render_progress_bar,
    "skeleton": render_skeleton,
    "placeholder": render_placeholder,
    "loader": render_loader,
    "indicator": render_indicator,
    "counter": render_counter,
    "notification": render_notification,
    "callout": render_callout,
    "error": render_error,
    "warning": render_warning,
    "info": render_info,
    "success": render_success,
}


def render_semantic_icon(dwg: svgwrite.Drawing, concept: str, size: int, color: str) -> bool:
    """Attempt to render a concept using semantic archetypes.

    Returns True if an archetype was matched and rendered, False otherwise.
    """
    base, modifier = _parse_concept(concept)
    handler = ARCHETYPES.get(base)
    if handler:
        handler(dwg, size, modifier, color)
        return True
    return False
