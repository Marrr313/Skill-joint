# ui-workflow

A [Claude Code](https://claude.com/claude-code) skill that gives UI work an actual pipeline instead of letting the model jump straight to code. Structure first as ASCII wireframes, then a design PRD, then mockups, then implementation, then a browser-rendered check against the spec.

The centerpiece is the anti-vibe-code checklist: a concrete audit of the tells that make AI-generated interfaces recognizable at a glance. Emojis standing in for icons, bright clashing palettes the model picked on its own, duplicated KPI cards, seven pricing tiers, landing pages made of text and generic feature icons. Run every screen against it before shipping.

## What's inside

- `SKILL.md` is the whole skill: the four-step pipeline (wireframes, PRD, mockups, integration), the UI best practices (shadcn/ui primitives, design tokens, the critique-then-redesign loop, reference screenshots, the eight required interaction states), and the anti-vibe-code checklist.

No scripts and no dependencies. Step 2 optionally uses the community [stitch-mcp](https://www.npmjs.com/package/stitch-mcp) server for Google Stitch mockups, and `SKILL.md` carries the full setup, but the pipeline works without it. The visual feedback loop wants any browser automation MCP, such as [Playwright MCP](https://github.com/microsoft/playwright-mcp).

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install everything:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or take just this one:

```bash
cp -R ui-workflow ~/.claude/skills/ui-workflow
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to build any interface, a dashboard, a landing page, a settings screen, and the skill routes the work through the pipeline. It will hand you ASCII wireframes for approval before it writes a line of CSS.

You can also invoke a single piece of it directly:

- "Audit this page against the anti-vibe-code checklist"
- "Write the design PRD for this app first"
- "Critique this component, then redesign it fixing everything you listed"

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
