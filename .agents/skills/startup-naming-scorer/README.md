# startup-naming-scorer

A [Claude Code](https://claude.com/claude-code) skill that scores startup and product names against research-backed patterns instead of taste. Hand it a shortlist, a single candidate, or a blank page, and it tells you which names survive contact with the real world.

The scoring rubric weighs six criteria (slop words, syllable count, radio test, category words, domain availability, metaphorical resonance) and returns a 0 to 5 score with a verdict band. Alongside it sits the AI Slop Index, a four-tier catalog of the patterns that make a name sound like every other name in the batch: the "Labs" suffix, the "Deep" prefix, the -ly and -ify graveyard, Data[Thing] compounds. It is built from an analysis of 10,029 AI company names, 300+ YC companies across recent batches, and portfolios from a16z, Sequoia, First Round, Founders Fund, Techstars, and 500 Global.

## What's inside

- `SKILL.md`: the full method. Six-criterion scoring rubric with weights and bands, the four-tier AI Slop Index, the four naming tests (Radio, Crowded Bar, Building, Tell-a-Friend), the seven naming patterns ranked by success rate, category-specific guidance for B2B SaaS, consumer, and developer tools, and a seven-step workflow from context gathering to a scored top three. Pure methodology, no external dependencies.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install everything:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R startup-naming-scorer ~/.claude/skills/startup-naming-scorer
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to score a name, generate candidates, or compare finalists:

```
Score the name "Ballast" for a B2B revenue intelligence platform
```

```
Generate 20 two-syllable real-word candidates for a compliance-focused revenue engine
```

```
Compare and score: Timber vs Mandate vs Vertic
```

Claude gathers context on what the company does and who buys it, generates or takes your candidates, scores each against the rubric, runs all four naming tests, flags Slop Index violations, screens domains and trademark classes, then presents the top three to five with scores and reasoning. State your constraints up front (syllable limits, banned letters, no "AI" in the name, must be trademark-clean) and the skill honors them throughout.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
