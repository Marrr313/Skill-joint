# course-infographics

A [Claude Code](https://claude.com/claude-code) skill that turns course lesson content into
publication-ready infographics and short motion graphics, rendered with
[Remotion](https://www.remotion.dev/).

Point it at a lesson markdown file, a module directory, or just describe the idea. It reads
the content, decides whether the idea is better served by a still or a short animation,
picks the right layout variant, builds the props, and renders. Stills come out as 1920x1080
PNGs for vocabulary, overviews, checklists and command references. Motion graphics come out
as 3 to 8 second looping GIFs for process flows and comparisons. Both formats drop straight
into Skool, Kajabi, Teachable, Circle, or any self-hosted LMS.

Every graphic uses one editorial layout: a two-column asymmetric frame with a serif headline
on the left and a content variant on the right. The palette follows a 60-30-10 split and is
achromatic except for a single accent color, which is a parameter you set per project rather
than a fixed brand value.

## What's inside

- `SKILL.md` : the skill definition, workflow, flags, and verification checklist.
- `references/design-tokens.md` : the color system, the accent parameter, typography scale,
  8px spacing grid, canvas coverage minimums, and anti-patterns.
- `references/layout-modes.md` : the Editorial layout and its five still variants plus two
  motion variants, with the exact token values for each.
- `references/content-routing.md` : the decision flow that maps content signals to tier and
  variant, the one-idea-per-frame limits, the schematic icon library, and the TypeScript
  input schema.
- `references/motion-specs.md` : the six approved animation types, the timing table, easing
  rules, and the Remotion render commands.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills)
monorepo. Install it with:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy this folder into your Claude Code skills directory:

```bash
cp -R course-infographics ~/.claude/skills/course-infographics
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Set `REMOTION_PROJECT` to the Remotion project that hosts your compositions, then ask Claude
to "create an infographic for this lesson", "make a motion graphic for module 2", or run
`/course-infographics`:

```bash
export REMOTION_PROJECT=/path/to/your/remotion-project
```

Useful flags:

```
--type=still|motion      output tier (default: still)
--theme=dark|light       color theme (default: dark)
--duration=5s            motion length, 3 to 8 seconds
--accent=#0d8aff         accent color for the 10% band
```

Set `--accent` once for the course and every graphic follows, since nothing else in the
palette carries hue.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
