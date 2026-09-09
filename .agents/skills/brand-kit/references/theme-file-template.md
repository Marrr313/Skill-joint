# Theme Markdown File Template

The companion `.md` theme file is a comprehensive text reference that documents every design decision. It is structured for both human designers and AI agents to follow without ambiguity.

## Required Sections

### 1. Header
```
# [Brand Name]: [Style Direction] Theme

> **Style Origin:** [Inspiration sources]
> **Mood:** [2-3 word mood descriptors]
> **Reference HTML:** [path to brand kit HTML]
```

### 2. Color System
Table format for each color group:

**Primary palette** covers backgrounds, borders, and text colors:
| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#000000` | [exact usage context] |

**Accent colors** each get a single-purpose rule:
| Token | Hex | Usage |
|-------|-----|-------|
| `--primary` | `#3B82F6` | [what this color is used for] |

**Color rules** are a numbered, non-negotiable list of what to never do.

### 3. Typography
- Font stack table (role, font, fallback, Google Fonts import)
- Full Google Fonts `<link>` tag ready to copy
- Display font rules (case, spacing, line-height, when to use/not use)
- Body font rules (weights used, sizes, line-height)
- **Full type scale table** with every element: font, size, weight, letter-spacing, line-height, transform, color

### 4. Spacing System
Token table: name, px value, usage context.

### 5. Borders & Surfaces
- Border treatments table (default, accent, heavy)
- Border behavior rules (width, style, radius, hover changes)
- Surface elevation table (ground, card, elevated), each with bg color, border, and trigger

### 6. Component Patterns
Each component gets:
- Layout specs (position, padding, max-width)
- Typography specs for each text element inside
- Border/background specs
- Hover/interaction behavior
- Complete CSS property values

Components to document: Nav, Hero, Buttons (primary + nav), Section layout, Cards, Pain points, Value ladder, Stat ticker, Trending list, CTA block, Footer.

### 7. Interaction States
Table with columns Element, Default, and Hover, covering every interactive element.
Plus specs for: Active, Focus, Disabled, Loading, Error, Empty states.

### 8. Imagery & Icons
Rules for: icons (library choice or none), images (treatment), decorative elements (allowed or not).

### 9. Voice & Copy Style
Per-element copy rules:
- Headline voice (examples + rules)
- Eyebrow voice
- Body copy voice
- CTA copy voice
- Pain point copy voice

### 10. Layout Principles
Grid philosophy, alignment rules, responsive breakpoints.

### 11. Animation & Motion
Duration, allowed properties, forbidden patterns.

### 12. Anti-Patterns
Table with columns Don't and Why, covering every visual rule that must not be broken.

### 13. CSS Custom Properties Block
Copy-paste-ready `:root { }` block with every token.

### 14. Quick Reference Cheat Sheet
One-line reminder per major decision (background, accent, fonts, borders, radius, shadows, gradients, buttons, motion, copy, icons, images).
