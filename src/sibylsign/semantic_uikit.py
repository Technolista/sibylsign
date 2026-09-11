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
