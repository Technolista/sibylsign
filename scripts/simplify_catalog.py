"""Simplify catalog.yaml: ui-kit uses per-base states, others unchanged."""

import yaml
from pathlib import Path

catalog_path = Path("catalog.yaml")
with catalog_path.open("r", encoding="utf-8") as fh:
    cat = yaml.safe_load(fh)

ui_kit = cat["categories"]["ui-kit"]
bases = ui_kit["base_concepts"]

default_states = ["default", "filled", "outline"]

state_overrides = {
    "button": ["default", "filled", "disabled"],
    "checkbox": ["unchecked", "checked", "indeterminate"],
    "radio": ["unchecked", "checked", "disabled"],
    "toggle": ["off", "on", "disabled"],
    "switch": ["off", "on", "disabled"],
    "slider": ["default", "active", "disabled"],
    "input": ["default", "focused", "disabled"],
    "select": ["default", "open", "disabled"],
    "textarea": ["default", "focused", "disabled"],
    "knob": ["low", "mid", "high"],
    "dial": ["default", "active", "disabled"],
    "wheel": ["default", "active", "disabled"],
    "icon-button": ["default", "active", "disabled"],
    "drag-handle": ["default", "active", "disabled"],
    "resize-handle": ["default", "active", "disabled"],
    "splitter": ["vertical", "horizontal", "default"],
    "menu": ["default", "active", "collapsed"],
    "dropdown": ["default", "open", "disabled"],
    "tab": ["default", "active", "disabled"],
    "pagination": ["default", "active", "disabled"],
    "breadcrumb": ["default", "current", "disabled"],
    "navbar": ["default", "active", "collapsed"],
    "sidebar": ["default", "collapsed", "active"],
    "footer": ["default", "compact", "expanded"],
    "header": ["default", "compact", "expanded"],
    "stepper": ["default", "active", "completed"],
    "wizard": ["default", "active", "completed"],
    "step": ["default", "active", "completed"],
    "alert": ["info", "warning", "error"],
    "badge": ["default", "active", "notification"],
    "toast": ["default", "success", "error"],
    "spinner": ["default", "active", "loading"],
    "progress-bar": ["default", "active", "complete"],
    "skeleton": ["default", "avatar", "card"],
    "placeholder": ["image", "text", "default"],
    "loader": ["default", "vertical", "active"],
    "indicator": ["default", "online", "offline"],
    "counter": ["default", "notification", "zero"],
    "notification": ["default", "active", "unread"],
    "callout": ["default", "tooltip", "popover"],
    "error": ["default", "filled", "warning"],
    "warning": ["default", "filled", "caution"],
    "info": ["default", "filled", "help"],
    "success": ["default", "filled", "celebration"],
}

new_ui_kit = {
    "count": 0,
    "description": (
        "Hand-authored UI element icons. Each base concept carries ~3 curated "
        "states instead of a Cartesian modifier product."
    ),
    "subcategories": {
        "controls": [
            "button", "input", "checkbox", "radio", "toggle", "slider",
            "switch", "knob", "dial", "wheel", "icon-button", "select",
            "textarea", "drag-handle", "resize-handle", "splitter",
        ],
        "navigation": [
            "menu", "dropdown", "tab", "pagination", "breadcrumb",
            "navbar", "sidebar", "footer", "header", "stepper",
            "wizard", "step",
        ],
        "feedback": [
            "alert", "badge", "toast", "spinner", "progress-bar",
            "skeleton", "placeholder", "loader", "indicator",
            "counter", "notification", "callout", "error", "warning",
            "info", "success",
        ],
    },
    "base_concepts": [],
}

total = 0
for base in bases:
    states = state_overrides.get(base, default_states)
    for state in states:
        new_ui_kit["base_concepts"].append(f"{base}-{state}")
        total += 1

new_ui_kit["count"] = total
cat["categories"]["ui-kit"] = new_ui_kit

others = {k: v["count"] for k, v in cat["categories"].items() if k != "ui-kit"}
print(f"ui-kit: {total}")
print(f"others: {others}")
print(f"sum: {sum(others.values()) + total}")

with catalog_path.open("w", encoding="utf-8") as fh:
    yaml.safe_dump(cat, fh, sort_keys=False, allow_unicode=True, width=120)
print("catalog.yaml updated")
