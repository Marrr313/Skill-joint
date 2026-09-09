# Layout: Editorial Only

All infographics use the Editorial layout. No exceptions. Data-dense and decorative modes
are deprecated.

Colors below reference the tokens in `design-tokens.md`. "Accent" means whatever `c10`
resolves to for the project (default `#0d8aff`, configurable).

---

## Structure

Two-column asymmetric (60/40 split):

```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  LABEL (mono, accent)            │                   │
│                                  │                   │
│  Headline                        │  [Right column    │
│  (serif, massive)                │   variant]        │
│                                  │                   │
│  ─── (accent line)               │                   │
│                                  │                   │
│  Body text                       │                   │
│  (sans, gray)                    │                   │
│                                  │                   │
│  MODULE 1 · LESSON 5             │                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Left column (always the same):**
1. Category label: monospace, uppercase, accent, wide letter-spacing
2. Headline: serif (Georgia / DM Serif Display), 120-160px, `#EEEEEE`
3. Accent line: 48-64px wide, 3px tall, accent
4. Body text: sans-serif, 36-48px, `#A3A3A3`
5. Module reference: monospace, bottom-left, `#333`

**Divider:** 1px vertical line between columns, `rgba(255,255,255,0.08)`

**Right column:** varies by content type (see below)

---

## Right-Column Variants: Stills

### Term List
Rows of term + definition separated by hairline dividers.
- Term: monospace, uppercase, wide tracking, `#666` (or `#EEEEEE` for emphasis)
- Definition: sans-serif, `#A3A3A3`
- Divider: `1px solid rgba(255,255,255,0.06)`
- Use for: vocabulary, command references

### Pull Quote + Stat
Italic serif quote in upper portion, large stat number at bottom.
- Quote: Georgia italic, `#666` (muted, not primary text)
- Stat value: sans-serif 900 weight, accent
- Stat label: monospace uppercase, `#666`
- Use for: concept explainers, key takeaways

### Numbered List
Ordered rows with monospace numbers.
- Number: accent for current or active, `#666` for others
- Item: sans-serif, `#EEEEEE` for active, `#A3A3A3` for others
- Use for: course overviews, module lists

### Checklist
Completion items with status indicators.
- Check mark: accent for done
- Dash: `#666` for not done
- Label: sans-serif, `#EEEEEE` for done, `#666` for not done
- Use for: module wrap-ups, skill summaries

### Terminal Block
Code or command mockup inside a subtle bordered container.
- Container: `#121212` background, `1px solid rgba(255,255,255,0.08)`, 4px radius
- Text: monospace, commands in `#EEEEEE`, output in `#666`
- Prompt: `$` in `#666`
- Success indicators: accent
- Use for: install steps, CLI demos

---

## Right-Column Variants: Motion Graphics

### Schematic Flow
Simplified icons (folders, clouds, terminals) connected by arrows, animating a process.
- Icons: flat, monochrome, constructed from basic shapes plus subtle borders
- Arrows: draw-on animation, directional, accent-tinted
- Labels: monospace underneath each icon
- Use for: git push, build pipelines, data flow

### Schematic Comparison
Before/after or this-vs-that with a visual transition.
- Two states shown side by side or transitioned between
- Use for: terminal vs editor, before and after

---

## Canvas Coverage Rules

- Content must fill **80%+ of canvas width** (1536px minimum at 1920x1080)
- Content must span **70%+ of canvas height** (756px minimum)
- Content must NOT cluster in one corner. Distribute across the full frame.
- Think poster design, not slide deck

If the host project ships a `DESIGN-RULES.md`, its coverage rules take precedence.

---

## Pairing With Thumbnails

Course lessons usually need a thumbnail as well as an infographic, and the two should not
look alike. Infographics stay calm and editorial. Thumbnails run loud and bold: heavier
display type, tighter crops, higher contrast. The shared accent is the only thread that
ties them together, which is why it stays a single configurable value across both.

| Property | Thumbnails | Infographics |
|----------|-----------|--------------|
| Background | Near-black, slightly cooler | `#0f0f0f` |
| Accent | Same `c10` | Same `c10` |
| Display font | Condensed grotesque, 700, often skewed | Georgia / DM Serif Display 400-700 |
| Energy | Loud, attention-grabbing | Calm, educational |
