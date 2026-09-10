# humanizer

A [Claude Code](https://claude.com/claude-code) skill that rewrites AI-generated,
human-facing prose — blog posts, emails, marketing copy, essays, docs, social
posts — to strip out the sentence-level and structural tells of AI writing,
without inventing facts or changing what the text actually says.

## What's inside

`SKILL.md` is a checklist-driven editing pass built from three public
sources:

- [blader/humanizer](https://github.com/blader/humanizer) (MIT, Siqi Chen) —
  the five-category pattern taxonomy (staging instead of stating, rhythm by
  rule, inflation and borrowed authority, formatting by rule, chatbot
  leftovers) and the mark-draft-check-vary editing process.
- Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
  essay (maintained by WikiProject AI Cleanup) — the puffery and
  invented-authority patterns ("industry experts say...").
- [StoryScope: Investigating idiosyncrasies in AI fiction](https://arxiv.org/abs/2604.03136)
  (Russell et al.) — the structural-level findings: AI narrators state their
  own theme explicitly far more often than human ones (77% vs. 52%), and lean
  on dialogue as illustration more often (59% vs. 34%), even once
  sentence-level style is cleaned up.

These are all independently written, publicly available sources — this
skill's text was written fresh, based on what each source documents, rather
than copied from any of them.

## Origin

This skill was requested via the `reel-to-skill` skill in this repository,
built from the transcript and caption of an Instagram reel by
[Jens Heitmann (@jens.heitmann)](https://www.instagram.com/jens.heitmann):
<https://www.instagram.com/reel/DbJzWBfxPvD/>. The reel describes combining
`blader/humanizer`, Wikipedia's AI-writing-signs essay, and a "StoryScope"
paper into one pass, then turning it into hooks and a `CLAUDE.md` rule so
every human-facing document runs through it automatically. This skill
implements the "one skill" version of that idea; wiring it into a `CLAUDE.md`
rule or a hook that runs automatically on human-facing output is a natural
next step, left for whoever adopts this skill to set up for their own repo.

## Install

Copy this folder into your Claude Code skills directory:

```bash
cp -R humanizer ~/.claude/skills/humanizer
```

## Use

Ask Claude to "humanize this," "make this sound less like AI," or hand it a
draft before you publish or send it. The skill walks the text against the
tell categories in `SKILL.md`, strongest signals first, and returns a rewrite
that keeps every fact the original supported.

## License

MIT. See [LICENSE](LICENSE).
