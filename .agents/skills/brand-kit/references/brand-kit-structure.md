# Brand Kit Structure Reference

## Table of Contents
1. [Section Order](#section-order)
2. [Color System Patterns](#color-system-patterns)
3. [Typography Patterns](#typography-patterns)
4. [Component State Patterns](#component-state-patterns)
5. [Do's & Don'ts Patterns](#dos--donts-patterns)
6. [Voice & Copy Patterns](#voice--copy-patterns)
7. [Style Direction Presets](#style-direction-presets)

---

## Section Order

Brand kit HTML pages MUST follow this exact section sequence. Each section gets a number (01-13), an eyebrow label, and a heading.

| # | Section | Category | Purpose |
|---|---------|----------|---------|
| 01 | Logo & Wordmark | Identity | Logo variations, construction rules, clear space, min size |
| 02 | Color System | Identity | Primary accent (with opacity variants), functional accents, neutral scale |
| 03 | Typography | Identity | Font specimens, character sets, weight samples |
| 04 | Type Hierarchy | Foundations | Every text element at rendered size with metadata |
| 05 | Spacing | Foundations | Token table with visual bars |
| 06 | Borders & Surfaces | Foundations | Border treatments, elevation levels, corner rules |
| 07 | Buttons | Components | All states: default, hover, focus, disabled, loading |
| 08 | Cards | Components | Default, hovered, featured states + grid behavior |
| 09 | Badges & Tags | Components | Archetype/category badges with anatomy |
| 10 | Navigation | Components | Live demo + specification table |
| 11 | Voice & Copy | Guidelines | Copy examples per element type |
| 12 | Do's & Don'ts | Guidelines | Side-by-side visual comparisons |
| 13 | Motion & Animation | Guidelines | Duration, properties, easing, scroll rules |

---

## Color System Patterns

### Primary Accent Swatch
Show as a tall block (200px height) with the color name in large display font inside. Below the swatch, show a grid of metadata:
- HEX value
- RGB value
- CSS Token name
- Usage description

Include an opacity variants strip: Dim (10%), Glow (25%), Full (100%), each rendered as a horizontal band with the rgba value shown.

### Functional Accents
4-column grid. Each swatch has:
- Color block (160px height) with role name inside (e.g., "MONEY", "INFO", "URGENCY", "BRAND")
- Below: CSS token, hex, usage description, usage tags as bordered inline labels

### Neutral Scale
Single horizontal strip with all neutrals from darkest to lightest. Each chip shows the name and hex. Text color adapts for contrast (light text on dark chips, dark text on light chips).

---

## Typography Patterns

### Font Card Structure
Each font gets its own card:
- Font name as eyebrow label
- Font family CSS string in monospace
- Large sample text at the font's primary size
- Full character set (A-Z, a-z if applicable, 0-9, symbols)
- Weight samples in a row (each weight as a column with weight name + sample text)
- Note box with critical rules (e.g., "never bold this font", "always pair with text-transform: uppercase")

### Type Hierarchy Specimens
Each text element is a horizontal row with two columns:
- **Left column (260px, dark bg):** Metadata, meaning element name, font, and size/height/spacing
- **Right column:** Live rendered sample at actual size and style

Elements to include (adapt to brand):
- Hero headline
- Section title
- Eyebrow (display font)
- Eyebrow (body font)
- Card title
- Body paragraph
- Stat number
- Label / meta text

---

## Component State Patterns

### Button States
Show as a horizontal row of cells. Each cell contains:
- State label at top (10px uppercase)
- Button rendered in that state

States to show (in order):
1. Default: standard appearance
2. Hover: background/color change
3. Focus: outline ring
4. Disabled: reduced opacity, not-allowed cursor
5. Loading: text swap to "LOADING..."

### Card States
3-column grid:
1. Default: resting borders and colors
2. Hovered: accent border, elevated background
3. Featured: permanently highlighted with the accent border

### Badge Specimens
Show each badge type in a row. Below, show anatomy as rule blocks:
- Font specs
- Padding
- Text color rules
- Border radius (always zero in bold styles)

---

## Do's & Don'ts Patterns

### Layout
2-column grid. Left = DO (green header with checkmark). Right = DON'T (red header with X).

### Structure per pair
```
┌─────────────────────┬─────────────────────┐
│ ✓ DO                │ ✗ DON'T             │
│─────────────────────│─────────────────────│
│ [Visual example]    │ [Visual example]    │
│─────────────────────│─────────────────────│
│ Brief explanation   │ Brief explanation   │
└─────────────────────┴─────────────────────┘
```

### Essential Do/Don't pairs to include:
1. **Corner treatment:** sharp vs rounded
2. **Depth method:** borders vs shadows
3. **Color fills:** flat vs gradient
4. **Typography:** display font for headlines only vs display font for body
5. **Color usage:** functional colors used correctly vs misused
6. **Section backgrounds:** consistent bg vs tinted sections
7. **Copy style:** direct/specific vs hedging/corporate

---

## Voice & Copy Patterns

### Voice Card Grid
2-column grid, each card shows:
- Voice label (display font, accent color)
- Live example rendered in the actual style
- Note explaining the rules

### Element types to cover:
1. **Headlines:** commanding, fragment sentences, periods not exclamation marks
2. **Eyebrows:** 2-4 word section labels
3. **Body copy:** conversational, specific numbers, "you" language
4. **CTA buttons:** imperative verbs, action-first
5. **Pain points:** first-person quoted italic statements
6. **Stat labels:** short descriptors, no articles

---

## Style Direction Presets

When the user provides a style direction, use these as starting configurations. Always customize based on the specific brand.

### Bold Creator
- **Mood:** Aggressive confidence, direct, no hedging
- **Background:** Pure black #000000
- **Primary accent:** One high-contrast signal color, e.g. #FF3B30 signal red or #00E5A0 electric green
- **Display font:** Condensed or impact face (Oswald, Anton, Archivo Black)
- **Body font:** Clean geometric sans (Sora, Inter, DM Sans)
- **Borders:** 2px solid, sharp corners, zero radius
- **Shadows:** None
- **Motion:** 0.2s transitions only, no animations
- **Copy:** Short, punchy, commanding

### Dark Tech
- **Mood:** Sophisticated, developer-forward, clean
- **Background:** Near-black #0A0A0F
- **Primary accent:** Cool-toned (indigo, violet, cyan)
- **Display font:** Geometric sans (Space Grotesk, Geist)
- **Body font:** Neutral sans (Inter, system-ui)
- **Borders:** 1px solid, subtle, small radius (6-8px)
- **Shadows:** Subtle, layered
- **Motion:** Smooth, spring-based, scroll-triggered reveals
- **Copy:** Technical, precise, understated

### Premium Modern
- **Mood:** Trustworthy, polished, enterprise-ready
- **Background:** Light gray #F8F9FC or white
- **Primary accent:** Vibrant (violet, blue-cyan gradient)
- **Display font:** Rounded geometric (Plus Jakarta Sans, Clash Display)
- **Body font:** Humanist sans (DM Sans, Inter)
- **Borders:** 1px solid, generous radius (12-16px)
- **Shadows:** Layered, glassmorphic
- **Motion:** Smooth, parallax, gradient animations
- **Copy:** Clear, confident, professional
