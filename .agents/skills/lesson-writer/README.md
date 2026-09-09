# lesson-writer

A [Claude Code](https://claude.com/claude-code) skill that writes course lesson content with real structural variety, in a voice you configure, and outputs HTML ready to paste into a course platform.

Generated course content has a habit of collapsing into one shape. Hook, "here is how it works," three bullets, a summary that restates the hook. It reads fine once. By lesson twelve the learner is skimming. This skill draws each lesson from a fifteen-section palette and enforces a rotation rule, so no two consecutive lessons share the same shape.

Voice is separated from structure. The engine handles section variety, procedural writing rules, reading level, and the anti-AI-tell pass. The voice lives in a single `voice-profile.md` you swap out per instructor or per brand.

## What's inside

- `SKILL.md` carries the engine: the section palette, ten procedural rules, structural craft rules, five example lesson shapes, the HTML output spec, and a pre-publish checklist.
- `voice-profile.md` is a neutral example profile (a plain-spoken practitioner voice) with the section headings the engine reads by name. Copy it, replace the contents, keep the headings.
- `references/banned-content.md` lists the words, phrases, and patterns that read as machine-written regardless of voice, plus a word-swap table.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install the whole collection:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R lesson-writer ~/.claude/skills/lesson-writer
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to "write a course lesson on X," "turn this outline into a lesson," "rewrite this lesson," or "write the lessons for this module." Point it at a source file if you have one:

```
Write a lesson from outline.md on setting up webhooks.
```

The skill loads a voice profile first and tells you which one it used. It looks for `voice-profile.md` at your project root or in `.claude/` before falling back to the one shipped here, so a project can carry its own voice without touching the skill.

Output is a narrow set of HTML tags that paste cleanly into Skool, Teachable, Circle, and most other course editors. Ask for Markdown instead if your platform prefers it.

For a whole module, tell Claude which section order the previous lesson used, or let it track the module as it goes. That log is what keeps the rotation honest.

### Building your own voice profile

Copy `voice-profile.md` and replace each section's contents, keeping the headings intact. If you have five or more pieces of the instructor's existing writing or transcripts, mine those rather than describing the voice from memory.

The [`brand-voice-extractor`](../brand-voice-extractor/) skill in this collection runs an interview that produces a structured profile you can paste straight into `voice-profile.md`.

### Companion skills

[`skool-course`](../skool-course/) publishes the resulting HTML to a Skool classroom. [`blog-writer`](../blog-writer/) applies the same engine-plus-profile split to long-form posts.

## License

MIT. See [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
