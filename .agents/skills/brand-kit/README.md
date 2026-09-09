# brand-kit

A [Claude Code](https://claude.com/claude-code) skill that turns a brand into two documents: a self-contained HTML style guide you can open in a browser, and a companion markdown theme file that any designer or coding agent can build from without ever seeing the HTML.

The HTML kit runs 13 numbered sections covering logo, color, typography, type hierarchy, spacing, borders and surfaces, buttons, cards, badges, navigation, voice, do's and don'ts, and motion. Components are rendered in every state (default, hover, focus, disabled, loading) rather than described, and each do/don't pair shows the correct and incorrect version side by side as actual markup. The markdown theme file mirrors all of it as tables plus a copy-paste `:root {}` token block.

## What's inside

- `SKILL.md`: the skill definition and the five-step workflow, from gathering brand context to opening the finished kit.
- `references/brand-kit-structure.md`: the canonical section order and the layout patterns for each one (color swatches, font cards, state rows, do/don't grids, voice cards), plus three style direction presets to start from.
- `references/theme-file-template.md`: the 14-section template for the companion markdown theme file.

The three presets are Bold Creator (black, one high-contrast signal accent, condensed display face, sharp corners), Dark Tech (near-black, cool accent, subtle elevation), and Premium Modern (light, vibrant accent, generous radius, layered shadows). They are starting configurations, not finished looks: the skill customizes every token to the actual brand.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install everything at once:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R brand-kit ~/.claude/skills/brand-kit
```

Claude Code auto-discovers skills by their `SKILL.md` front matter, so it works from a plugin's `skills/` directory too.

## Use

Ask Claude to "create a brand kit for [brand]", "build a style guide", or "document the visual identity for this project". The skill asks for a brand name, style direction, primary accent hex, and font pairing, then builds both files into a `themes/` directory and opens the HTML for review.

If you already have branding to work from, hand it over first: an existing landing page, a theme file, a logo, or brand copy. The skill reads real source and extracts the tokens instead of asking you to retype them. It will not invent a logo, wordmark, or tagline. If an asset it needs is missing, it says so rather than shipping a placeholder.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
