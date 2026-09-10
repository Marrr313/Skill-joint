---
name: humanizer
description: Rewrites AI-generated, human-facing prose (blog posts, emails, marketing copy, essays, docs, LinkedIn/social posts) to strip out telltale signs of AI writing — staged phrasing, forced triads, inflated vocabulary, decorative formatting, and flat narrative structure. Use this whenever the user asks to "humanize" text, make something "sound less like AI" or "less robotic," polish a draft before publishing or sending, or whenever a finished human-facing document is about to be handed over and deserves a self-check for AI tells first. Trigger on phrases like "make this sound human," "this reads like ChatGPT," "humanize my email/post/blog," or "remove the AI-isms."
---

# Humanizer

A language model writes whatever is statistically most likely to come next for
a wide, generic audience. That default behavior leaves fingerprints: uniform
pacing, staged delivery, inflated language, and — at a structural level —
stories and arguments that resolve too neatly and explain themselves out
loud. This skill catalogs those fingerprints and gives you a repeatable pass
for removing them without inventing facts or changing what the text actually
says.

Run this as a **rewrite pass on a finished draft**, not as a first-draft
generator. The input is text (yours, the user's, or something Claude already
wrote); the output is the same content with the AI tells edited out.

## Editing process

1. **Mark every tell**, strongest first (Category A below is strongest,
   E is weakest — see "Weighting the tells").
2. **Draft a rewrite** that keeps every fact, name, date, number, and
   claim the original supported. Never invent detail to replace a
   generic phrase — if the original was vague because the source
   material was vague, stay vague; don't manufacture specificity.
3. **Re-read for two things**: did any tell survive, and did any real
   fact get lost or softened in the rewrite?
4. **Vary the rhythm.** Read it aloud. Human writing has uneven sentence
   lengths and a few genuine asides or mixed feelings — it doesn't march.

## The tells, by category

### A. Staging instead of stating (strongest signal — one hit is enough to edit)

- **"Not X, but Y"** — negative framing bolted onto a claim to make it sound
  weightier than it is. Just state Y.
- **One-line closers** — a short punchy sentence that restates the previous
  point instead of adding to it ("And that changes everything.").
- **Deep-sounding openers** — "The real question is...", "Here's the thing:"
  masking an ordinary claim.
- **Staged run-ups** — "Let's dive in," "Buckle up," announcing that a point
  is coming instead of just making it.
- **Arguing with no one** — pre-emptively rebutting an objection nobody
  raised, to sound balanced.

### B. Rhythm by rule

- Forced triads — three examples, three adjectives, three steps, every time.
- The same sentence opener repeated across a paragraph.
- Em dashes used as a universal connector for anything that needs joining.
- Stacked qualifiers — "could potentially possibly."
- Hyphenated compound pairs everywhere ("results-driven," "forward-thinking").
- Passive voice that hides who actually did the thing.

### C. Inflation and borrowed authority

- Overused AI vocabulary: *crucial, landscape, testament, enhance, robust,
  seamless, elevate.*
- Inflating a routine fact into something significant ("a testament to...",
  "underscores the importance of...").
- Vague associations that gesture at a relationship without explaining it.
- Sales language applied to places, people, or organizations that didn't ask
  for a pitch.
- **Invented or unnamed authorities** — "industry experts say," "some critics
  argue," "observers have noted" — used to back a claim with a source that
  doesn't exist. (Documented at length in Wikipedia's [Signs of AI
  writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
  essay, alongside a related habit: listing what kind of press coverage a
  subject received and mischaracterizing what that coverage actually said.)
- Puffery — connecting some minor, arbitrary detail of the subject to a much
  bigger theme just to sound consequential.
- Avoiding plain verbs like "is" and "has" in favor of something fancier.

### D. Formatting by rule

- Bold used decoratively rather than to mark something you'd actually want a
  skimming reader to catch.
- Every heading capitalized like a title, even for casual writing.
- Emoji or arrows (→) used as bullet decoration.
- Curly quotation marks showing up in contexts (code, casual chat) where they
  don't belong.

### E. Leftovers from being a chatbot

- Greetings/closings that assume a chat interface ("Sure, here's...", "I hope
  this helps!", "Let me know if you'd like me to adjust anything!").
- Knowledge-cutoff or capability disclaimers with no reader who asked for one.
- Restating the heading in the first sentence under it.
- References to a previous version of the text the reader never saw
  ("as I mentioned above" when nothing was mentioned above in this draft).

### Structural tells (beyond the sentence level)

Sentence-level fixes aren't the whole story — AI writing has a structural
signature too, even once the vocabulary is cleaned up. The
[StoryScope](https://arxiv.org/abs/2604.03136) study (Russell et al.) found
that AI-generated fiction is separable from human writing with 93.2%
accuracy using *only* narrative-structure features — not style or word
choice — across ten dimensions: agents, social network, events, plot,
structure, setting, time, revelation, perspective, and style. Two findings
worth carrying into non-fiction editing too:

- **Over-explaining the point.** AI narrators state their theme outright far
  more often than human ones do (77% vs. 52% in the study). If a piece of
  writing tells the reader what its own moral or takeaway is instead of
  trusting them to get it, that's a tell — cut the explicit summary line.
- **Using dialogue or examples as a lecture.** AI text reaches for
  on-the-nose illustrative exchanges to make an abstract point (59% vs. 34%
  for humans). Prefer a concrete, specific example that shows the point
  without narrating what it proves.

More generally: human writing tends to have specific, slightly odd details
that don't serve the argument perfectly. AI writing tends to resolve too
cleanly and could, with minor edits, be about a different subject entirely.
If a paragraph would still make sense with the nouns swapped out, that's
worth a second look.

## Weighting the tells

- **One sighting of a Category A pattern** already justifies an edit — these
  are the strongest, most recognizable signals.
- **Categories B–E are weaker individually.** Don't rewrite a sentence just
  because it has one em dash; look for these patterns showing up in company
  with each other before treating them as a real tell.
- **Match the voice to the source.** A skill applied to a technical doc
  should not force it into the register of a marketing email, and vice
  versa. The goal is removing AI fingerprints, not imposing a new voice.
- **Never invent facts, names, dates, sources, or quotes** to replace a
  vague or generic-sounding original. If the input didn't support a claim,
  the output shouldn't either.
