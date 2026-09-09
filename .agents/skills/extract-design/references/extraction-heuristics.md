# Extraction Heuristics

Procedural rules for turning raw harvested values into a coherent DESIGN.md token system. Apply these *after* running `scripts/extract_primitives.py` and *before* writing prose.

## Naming the system

The `name` field is the first thing an agent reads. Make it earn its position.

- Two-word names work best: a noun + an adjective or material. "Heritage." "Atmospheric Glass." "Paws and Paths." "Totality Festival."
- Avoid generic words ("Modern," "Clean," "Minimal") unless paired with something specific ("Modern Brutalism").
- The name should describe the *feel* the design produces, not the company. "AI Surfer" → not the name; "Wave Code" or "Saltwater Console" might be.
- If multiple sources for the same brand differ in feel, pick a name per file (e.g., `Wave Code Mint` vs. `Wave Code Indigo`).

## Compressing the color inventory

The script returns every distinct color it found. Most pages have 30–80. The DESIGN.md needs ~10–25 tokens.

**Compression rules:**

1. **Group near-duplicates.** `#1a1c1e`, `#1a1d1e`, `#1b1d1f` collapse to one ink token unless they appear in distinct semantic roles.
2. **Identify the role each color plays:**
   - `primary` — the color used for the dominant action / brand mark
   - `secondary` — supporting accent
   - `tertiary` — second accent, often used sparingly
   - `neutral` — the base background
   - `surface`, `surface-container`, `surface-container-high` — layered backgrounds when the design uses multiple
   - `on-primary`, `on-surface` — text/icon colors that sit *on* a given surface
   - `error`, `success`, `warning` — semantic colors when the source uses them distinctly
3. **Drop colors with no role.** A one-off `#fafafa` used in a single decorative element is not a token. It's noise.
4. **Express variants as separate tokens, not as alpha.** If the design uses `#1A1C1E` at 60% opacity for borders, define `outline: "#7d7e80"` (the resolved blended color) — not `rgba(...)`. Exception: glassmorphism systems where alpha *is* the system. In those cases, document literal `rgba(...)` strings inside components.

**Naming rules:**

- Numeric scales (`primary-10`, `primary-50`, `primary-90`) are valid and useful for systems that span tints/shades.
- Descriptive names (`boston-clay`, `limestone`, `midnight-forest`) work in the prose to give the system character — but the YAML token names should follow a *consistent* convention. Do not mix `primary-50` and `boston-clay` in the same file.
- Recommended convention for most extracts: semantic role names (`primary`, `secondary`, `neutral`) + variant suffixes (`-container`, `-dim`, `on-`).

## Typography scale

Most design systems have 6–15 levels. Aim for 8–12.

**Step-by-step:**

1. Group raw `font-size` values into clusters. Sizes within ~2px of each other usually represent the same level rendered at different breakpoints.
2. For each cluster, pick the desktop value as the canonical size.
3. Map clusters to roles:
   - `display-lg` / `display-md` — hero text only, 64px+
   - `headline-lg` / `headline-md` / `headline-sm` — section headings, 24–48px
   - `body-lg` / `body-md` / `body-sm` — paragraph text, 14–20px
   - `label-lg` / `label-md` / `label-sm` — buttons, captions, 11–14px
4. For each level, define `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, optionally `letterSpacing`.
5. If the design uses two distinct font families (e.g., serif headlines + sans-serif body), make that visible — don't normalize to one.
6. Quote `fontWeight` as a number (`fontWeight: 600`) or a string number (`fontWeight: "600"`). Both are valid per spec.

## Spacing scale

Pages reveal their spacing system through repeated values. Look at the script output for `spacing` (top values: padding, margin, gap).

- Identify the base unit. Most modern systems use 4px or 8px. Look for the GCD of the most common values.
- Build a scale: `xs`, `sm`, `md`, `lg`, `xl` — usually `4`, `8`, `16`, `24`, `32`, `64`.
- Values that appear once or twice usually quantize to the nearest scale step.
- Add domain-specific tokens when they earn their place: `gutter`, `container-padding`, `card-gap`, `section-margin`.

## Rounded scale

Border-radii usually cluster around 3–6 values. Common scales:

- Sharp systems: `0`, `2px`, `4px`
- Soft systems: `4px`, `8px`, `12px`, `16px`, `9999px`
- Pillowy / playful systems: `12px`, `24px`, `32px`, `9999px`

Map them to `none`, `sm`, `md`, `lg`, `xl`, `full`. If the inventory has `9999px` or `50%`, that's `full`.

## Components

Pick the components that *anchor* the system. A button system, a card system, an input. Stop there unless the source has additional load-bearing patterns (testimonial card, pricing card, hero block).

**Each component must:**

- Use token references for color values: `backgroundColor: "{colors.primary}"`, not `backgroundColor: "#1A1C1E"`.
- Use token references for typography: `typography: "{typography.label-md}"`.
- Use token references for rounded: `rounded: "{rounded.md}"`.
- Express variants as separate component entries: `button-primary`, `button-primary-hover`, `button-primary-disabled`. Only specify the props that *change* in the variant.

**Property reference:**

- `backgroundColor` — fill
- `textColor` — text/icon color
- `typography` — typography token reference
- `rounded` — corner radius
- `padding` — internal spacing
- `size`, `height`, `width` — dimensions

If a property doesn't fit the spec list (e.g., `borderColor`), the spec accepts it with a warning. Use sparingly.

## Elevation & Depth

Three common patterns:

1. **Shadow-based** — drop shadows define hierarchy. Document each shadow level (`shadow-sm`, `shadow-md`, `shadow-lg`) in the prose with its full CSS value.
2. **Tonal-layer-based** — slightly lighter or darker surfaces define hierarchy. No shadows. Common in editorial / Material-3 systems.
3. **Glass / blur-based** — `backdrop-filter: blur()` plus translucent backgrounds. Document blur radius and alpha values in prose.

The DESIGN.md spec doesn't have a token group for shadows yet. Document them in the `## Elevation & Depth` prose section, with explicit CSS values.

## Do's and Don'ts

These are *practical guardrails*, not platitudes. Bad: "Don't use ugly colors." Good: "Don't apply tertiary color to more than one element per screen." Each rule should:

- Reference a specific token or pattern by name.
- State an action ("Do" / "Don't").
- Be falsifiable — you can look at a design and tell if it broke the rule.

Aim for 4–8 rules. Cover:
- Color usage (where to apply primary / tertiary / accent)
- Typography pairing (when fonts mix)
- Contrast minimums
- Shape consistency (don't mix sharp and round)
- Density rules (when to use generous vs. tight padding)
