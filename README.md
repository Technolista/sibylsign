# sibylsign

> A comprehensive open-source collection of **65,535** mono-color icons for developers and designers.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Icons: 65,535](https://img.shields.io/badge/icons-65%2C535-brightgreen.svg)](#icon-catalog)
[![Validation: passing](https://img.shields.io/badge/validation-passing-success.svg)](#validation)
[![Sizes: 32 / 64](https://img.shields.io/badge/sizes-32%20%2F%2064-lightgrey.svg)](#repository-structure)

`sibylsign` provides an exhaustive icon set rendered as solid black glyphs, shipped in both **SVG** (vector) and **PNG** (raster) at **32×32** and **64×64** pixel sizes. Icons are organised into twelve thematic categories and named using descriptive kebab-case identifiers. Every icon is generated procedurally from a deterministic plan, so the corpus is reproducible and consistent.

## Features

- **65,535 distinct icons** spanning common UI elements, everyday concepts, and industries
- **Mono-color black** — single solid `#000000` fill, no transparency, no grayscale; recolour at the application layer
- **Two formats**: SVG (vector source) and PNG (raster)
- **Two sizes**: 32×32 and 64×64
- **Open source** under the MIT License
- **Categorised** into themed directories (`ui-kit`, `animals`, `food-drink`, `transportation`, `tools`, `weather`, `communication`, `clothing`, `sports`, `nature`, `symbols`, `icons-special`)
- **Indexable** via a generated `index.json` with 262,140 entries (one per `(format, size, concept)` tuple)

## Icon catalog

The full set of 65,535 icons is partitioned across twelve categories:

| Category | Concepts | Format |
|---|---|---|
| `ui-kit` | 5,200 | buttons, inputs, navigation, feedback, forms, … |
| `animals` | 6,000 | mammals, birds, reptiles, insects, sea life, … |
| `food-drink` | 6,000 | fruits, vegetables, dishes, drinks, … |
| `transportation` | 5,500 | cars, bikes, boats, planes, public transit, … |
| `tools` | 5,000 | hand tools, power tools, measuring tools, … |
| `weather` | 5,500 | sun, moon, clouds, rain, snow, storms, … |
| `communication` | 5,500 | phones, mail, video, signage, … |
| `clothing` | 5,500 | shirts, shoes, accessories, … |
| `sports` | 5,500 | balls, equipment, venues, … |
| `nature` | 5,500 | trees, flowers, landscapes, weather features, … |
| `symbols` | 5,000 | UI glyphs (arrows, controls, media, …) |
| `icons-special` | 5,335 | buildings, public venues, services, … |

Each icon is the result of composing simple geometric primitives — circles, squares, triangles, lines, and arcs — selected deterministically from a SHA-256 digest of the concept name. The composition is the same on every machine, so the corpus is reproducible.

## Repository structure

```
sibylsign/
├── svg/
│   ├── 32/<category>/<descriptive-name>.svg
│   └── 64/<category>/<descriptive-name>.svg
├── png/
│   ├── 32/<category>/<descriptive-name>.png
│   └── 64/<category>/<descriptive-name>.png
├── docs/
│   └── adr/
├── scripts/
│   ├── check_bootstrap.py    # T1: verify required files/dirs/deps
│   ├── check_catalog.py      # T2: verify catalog well-formedness
│   ├── generate.py           # T6: per-category (or 'all') generation
│   ├── rebuild_index.py      # T9: rebuild a single global index.json
│   └── validate.py           # T7: full-set validation
├── src/sibylsign/            # Python package: generator, catalog, pipeline, validation
├── tests/                    # 53 pytest cases covering every public seam
├── catalog.yaml              # T2: source of truth for category definitions
├── index.json                # Generated: 262,140 metadata entries
├── requirements.txt
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Usage examples

### Browse the index programmatically

`index.json` is a JSON array. Each entry has the shape:

```json
{
  "file_path": "svg/32/ui-kit/button-primary.svg",
  "category": "ui-kit",
  "descriptive_name": "button-primary",
  "color": "#000000"
}
```

To find every `weather` icon, filter on `category == "weather"`:

```bash
.venv/bin/python -c "
import json
data = json.load(open('index.json'))
weather = [e for e in data if e['category'] == 'weather']
print(f'{len(weather)} weather entries')
print(weather[0])
"
```

### Reference an icon in HTML

```html
<img src="svg/32/ui-kit/button-primary.svg" width="32" height="32" alt="Primary button">
```

### Recolour at runtime

Because every glyph uses a single `#000000` fill, you can recolour with CSS:

```css
.dark-icon { color: #000000; }       /* default */
.brand-icon { color: #1a73e8; }      /* recoloured */
.dark-icon, .brand-icon { fill: currentColor; }
```

(If you author a recoloured variant yourself, replace `fill="#000000"` in the SVG with `fill="currentColor"`.)

## Validation

Every file in the repository is checked by `scripts/validate.py`:

- SVG well-formedness (XML parseable, root element, declared dimensions)
- PNG dimensions match the declared size
- Filenames are kebab-case
- Paths match the canonical layout
- Every entry in `index.json` points to an existing file

The current set passes with **zero issues** across all 262,140 files.

## Regenerating the set

```bash
# Generate every category (long-running; ~5–10 minutes).
.venv/bin/python scripts/generate.py all

# Or one category at a time.
.venv/bin/python scripts/generate.py ui-kit

# Rebuild a single unified index.json from the filesystem.
.venv/bin/python scripts/rebuild_index.py

# Validate the result.
.venv/bin/python scripts/validate.py
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup, style guidelines, and the pull-request workflow.

## License

Released under the **MIT License** — see [`LICENSE`](LICENSE).
