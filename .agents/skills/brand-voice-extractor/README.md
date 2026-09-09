# brand-voice-extractor

A [Claude Code](https://claude.com/claude-code) skill that extracts an authentic brand voice through a structured, direct-response-style interview, then synthesizes the answers into a reusable voice profile.

The interview is organized around 6 pillars — **Intent, Message, Soul, Voice, Positioning, Shadow** — each with primary questions, adaptive follow-up probes, and live observation tasks. The output is a structured Voice Profile (mission, core belief, origin, tonality, signature phrases, objections, boundaries, and example quotes) suitable for AI training, copywriting, or content creation.

## What's inside

- `SKILL.md` — the complete interview protocol, output template, interview principles, and common pitfalls. No external dependencies; the skill is pure methodology.

## Install

Copy this folder into your Claude Code skills directory:

```bash
cp -R brand-voice-extractor ~/.claude/skills/brand-voice-extractor
```

Or include it in a plugin's `skills/` directory. Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to "extract brand voice", "create a voice guide", "capture how someone speaks", or "build a voice profile". Claude runs the interview phase by phase, follows the energy, probes for specifics, then produces the Voice Profile in the documented format.

## License

MIT — see [LICENSE](LICENSE).
