# Content Routing

Maps lesson content to the correct output tier (still vs motion) and right-column variant.
All compositions use the Editorial layout, so routing only determines what goes in the right
column.

---

## Decision Flow

```
Content in → Is this a concept that needs visualization?
  YES → Motion graphic (GIF, 3-8s loop)
    → Process/flow? → Schematic Flow
    → Comparison? → Schematic Comparison
  NO → Still image (PNG)
    → Has terms/definitions? → Term List
    → Has a key quote + number? → Pull Quote + Stat
    → Has ordered items? → Numbered List
    → Has completion items? → Checklist
    → Has CLI commands? → Terminal Block
```

---

## Routing Table

| Content Signal | Tier | Right-Column Variant |
|---------------|------|---------------------|
| Vocabulary or term definitions | Still | Term List |
| Concept with a memorable quote and a stat | Still | Pull Quote + Stat |
| Module overview or ordered sequence | Still | Numbered List |
| Completion summary or skills learned | Still | Checklist |
| CLI commands or install steps | Still | Terminal Block |
| Process flow (A → B → C) | Motion | Schematic Flow |
| Before/after or this-vs-that | Motion | Schematic Comparison |

---

## One Idea Per Frame

Heavy lessons must be split across multiple graphics. Rules:

- **Maximum 5 terms** per Term List graphic. If a lesson has 11 commands, split into "Core
  Commands" (5) and "Bonus Commands" (6).
- **Maximum 1 concept** per Pull Quote + Stat graphic.
- **Maximum 10 items** per Numbered List graphic.
- **Maximum 6 items** per Checklist graphic.
- **Maximum 1 process** per Schematic Flow graphic. If a lesson covers commit, push and
  revert, either show the full cycle in one flow or split into individual graphics.

When splitting, each graphic gets its own headline and body text. Do not just paginate.

---

## Schematic Icon Library

Motion graphics use simplified schematic icons. These are constructed from basic CSS shapes
(divs with borders, border-radius, background colors). No SVG files, no icon fonts.

| Concept | Icon | Construction |
|---------|------|-------------|
| Local project / folder | Folder shape | Tab div + body div with file lines inside |
| Remote / cloud | Cloud shape | Overlapping rounded divs |
| Terminal | Terminal window | Dark rect with 3 dots + monospace text |
| File | Document | Rect with folded corner |
| Arrow / flow | Directional arrow | Line div + triangle border-hack |
| Success | Checkmark | Accent `✓` character or drawn angle |
| Website | Browser window | Rect with address bar |

Keep icons monochrome (`#1a1a1a` fills, `rgba(255,255,255,0.1)` borders) with the accent
reserved for active and success states.

---

## TypeScript Input Schema

```ts
type OutputTier = 'still' | 'motion';
type StillVariant = 'term-list' | 'pull-quote-stat' | 'numbered-list' | 'checklist' | 'terminal-block';
type MotionVariant = 'schematic-flow' | 'schematic-comparison';
type Theme = 'dark' | 'light';

interface InfographicInput {
  // Required
  headline: string;
  label: string;           // Category label (e.g., "VOCABULARY", "GIT", "TERMINAL")
  body: string;            // Body text below headline

  // Tier and variant (auto-detected if omitted)
  tier?: OutputTier;
  variant?: StillVariant | MotionVariant;
  theme?: Theme;           // default: 'dark'
  accent?: string;         // hex accent color; default: '#0d8aff'

  // Content (provide what applies to the variant)
  terms?: Array<{ term: string; definition: string }>;
  pullQuote?: string;
  statValue?: string;
  statLabel?: string;
  items?: Array<{ number?: string; label: string; active?: boolean }>;
  checklist?: Array<{ label: string; done: boolean }>;
  codeLines?: Array<{ type: 'prompt' | 'output' | 'success'; text: string }>;
  flowSteps?: Array<{ icon: string; label: string }>;
  comparison?: { before: { label: string; items: string[] }; after: { label: string; items: string[] } };

  // Metadata
  moduleRef?: string;      // e.g., "MODULE 1 · LESSON 5"

  // Rendering (motion only)
  duration?: number;       // seconds, 3-8, default: 5
}
```

---

## Output

| Tier | Format | Resolution | Notes |
|------|--------|-----------|-------|
| Still | PNG | 1920x1080 | Single frame |
| Motion | GIF | 1920x1080 | Loopable, 3-8 seconds |
