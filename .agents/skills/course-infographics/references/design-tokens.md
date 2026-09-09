# Design Tokens

All infographics follow the 60-30-10 proportion rule: 60% dominant (background), 30%
secondary (text and neutrals), 10% accent (a single configurable color).

---

## The Accent Parameter

The palette is achromatic except for one accent. That accent is a **parameter**, not a
constant.

| Property | Value |
|----------|-------|
| Token | `c10` |
| Default | `#0d8aff` |
| Set via | `--accent` flag, `ACCENT_COLOR` env var, or a project design config |
| Derived: dim | accent at 12% alpha (default `rgba(13,138,255,0.12)`) |
| Derived: glow | accent at 25% alpha (default `rgba(13,138,255,0.25)`) |

Change `c10` and the whole system follows, because nothing else in the palette carries hue.
Pick the course's own color, or keep the default. Throughout these references, "accent"
always means whatever `c10` resolves to.

---

## Color Tokens

### Dark Theme (Primary)

| Role | Proportion | Token | Value | Usage |
|------|-----------|-------|-------|-------|
| Dominant | 60% | `c60` | `#0f0f0f` | Background canvas |
| Dominant surface | n/a | `c60Surface` | `#121212` | Terminal blocks, cards |
| Dominant surface 2 | n/a | `c60Surface2` | `#1a1a1a` | Schematic icon fills |
| Dominant surface 3 | n/a | `c60Surface3` | `#252525` | Active states |
| Secondary primary | 30% | `c30Primary` | `#EEEEEE` | Headlines, key data |
| Secondary secondary | n/a | `c30Secondary` | `#A3A3A3` | Body text, definitions |
| Secondary tertiary | n/a | `c30Tertiary` | `#666666` | Labels, metadata, term labels |
| Secondary muted | n/a | `c30Muted` | `#404040` | Module ref, disabled |
| Secondary border | n/a | `c30Border` | `rgba(255,255,255,0.08)` | Vertical divider, hairlines |
| Secondary border strong | n/a | `c30BorderStrong` | `rgba(255,255,255,0.15)` | Terminal block borders |
| Accent | 10% | `c10` | configurable, default `#0d8aff` | Key information only |
| Accent dim | n/a | `c10Dim` | accent at 12% alpha | Accent backgrounds |
| Accent glow | n/a | `c10Glow` | accent at 25% alpha | Glow bloom behind accent elements |

### Light Theme (Alt)

Same structure, warm ivory base. Not the current focus.

| Role | Token | Value |
|------|-------|-------|
| Dominant | `c60` | `#faf9f5` |
| Surface | `c60Surface` | `#ffffff` |
| Primary text | `c30Primary` | `#141413` |
| Body text | `c30Secondary` | `#5e5d59` |
| Accent | `c10` | configurable, same value as dark theme |

---

## Typography

Three-font system. **Nothing below 24px** at 1920x1080 canvas.

| Role | Font | Size | Weight | Tracking | Line Height |
|------|------|------|--------|----------|-------------|
| Headline | Georgia / DM Serif Display | 120-160px | 400-700 | -0.02em | 1.0 |
| Body text | Inter / system-ui | 36-48px | 400 (light) / 500 (dark) | 0 | 1.55 |
| Label / overline | JetBrains Mono / ui-monospace | 24-28px | 600 | 0.3em | 1.2 |
| Pull quote | Georgia / DM Serif Display | 40px | 400 italic | 0 | 1.3 |
| Key statistic | Inter / system-ui | 96-120px | 900 | -0.03em | 1.0 |
| Term name | JetBrains Mono / ui-monospace | 28-36px | 700 | 0.15em | 1.4 |
| Term definition | Inter / system-ui | 28-36px | 400 | 0 | 1.5 |
| Module reference | JetBrains Mono / ui-monospace | 24px | 400 | 0.25em | 1.0 |

### Font loading

Use `@remotion/google-fonts` with local bundling. Fallback stacks:
- DM Serif Display, then Georgia, then serif
- Inter, then system-ui, then sans-serif
- JetBrains Mono, then ui-monospace, then SF Mono, then monospace

### Text transform rules

- Labels and overlines: `uppercase`
- Headlines: sentence case (editorial, not aggressive)
- Module references: `uppercase` monospace
- Term names: uppercase for vocabulary, as-is for commands (`pwd`, `ls`)

---

## Spacing

Strict 8px grid. All values must be multiples of 8.

| Token | Value | Usage |
|-------|-------|-------|
| `framePadding` | 64px | Outer canvas padding |
| `sectionGap` | 48px | Between major sections |
| `elementGap` | 24px | Between related elements |
| `cardPadding` | 32-48px | Inside terminal blocks |
| `borderWidth` | 1-2px | Borders, dividers |
| `borderRadius` | 4px | Terminal blocks only (0px for everything else) |
| `accentLineWidth` | 48-64px | Accent divider width |
| `accentLineHeight` | 3px | Accent divider thickness |

---

## Canvas Coverage

- Content must fill **80%+ of canvas width** (1536px min at 1920x1080)
- Content must span **70%+ of canvas height** (756px min)
- No content clustering in one area. Distribute across the full frame.
- Two-column split: ~58% left, ~38% right, ~4% divider zone

---

## Accent Usage Rules

The accent appears ONLY on meaningful whole elements:

### DO use accent on:
- Category label text (one per graphic)
- Accent line divider
- Single key stat number
- Active or current item in a list (one row)
- Success checkmarks
- Glow bloom behind accent elements

### DO NOT use accent on:
- Individual letters within a word
- Multiple items simultaneously
- Borders (unless a terminal block highlight)
- Large background fills
- Decorative elements

---

## Depth Layers

Three static overlays for cinematic depth:

### 1. Vignette
```css
/* Full-canvas overlay */
background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.3) 100%);
```

### 2. Accent Glow
```css
/* Behind each accent element; color = c10 */
filter: blur(20px);
opacity: 0.25;
color: var(--c10);
```

### 3. Film Grain (optional)
```css
/* SVG noise filter at 3-5% opacity */
filter: url(#grain);
opacity: 0.04;
```

---

## Anti-Patterns

| Anti-Pattern | Instead |
|-------------|---------|
| Pure `#000` + `#FFF` | `#0f0f0f` + `#EEEEEE` |
| Accent on individual letters | Accent on whole elements only |
| Multiple accent colors | A single `c10` |
| Text below 24px | Minimum 24px at 1920x1080 |
| Content in <80% of canvas | Fill the frame, poster design |
| Rounded corners >4px | Sharp (0px) or 4px max |
| Drop shadows on dark bg | Lighter surface + border |
| Data-dense or decorative layouts | Editorial only |
