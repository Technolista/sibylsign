# Contributing to sibylsign

Thank you for your interest in expanding the **sibylsign** icon set. This guide explains how to add new icons while keeping the corpus consistent, well-formed, and easy to navigate.

## License

sibylsign is released under the **MIT License**. By submitting a contribution, you agree that your work will be distributed under the same license. See [`LICENSE`](LICENSE) for the full text.

## Quick start

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/<your-username>/sibylsign.git
   cd sibylsign
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Verify the bootstrap is intact:

   ```bash
   python3 scripts/check_bootstrap.py
   ```

4. Generate icons for the category you are contributing to:

   ```bash
   python3 scripts/generate.py <category>
   ```

   For example, `python3 scripts/generate.py ui-kit` regenerates the `ui-kit` icons from the catalog.

5. Validate the result before opening a PR:

   ```bash
   python3 scripts/validate.py
   ```

## Where do new icons go?

Icons live under the project root in this layout:

```
svg/<size>/<category>/<descriptive-name>.svg
png/<size>/<category>/<descriptive-name>.png
```

- `<size>` is `32` or `64`. Both sizes must be provided for every icon.
- `<category>` is one of the keys defined in [`catalog.yaml`](catalog.yaml).
- `<descriptive-name>` is the kebab-case identifier of the concept (e.g. `button-primary`, `cloud-rain`).

The PNG file at the matching path must visually correspond to the SVG at the same size.

## Style guidelines

Every icon in sibylsign obeys a small set of contracts:

- **Mono-color black** — icons use a single solid color (no gradients, no transparency, no grayscale). The fill color is `#000000`.
- **Two sizes only** — `32×32` and `64×64` pixels. Other sizes are rejected by the validator.
- **Two formats** — SVG (vector source) and PNG (raster). Both must be present.
- **Kebab-case names** — file stems must match `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- **Square viewBox** — `width` and `height` attributes match the size; the viewBox is `0 0 N N`.

When contributing a manually refined icon, follow the same contracts. The simplest way to produce a conforming icon is to start from an output of `generate_svg()` and edit it, or to compose it from the same primitive shapes used by the generator (circles, squares, triangles, lines, arcs).

## Updating the index

Every icon in the project must be reflected in [`index.json`](index.json). After adding or modifying icons:

1. Regenerate the affected category:

   ```bash
   python3 scripts/generate.py <category>
   ```

2. Confirm the index entries are present and the files exist:

   ```bash
   python3 scripts/validate.py
   ```

The validator is the source of truth: if it reports zero issues, your contribution is internally consistent.

## Pull request process

1. Create a topic branch:

   ```bash
   git checkout -b add-<category>-<concept>
   ```

2. Make your changes and commit them with a clear message describing what was added or changed.

3. Push the branch and open a pull request against `main`.

4. In the PR description, list:
   - The category and concepts you contributed.
   - Any deviation from the auto-generated style (and why).
   - A confirmation that `scripts/validate.py` passes locally.

5. A maintainer will review the PR. Expect automated checks on well-formedness, sizing, and index consistency.

## Reporting issues

If you find a bug in the generator, validator, or pipeline, open an issue on GitHub with:

- A clear description of the problem.
- Reproduction steps (the command you ran and the output you saw).
- The output of `python3 scripts/check_bootstrap.py`.

## Code of conduct

Be respectful in issues, pull requests, and reviews. sibylsign is a community project; thoughtful, constructive feedback is welcome.
