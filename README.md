# sibylsign

> A comprehensive open-source collection of **65,535** mono-color icons for developers and designers.

`sibylsign` provides an exhaustive icon set rendered as solid black glyphs, shipped in both **SVG** (vector) and **PNG** (raster) at **32×32** and **64×64** pixel sizes. Icons are organized into thematic categories and named using descriptive kebab-case identifiers.

## Features

- **65,535 distinct icons** spanning common UI elements, industries, and concepts
- **Mono-color black** (no transparency, no grayscale) for easy recoloring
- **Two formats**: SVG (vector) and PNG (raster)
- **Two sizes**: 32×32 and 64×64
- **Open source** under the MIT license
- **Categorized** into themed directories (e.g., `ui-kit`, `animals`, `tools`)
- **Indexable** via a generated `index.json` metadata file

## Repository Structure

```
sibylsign/
├── svg/
│   ├── 32/
│   │   └── <category>/<descriptive-name>.svg
│   └── 64/
│       └── <category>/<descriptive-name>.svg
├── png/
│   ├── 32/
│   │   └── <category>/<descriptive-name>.png
│   └── 64/
│       └── <category>/<descriptive-name>.png
├── docs/
│   └── adr/
├── scripts/
│   └── check_bootstrap.py
├── requirements.txt
├── LICENSE
└── README.md
```

## Quick Start

```bash
git clone https://github.com/Technolista/sibylsign.git
cd sibylsign
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Verify the bootstrap

```bash
python3 scripts/check_bootstrap.py
```

## License

MIT — see [LICENSE](LICENSE).
