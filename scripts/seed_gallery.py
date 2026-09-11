"""Author the seed gallery: 5 controls icons for the ui-kit category.

Per the agreed plan, this script hand-writes the first batch of icons
(button, checkbox, radio, toggle, input) at 32x32 and 64x64 to lock
the visual style before any AI agent is dispatched. The agents that
follow will use these as a reference.
"""

from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------------
# SVG templates. Hand-authored, monochrome #000000, transparent background.
# Sizes are passed in and the templates scale coordinates accordingly.
# ----------------------------------------------------------------------------


def button_default(size: int) -> str:
    s = size / 32.0
    # Filled rounded rect with an evenodd label cutout
    x, y, w, h = 3 * s, 8 * s, 26 * s, 16 * s
    rx = 4 * s
    label_x, label_y, label_w, label_h = 10 * s, 15 * s, 12 * s, 2 * s
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <path fill="#000000" fill-rule="evenodd" '
        f'd="M {x},{y} h {w} a {rx},{rx} 0 0 1 0,{h} h -{w} a {rx},{rx} 0 0 1 0,{-h} z '
        f'M {label_x},{label_y} h {label_w} v {label_h} h -{label_w} z"/>\n'
        f'</svg>\n'
    )


def checkbox_default(size: int) -> str:
    s = size / 32.0
    box_x, box_y = 6 * s, 6 * s
    box_w, box_h = 20 * s, 20 * s
    rx = 2 * s
    sw = 2 * s
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <rect x="{box_x}" y="{box_y}" width="{box_w}" height="{box_h}" '
        f'rx="{rx}" ry="{rx}" fill="none" stroke="#000000" stroke-width="{sw}"/>\n'
        f'</svg>\n'
    )


def radio_default(size: int) -> str:
    s = size / 32.0
    cx, cy = size / 2, size / 2
    r = 10 * s
    sw = 2 * s
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="#000000" stroke-width="{sw}"/>\n'
        f'</svg>\n'
    )


def toggle_default(size: int) -> str:
    s = size / 32.0
    x, y, w, h = 4 * s, 10 * s, 24 * s, 12 * s
    r = h / 2
    sw = 2 * s
    knob_cx = x + r
    knob_cy = y + r
    knob_r = r - 3 * s
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" '
        f'fill="none" stroke="#000000" stroke-width="{sw}"/>\n'
        f'  <circle cx="{knob_cx}" cy="{knob_cy}" r="{knob_r}" fill="#000000"/>\n'
        f'</svg>\n'
    )


def input_default(size: int) -> str:
    s = size / 32.0
    x, y, w, h = 3 * s, 10 * s, 26 * s, 12 * s
    rx = 2 * s
    sw = 1.5 * s
    # Placeholder dashed line inside
    line_y = y + h / 2
    line_x1 = x + 5 * s
    line_x2 = x + 16 * s
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}">\n'
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
        f'fill="none" stroke="#000000" stroke-width="{sw}"/>\n'
        f'  <line x1="{line_x1}" y1="{line_y}" x2="{line_x2}" y2="{line_y}" '
        f'stroke="#000000" stroke-width="{1.5 * s}" '
        f'stroke-dasharray="{2 * s},{2 * s}"/>\n'
        f'</svg>\n'
    )


# ----------------------------------------------------------------------------
# Authoring: write SVG + render PNG for each icon at each size.
# ----------------------------------------------------------------------------


AUTHORS = {
    "button": button_default,
    "checkbox": checkbox_default,
    "radio": radio_default,
    "toggle": toggle_default,
    "input": input_default,
}


def main() -> None:
    count = 0
    for name, fn in AUTHORS.items():
        for size in (32, 64):
            svg_dir = ROOT / "svg" / str(size) / "ui-kit"
            png_dir = ROOT / "png" / str(size) / "ui-kit"
            svg_dir.mkdir(parents=True, exist_ok=True)
            png_dir.mkdir(parents=True, exist_ok=True)

            svg_path = svg_dir / f"{name}.svg"
            png_path = png_dir / f"{name}.png"
            svg_text = fn(size)
            svg_path.write_text(svg_text, encoding="utf-8")

            png_bytes = cairosvg.svg2png(
                bytestring=svg_text.encode("utf-8"),
                output_width=size,
                output_height=size,
            )
            img = Image.open(io.BytesIO(png_bytes)).copy()
            img.convert("RGBA").save(png_path, format="PNG")
            count += 1

    print(f"Authored {len(AUTHORS)} icons x 2 sizes = {count} SVG+PNG pairs")


if __name__ == "__main__":
    main()
