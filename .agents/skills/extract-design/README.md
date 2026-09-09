# extract-design

A [Claude Code](https://claude.com/claude-code) skill that reverse-engineers a `DESIGN.md` file from an existing visual identity — an HTML page, CSS file, screenshot, live URL, or design export.

It produces a `DESIGN.md` that conforms to the [google-labs-code/design.md](https://github.com/google-labs-code/design.md) spec: YAML token frontmatter (colors, typography, rounded, spacing, components) plus prose sections (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts). The result is a portable, AI-readable description of a design system that other coding agents can use to rebuild the same look.

## What's inside

- `SKILL.md` — the skill definition and workflow.
- `scripts/extract_primitives.py` — a zero-dependency Python script that harvests frequency-ranked raw primitives (colors, fonts, sizes, weights, radii, spacing, shadows, gradients, class hints) from HTML/CSS. Stdlib only; runs on Python 3.9+.
- `references/spec.md` — the normative design.md spec.
- `references/extraction-heuristics.md` — how to normalize raw primitives into a token system.
- `references/example-*.md` — calibration examples for the prose voice.

## Install

Copy this folder into your Claude Code skills directory:

```bash
cp -R extract-design ~/.claude/skills/extract-design
```

Or drop it into a plugin's `skills/` directory if you distribute it as part of a plugin. Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to "extract design from this page", "make a DESIGN.md from this HTML/screenshot/URL", or run `/extract-design`. For HTML/CSS sources the skill first runs the primitive extractor, then normalizes the output into a coherent token system before writing the `DESIGN.md`.

You can also run the extractor directly:

```bash
python3 scripts/extract_primitives.py path/to/file.html [more files...] --top 30
```

## License

MIT — see [LICENSE](LICENSE).
