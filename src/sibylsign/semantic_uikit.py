"""UI-Kit Semantic Icon Design & Rendering Engine.

This module provides handcrafted archetypes and modifier rules for UI kit
concepts so that every generated icon is visually recognizable, properly
aligned, padded within the canvas (no clipping), and distinct.
"""

from __future__ import annotations

import math
from typing import Callable, Optional
import svgwrite

# Canvas dimensions & grid rules
# For size=32: padding=3px, content box [3, 3] to [29, 29] (26x26)
# For size=64: scaled 2x


def _parse_concept(concept: str) -> tuple[str, str]:
    """Parse a concept name like 'button-primary' into (base, modifier)."""
    parts = concept.strip().lower().split("-")
    # Common multi-word bases or suffixes
    # Known bases that might contain a dash:
    multi_word_bases = {
        "icon-button", "progress-bar", "header-cell", "tree-view",
        "breadcrumb-1", "checkbox-1", "radio-1", "toggle-1", "input-1",
        "file-upload", "file-download", "drag-handle", "resize-handle",
        "circle-1", "square-1", "triangle-1", "diamond-1", "stopwatch-1", "timer-1"
    }
    for mwb in multi_word_bases:
        if concept.startswith(mwb + "-"):
            base = mwb
            mod = concept[len(mwb) + 1:]
            return base, mod

    if len(parts) >= 2:
        return parts[0], "-".join(parts[1:])
    return parts[0], "default"


# -------------------------------------------------------------------------
# Archetype Renderers (Controls)
# -------------------------------------------------------------------------

def render_button(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    filled = modifier in {"filled", "primary", "secondary", "tertiary", "active", "pressed", "selected"}
    is_outline = modifier in {"outline", "ghost", "empty", "borderless", "minimal"} or not filled
    rx = 2 * s if modifier in {"square", "dense"} else 6 * s if modifier in {"rounded", "pill"} else 4 * s
    w = 26 * s
    h = 16 * s
    x = (size - w) / 2
    y = (size - h) / 2

    # Container
    if filled:
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill=color))
        # Inner text / icon indicator
        if modifier not in {"empty"}:
            inner_color = "#ffffff"  # Contrasting inner mark or cutout
            # For pure mono-color black, we draw inner details or cutouts
            if modifier in {"with-icon", "secondary"}:
                dwg.add(dwg.circle(center=(x + 5 * s, y + h / 2), r=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
                dwg.add(dwg.line(start=(x + 9 * s, y + h / 2), end=(x + 20 * s, y + h / 2), stroke=color, stroke_width=2 * s))
            elif modifier in {"loading"}:
                dwg.add(dwg.circle(center=(size / 2, size / 2), r=3 * s, fill="none", stroke=color, stroke_width=1.5 * s, stroke_dasharray=f"{3*s},{2*s}"))
    else:
        # Outline / ghost / minimal
        sw = 2.5 * s if modifier in {"thick", "prominent"} else 1 * s if modifier in {"thin", "minimal"} else 1.8 * s
        if modifier != "borderless":
            dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=sw))
        # Center line representing label
        label_w = 12 * s if modifier in {"small", "compact"} else 16 * s
        dwg.add(dwg.line(start=((size - label_w) / 2, size / 2), end=((size + label_w) / 2, size / 2), stroke=color, stroke_width=2 * s))
        if modifier == "with-icon":
            dwg.add(dwg.circle(center=(x + 4 * s, size / 2), r=1.5 * s, fill=color))

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

    # Text cursor or placeholder line
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
        # Default placeholder hint dots/dashes
        dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + 12 * s, size / 2), stroke=color, stroke_width=1.5 * s, stroke_dasharray=f"{2*s},{2*s}"))


def render_checkbox(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    box_size = 18 * s
    x = (size - box_size) / 2
    y = (size - box_size) / 2
    rx = 3 * s if modifier in {"rounded", "default"} else 0

    is_checked = modifier in {"checked", "selected", "active", "filled", "primary", "success"}
    if is_checked:
        dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), rx=rx, ry=rx, fill=color))
        # Cutout / checkmark drawn in inverted shape or check icon
        # In black monochrome, we can render checkmark with stroke
        p1 = (x + 4 * s, y + 9 * s)
        p2 = (x + 7.5 * s, y + 13 * s)
        p3 = (x + 14 * s, y + 5 * s)
        # Invert or draw distinctive mark
        dwg.add(dwg.polygon(points=[
            (p1[0], p1[1]), (p2[0], p2[1]), (p3[0], p3[1]),
            (p3[0], p3[1] + 2.5 * s), (p2[0], p2[1] + 2.5 * s), (p1[0], p1[1] + 2.5 * s)
        ], fill="#ffffff" if is_checked else color))
    else:
        dwg.add(dwg.rect(insert=(x, y), size=(box_size, box_size), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=2 * s))
        if modifier == "intermediate":
            dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + box_size - 4 * s, size / 2), stroke=color, stroke_width=2 * s))


def render_radio(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    r = 10 * s
    cx, cy = size / 2, size / 2
    is_selected = modifier in {"selected", "active", "checked", "filled", "primary", "on"}

    dwg.add(dwg.circle(center=(cx, cy), r=r, fill="none", stroke=color, stroke_width=2 * s))
    if is_selected:
        dwg.add(dwg.circle(center=(cx, cy), r=5 * s, fill=color))
    elif modifier in {"hover", "focused"}:
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
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=r, ry=r, fill=color))
        # Knob on right (drawn with contrast or gap)
        dwg.add(dwg.circle(center=(x + w - r, cy := y + r), r=r - 2 * s, fill="#ffffff"))
    else:
        dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=r, ry=r, fill="none", stroke=color, stroke_width=2 * s))
        # Knob on left
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

    # Pointer angle
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
    # Outer tick marks
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        x1 = cx + (r - 1 * s) * math.cos(rad)
        y1 = cy + (r - 1 * s) * math.sin(rad)
        x2 = cx + (r - 3 * s) * math.cos(rad)
        y2 = cy + (r - 3 * s) * math.sin(rad)
        dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=1.2 * s))
    # Center indicator
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
    x = (size - w) / 2
    y = (size - h) / 2
    rx = 2 * s
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=rx, ry=rx, fill="none", stroke=color, stroke_width=1.5 * s))
    # Selected text line
    dwg.add(line := dwg.line(start=(x + 4 * s, size / 2), end=(x + 14 * s, size / 2), stroke=color, stroke_width=1.5 * s))
    # Down caret chevron
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
    x = (size - w) / 2
    y = (size - h) / 2
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    # Text lines inside
    dwg.add(dwg.line(start=(x + 4 * s, y + 5 * s), end=(x + w - 4 * s, y + 5 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 9.5 * s), end=(x + w - 8 * s, y + 9.5 * s), stroke=color, stroke_width=1.2 * s))
    dwg.add(dwg.line(start=(x + 4 * s, y + 14 * s), end=(x + 12 * s, y + 14 * s), stroke=color, stroke_width=1.2 * s))
    # Resize grip in bottom-right corner
    dwg.add(dwg.line(start=(x + w - 3 * s, y + h - 6 * s), end=(x + w - 6 * s, y + h - 3 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(x + w - 2 * s, y + h - 3.5 * s), end=(x + w - 3.5 * s, y + h - 2 * s), stroke=color, stroke_width=1 * s))


def render_drag_handle(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    # 6-dot grip (2 cols x 3 rows)
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
    # Diagonal two-headed arrow or corner lines
    if modifier in {"horizontal"}:
        dwg.add(dwg.line(start=(cx - 8 * s, cy), end=(cx + 8 * s, cy), stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[(cx - 5 * s, cy - 3 * s), (cx - 8 * s, cy), (cx - 5 * s, cy + 3 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
        dwg.add(dwg.polyline(points=[(cx + 5 * s, cy - 3 * s), (cx + 8 * s, cy), (cx + 5 * s, cy + 3 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
    elif modifier in {"vertical"}:
        dwg.add(dwg.line(start=(cx, cy - 8 * s), end=(cx, cy + 8 * s), stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[(cx - 3 * s, cy - 5 * s), (cx, cy - 8 * s), (cx + 3 * s, cy - 5 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
        dwg.add(dwg.polyline(points=[(cx - 3 * s, cy + 5 * s), (cx, cy + 8 * s), (cx + 3 * s, cy + 5 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
    else:
        # Diagonal arrows
        dwg.add(dwg.line(start=(cx - 7 * s, cy - 7 * s), end=(cx + 7 * s, cy + 7 * s), stroke=color, stroke_width=2 * s))
        dwg.add(dwg.polyline(points=[(cx - 7 * s, cy - 2 * s), (cx - 7 * s, cy - 7 * s), (cx - 2 * s, cy - 7 * s)], fill="none", stroke=color, stroke_width=1.8 * s))
        dwg.add(dwg.polyline(points=[(cx + 7 * s, cy + 2 * s), (cx + 7 * s, cy + 7 * s), (cx + 2 * s, cy + 7 * s)], fill="none", stroke=color, stroke_width=1.8 * s))


def render_splitter(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    if modifier in {"horizontal"}:
        # Two panels split horizontally
        dwg.add(dwg.rect(insert=(4 * s, 4 * s), size=(24 * s, 10 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
        dwg.add(dwg.rect(insert=(4 * s, 18 * s), size=(24 * s, 10 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
        dwg.add(dwg.line(start=(11 * s, 16 * s), end=(21 * s, 16 * s), stroke=color, stroke_width=2 * s))
    else:
        # Vertical divider between two panels
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
        # Three vertical bars
        gap = 5 * s
        for r_off in (-gap, 0, gap):
            dwg.add(dwg.rect(insert=(cx - 9 * s, cy + r_off - 1 * s), size=(18 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))
    elif modifier in {"dots"}:
        gap = 5 * s
        for r_off in (-gap, 0, gap):
            dwg.add(dwg.circle(center=(cx, cy + r_off), r=2 * s, fill=color))
    else:
        # Three horizontal lines (hamburger)
        gap = 4 * s
        for r_off in (-gap, 0, gap):
            dwg.add(dwg.rect(insert=(4 * s, cy + r_off - 1 * s), size=(24 * s, 2 * s), rx=1 * s, ry=1 * s, fill=color))


def render_dropdown(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    # Container
    w, h = 26 * s, 14 * s
    x, y = (size - w) / 2, (size - h) / 2
    dwg.add(dwg.rect(insert=(x, y), size=(w, h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    # Selected text line
    dwg.add(dwg.line(start=(x + 4 * s, size / 2), end=(x + 14 * s, size / 2), stroke=color, stroke_width=1.5 * s))
    # Caret indicator
    cx_c = x + w - 5 * s
    cy_c = size / 2
    if modifier in {"open", "expanded", "active"}:
        # Up caret
        dwg.add(dwg.polyline(points=[
            (cx_c - 2.5 * s, cy_c + 1.5 * s),
            (cx_c, cy_c - 1.5 * s),
            (cx_c + 2.5 * s, cy_c + 1.5 * s),
        ], fill="none", stroke=color, stroke_width=1.5 * s))
        # Open menu panel below
        if modifier in {"open", "expanded"}:
            dwg.add(dwg.rect(insert=(x, y + h + 2 * s), size=(w, 10 * s), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1 * s))
            dwg.add(dwg.line(start=(x + 4 * s, y + h + 5 * s), end=(x + 18 * s, y + h + 5 * s), stroke=color, stroke_width=1 * s))
    else:
        # Down caret
        dwg.add(dwg.polyline(points=[
            (cx_c - 2.5 * s, cy_c - 1.5 * s),
            (cx_c, cy_c + 1.5 * s),
            (cx_c + 2.5 * s, cy_c - 1.5 * s),
        ], fill="none", stroke=color, stroke_width=1.5 * s))


def render_tab(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    if modifier in {"vertical"}:
        # Vertical tab column
        col_w = 10 * s
        col_x = 4 * s
        for i, h in enumerate((6 * s, 6 * s, 6 * s, 6 * s)):
            ry = 4 * s + i * 7 * s
            is_active = i == 1
            if is_active:
                dwg.add(dwg.rect(insert=(col_x - 1 * s, ry), size=(col_w + 2 * s, h), rx=2 * s, ry=2 * s, fill=color))
                # Inverted indicator inside active tab
                dwg.add(dwg.line(start=(col_x + 2 * s, ry + h / 2), end=(col_x + 8 * s, ry + h / 2), stroke="#ffffff", stroke_width=1.2 * s))
            else:
                dwg.add(dwg.rect(insert=(col_x, ry), size=(col_w, h), rx=1.5 * s, ry=1.5 * s, fill="none", stroke=color, stroke_width=1 * s))
    else:
        # Horizontal tab strip
        tab_w = 6 * s
        gap = 1 * s
        for i in range(4):
            tx = 3 * s + i * (tab_w + gap)
            ty = 6 * s
            is_active = (i == 1 and not modifier.endswith("right")) or (i == 3 and "right" in modifier) or (modifier in {"active"} and i == 2)
            if is_active or modifier in {"active", "selected", "primary"} and i == 0:
                dwg.add(dwg.rect(insert=(tx, ty), size=(tab_w, 16 * s), rx=2 * s, ry=2 * s, fill=color))
                # Inner indicator
                dwg.add(dwg.line(start=(tx + 2 * s, ty + 8 * s), end=(tx + tab_w - 2 * s, ty + 8 * s), stroke="#ffffff", stroke_width=1.2 * s))
            else:
                dwg.add(dwg.rect(insert=(tx, ty), size=(tab_w, 16 * s), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1 * s))
        # Underline strip
        dwg.add(dwg.line(start=(3 * s, 23 * s), end=(size - 3 * s, 23 * s), stroke=color, stroke_width=1 * s))


def render_pagination(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    # Left arrow
    dwg.add(dwg.polyline(points=[
        (6 * s, cy), (10 * s, cy - 4 * s), (10 * s, cy + 4 * s), (6 * s, cy),
    ], fill="none", stroke=color, stroke_width=1.5 * s, stroke_linejoin="round"))
    # Page dots
    dot_r = 2 * s
    for i in range(4):
        cx_dot = 13 * s + i * 4 * s
        is_active = (i == 1 and modifier in {"active", "current", "selected", "primary"}) or (modifier == "page-3" and i == 2) or (modifier == "page-4" and i == 3)
        if is_active or (modifier in {"filled"}):
            dwg.add(dwg.circle(center=(cx_dot, cy), r=dot_r, fill=color))
        else:
            dwg.add(dwg.circle(center=(cx_dot, cy), r=dot_r, fill="none", stroke=color, stroke_width=1.2 * s))
    # Right arrow
    dwg.add(dwg.polyline(points=[
        (size - 6 * s, cy), (size - 10 * s, cy - 4 * s), (size - 10 * s, cy + 4 * s), (size - 6 * s, cy),
    ], fill="none", stroke=color, stroke_width=1.5 * s, stroke_linejoin="round"))


def render_breadcrumb(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    # Three nodes separated by chevrons
    node_w = 6 * s
    node_h = 4 * s
    # Node 1
    dwg.add(dwg.rect(insert=(3 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
    # Chevron
    dwg.add(dwg.polyline(points=[(10 * s, cy - 2 * s), (12 * s, cy), (10 * s, cy + 2 * s)], fill="none", stroke=color, stroke_width=1.2 * s))
    # Node 2
    dwg.add(dwg.rect(insert=(13 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))
    # Chevron
    dwg.add(dwg.polyline(points=[(20 * s, cy - 2 * s), (22 * s, cy), (20 * s, cy + 2 * s)], fill="none", stroke=color, stroke_width=1.2 * s))
    # Node 3 (current/active) - filled
    if modifier in {"active", "current", "selected", "primary", "filled"}:
        dwg.add(dwg.rect(insert=(23 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill=color))
    else:
        dwg.add(dwg.rect(insert=(23 * s, cy - node_h / 2), size=(node_w, node_h), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1.2 * s))


def render_navbar(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    # Top header bar
    dwg.add(dwg.rect(insert=(3 * s, 4 * s), size=(26 * s, 6 * s), rx=1.5 * s, ry=1.5 * s, fill=color))
    # Hamburger menu
    dwg.add(dwg.rect(insert=(5 * s, 6 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    dwg.add(dwg.rect(insert=(5 * s, 8 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    dwg.add(dwg.rect(insert=(5 * s, 10 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    # Logo dot
    dwg.add(dwg.circle(center=(12 * s, 8 * s), r=1.5 * s, fill="#ffffff"))
    # Nav items
    for i, x in enumerate((16 * s, 21 * s, 26 * s)):
        dwg.add(dwg.rect(insert=(x, 6 * s), size=(3 * s, 1 * s), fill="#ffffff"))
        dwg.add(dwg.rect(insert=(x, 9 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    # Bottom content area
    dwg.add(dwg.rect(insert=(3 * s, 14 * s), size=(26 * s, 14 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 19 * s), end=(26 * s, 19 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 22 * s), end=(20 * s, 22 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 25 * s), end=(24 * s, 25 * s), stroke=color, stroke_width=1 * s))


def render_sidebar(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    # Left sidebar
    dwg.add(dwg.rect(insert=(3 * s, 3 * s), size=(8 * s, 26 * s), rx=1.5 * s, ry=1.5 * s, fill=color))
    # Sidebar items
    for i, y in enumerate((6 * s, 10 * s, 14 * s, 18 * s, 22 * s)):
        is_active = (i == 1 and modifier in {"active", "selected", "primary"}) or (modifier == "item-3" and i == 2)
        if is_active:
            # Active item: inverted band
            dwg.add(dwg.rect(insert=(3.5 * s, y), size=(7 * s, 2 * s), rx=1 * s, ry=1 * s, fill="#ffffff"))
        else:
            dwg.add(dwg.rect(insert=(4.5 * s, y), size=(5 * s, 2 * s), rx=1 * s, ry=1 * s, fill="#ffffff"))
    # Main content area
    dwg.add(dwg.rect(insert=(13 * s, 3 * s), size=(16 * s, 26 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(15 * s, 8 * s), end=(27 * s, 8 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(15 * s, 13 * s), end=(27 * s, 13 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(15 * s, 18 * s), end=(22 * s, 18 * s), stroke=color, stroke_width=1 * s))


def render_footer(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    # Main content area
    dwg.add(dwg.line(start=(6 * s, 6 * s), end=(26 * s, 6 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 10 * s), end=(26 * s, 10 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 14 * s), end=(20 * s, 14 * s), stroke=color, stroke_width=1 * s))
    # Footer bar
    dwg.add(dwg.rect(insert=(3 * s, 22 * s), size=(26 * s, 6 * s), rx=1.5 * s, ry=1.5 * s, fill=color))
    # Footer items
    for i, x in enumerate((6 * s, 11 * s, 16 * s, 21 * s, 26 * s)):
        dwg.add(dwg.rect(insert=(x, 24 * s), size=(2 * s, 2 * s), fill="#ffffff"))


def render_header(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    # Header bar
    dwg.add(dwg.rect(insert=(3 * s, 4 * s), size=(26 * s, 7 * s), rx=1.5 * s, ry=1.5 * s, fill=color))
    # Hamburger
    dwg.add(dwg.rect(insert=(5 * s, 6 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    dwg.add(dwg.rect(insert=(5 * s, 8 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    dwg.add(dwg.rect(insert=(5 * s, 10 * s), size=(3 * s, 1 * s), fill="#ffffff"))
    # Title pill (white)
    dwg.add(dwg.rect(insert=(11 * s, 6 * s), size=(8 * s, 3 * s), rx=1 * s, ry=1 * s, fill="#ffffff"))
    # Right icons
    dwg.add(dwg.circle(center=(24 * s, 8 * s), r=1.5 * s, fill="#ffffff"))
    dwg.add(dwg.circle(center=(27 * s, 8 * s), r=1.5 * s, fill="#ffffff"))
    # Main content
    dwg.add(dwg.line(start=(6 * s, 17 * s), end=(26 * s, 17 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 22 * s), end=(26 * s, 22 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(6 * s, 26 * s), end=(18 * s, 26 * s), stroke=color, stroke_width=1 * s))


def render_stepper(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    # Four steps with connecting lines
    step_r = 4 * s
    spacing = 7 * s
    for i in range(4):
        cx_step = 4 * s + i * spacing
        is_done = i < 1 and modifier not in {"active", "current"}
        is_active = i == 1 and modifier in {"active", "current", "selected", "primary"}
        if is_done or modifier in {"completed", "filled"}:
            # Filled circle with check
            dwg.add(dwg.circle(center=(cx_step, cy), r=step_r, fill=color))
            # Check mark inside
            dwg.add(dwg.polyline(points=[
                (cx_step - 2 * s, cy),
                (cx_step - 0.5 * s, cy + 1.5 * s),
                (cx_step + 2 * s, cy - 1.5 * s),
            ], fill="none", stroke="#ffffff", stroke_width=1.5 * s, stroke_linejoin="round", stroke_linecap="round"))
        elif is_active:
            # Active ring
            dwg.add(dwg.circle(center=(cx_step, cy), r=step_r, fill="none", stroke=color, stroke_width=2 * s))
            dwg.add(dwg.circle(center=(cx_step, cy), r=2 * s, fill=color))
        else:
            # Empty ring
            dwg.add(dwg.circle(center=(cx_step, cy), r=step_r, fill="none", stroke=color, stroke_width=1.2 * s))
        # Connector line (not after last)
        if i < 3:
            x1 = cx_step + step_r
            x2 = cx_step + spacing - step_r
            if is_done:
                dwg.add(dwg.line(start=(x1, cy), end=(x2, cy), stroke=color, stroke_width=1.5 * s))
            else:
                dwg.add(dwg.line(start=(x1, cy), end=(x2, cy), stroke=color, stroke_width=1 * s, stroke_dasharray=f"{2*s},{2*s}"))


def render_wizard(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cy = size / 2
    # Numbered step panel
    panel_w = 26 * s
    panel_h = 18 * s
    panel_x = (size - panel_w) / 2
    panel_y = (size - panel_h) / 2
    dwg.add(dwg.rect(insert=(panel_x, panel_y), size=(panel_w, panel_h), rx=2 * s, ry=2 * s, fill="none", stroke=color, stroke_width=1.5 * s))
    # Title bar
    dwg.add(dwg.rect(insert=(panel_x, panel_y), size=(panel_w, 5 * s), rx=2 * s, ry=2 * s, fill=color))
    dwg.add(dwg.rect(insert=(panel_x, panel_y + 2 * s), size=(panel_w, 3 * s), fill=color))
    # Active step number circle
    active_step = 2 if modifier in {"active", "current", "step-2", "step-3"} else 3 if modifier == "step-4" else 1
    cx_circle = panel_x + 6 * s
    cy_circle = panel_y + 12 * s
    dwg.add(dwg.circle(center=(cx_circle, cy_circle), r=4 * s, fill=color))
    # Number indicator (white dot inside)
    dwg.add(dwg.rect(insert=(cx_circle - 2 * s, cy_circle - 0.5 * s), size=(4 * s, 1 * s), fill="#ffffff"))
    # Step description lines
    dwg.add(dwg.line(start=(cx_circle + 6 * s, cy_circle - 2 * s), end=(panel_x + panel_w - 3 * s, cy_circle - 2 * s), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(cx_circle + 6 * s, cy_circle), end=(panel_x + panel_w - 8 * s, cy_circle), stroke=color, stroke_width=1 * s))
    dwg.add(dwg.line(start=(cx_circle + 6 * s, cy_circle + 2 * s), end=(panel_x + panel_w - 12 * s, cy_circle + 2 * s), stroke=color, stroke_width=1 * s))
    # Footer nav buttons
    dwg.add(dwg.rect(insert=(panel_x + 4 * s, panel_y + panel_h - 5 * s), size=(6 * s, 3 * s), rx=1 * s, ry=1 * s, fill="none", stroke=color, stroke_width=1 * s))
    dwg.add(dwg.rect(insert=(panel_x + panel_w - 10 * s, panel_y + panel_h - 5 * s), size=(6 * s, 3 * s), rx=1 * s, ry=1 * s, fill=color))


def render_step(dwg: svgwrite.Drawing, size: int, modifier: str, color: str) -> None:
    s = size / 32.0
    cx = size / 2
    cy = size / 2
    # Determine which step number to show
    if "step-1" in modifier or modifier == "1":
        num = "1"
    elif "step-2" in modifier or modifier == "2":
        num = "2"
    elif "step-3" in modifier or modifier == "3":
        num = "3"
    elif "step-4" in modifier or modifier == "4":
        num = "4"
    else:
        num = "1"
    is_done = modifier in {"completed", "done", "finished"}
    is_active = modifier in {"active", "current", "selected", "primary"}
    if is_done:
        # Filled circle with check
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill=color))
        dwg.add(dwg.polyline(points=[
            (cx - 4 * s, cy),
            (cx - 1 * s, cy + 3 * s),
            (cx + 4 * s, cy - 3 * s),
        ], fill="none", stroke="#ffffff", stroke_width=2 * s, stroke_linejoin="round", stroke_linecap="round"))
    elif is_active:
        # Active step: thick ring + filled inner dot
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill="none", stroke=color, stroke_width=2.5 * s))
        dwg.add(dwg.circle(center=(cx, cy), r=4 * s, fill=color))
    else:
        # Default empty ring
        dwg.add(dwg.circle(center=(cx, cy), r=9 * s, fill="none", stroke=color, stroke_width=1.5 * s))
        # Number indicator (drawn as a small filled segment to suggest number)
        dwg.add(dwg.rect(insert=(cx - 4 * s, cy - 1 * s), size=(8 * s, 2 * s), fill=color))


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
