# blog-writer

A [Claude Code](https://claude.com/claude-code) skill that writes blog posts and long-form articles in a voice you define, with structural variety and an anti-AI-tell pass built in.

The writing engine and the voice are separate. `SKILL.md` holds the engine: four rotating post shapes so every piece is not the same tidy arc, sentence-rhythm rules, rationed rhetorical devices, a banned-content list, and a pre-publish checklist. `voice-profile.md` holds the voice: stance, signature language, pronouns, opening patterns, evidence rules, and a hard "never do" list. Swap that one file and the same engine writes as someone else.

A neutral profile ships with the skill, so it works the moment you install it. It describes a builder writing about the systems they run, with concrete numbers and no invented authority. Replace it with your own when you are ready.

## What's inside

- `SKILL.md`: the engine, covering shape rotation, rhythm, pattern rationing, the checklist, and the interview for building a profile.
- `voice-profile.md`: the swappable voice definition, shipped with a working neutral example.
- `references/banned-content.md`: words, phrases, and structural patterns that read as machine-written in any voice.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install the whole collection:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy this folder into your Claude Code skills directory:

```bash
cp -R blog-writer ~/.claude/skills/blog-writer
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to "write a blog post about X," "draft an article in my voice," or "rewrite this draft so it does not read like AI." The skill loads the voice profile first, picks a post shape that differs from the last one, drafts, then runs the pre-publish checklist over its own output.

To write in your own voice, edit `voice-profile.md` and keep the section headings, since the engine reads them by name. If you have five or more existing pieces of your writing, point Claude at them and ask it to mine the profile from the real text rather than from self-description. Otherwise, `SKILL.md` includes a ten-question interview that produces a usable profile in one sitting.

The `brand-voice-extractor` skill in this same collection runs a longer structured interview and emits a voice profile you can paste straight into `voice-profile.md`.

Per-project voices work too: drop a `voice-profile.md` at a project root or in its `.claude/` directory and it takes precedence over the one shipped here.

## License

MIT. See [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
