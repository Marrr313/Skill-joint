# Project instructions

## Human-facing writing

Before finalizing any human-facing prose in this repo — README updates, skill
descriptions written for people to read, PR descriptions, commit messages
meant to explain "why" to a human reviewer, or any other document a person
(not a script) will read — run it through the `humanizer` skill
(`.claude/skills/humanizer/SKILL.md`) first. Check the draft against its tell
categories (staged phrasing, forced triads, inflated vocabulary, decorative
formatting, over-explained structure) and fix what it finds before treating
the writing as done. Skip this for code, configuration, and machine-read
files (SKILL.md frontmatter, JSON, YAML) where none of this applies.
