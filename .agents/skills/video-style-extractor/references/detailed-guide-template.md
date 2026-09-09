# Detailed Single-Video Guide Template (STYLE-GUIDE-DETAILED.md)

Use this template to compile the final style guide. Replace all `[placeholder]` values with exact measurements extracted from the analysis steps. Delete any section that does not apply to the analyzed video(s).

---

# Style Guide: [Creator/Channel Name], [Style Name or Description]

> Extracted from [number] video(s) on [date]. Source: [URLs or filenames].

## 1. Canvas & Dimensions

| Property | Value |
|----------|-------|
| Aspect ratio | [e.g., 9:16] |
| Resolution | [e.g., 1080x1920] |
| Frame rate | [e.g., 30fps] |
| Duration range | [e.g., 45-60s] |
| Safe zone (top) | [px from top edge where content starts] |
| Safe zone (bottom) | [px from bottom edge where content stops] |
| Safe zone (sides) | [px from left/right edges] |

## 2. Color Palette

### Primary Colors

| Role | Hex | OKLCH | Usage |
|------|-----|-------|-------|
| Background (primary) | [#000000] | [oklch(0 0 0)] | [Where and when used] |
| Background (secondary) | [#hex] | [oklch(...)] | [Where and when used] |
| Text (primary) | [#hex] | [oklch(...)] | [Headlines, body, etc.] |
| Text (secondary) | [#hex] | [oklch(...)] | [Subtitles, captions, etc.] |
| Accent | [#hex] | [oklch(...)] | [Highlights, emphasis, CTAs] |

### Overlay & Effects

| Effect | Value |
|--------|-------|
| Background gradient | [direction, stops with hex + positions] |
| Vignette | [color, opacity, spread] |
| Color filter on B-roll | [description, hex overlay, opacity] |
| Text shadow | [color, x-offset, y-offset, blur-radius] |

## 3. Typography

### Headline / Hook Text

| Property | Value |
|----------|-------|
| Font family | [exact name or closest match] |
| Font weight | [100-900] |
| Size | [px at 1080p / % of canvas height] |
| Case | [uppercase / lowercase / sentence / mixed] |
| Color | [#hex] |
| Letter spacing | [px or em] |
| Line height | [unitless ratio or px] |
| Text align | [left / center / right] |
| Position | [% from top, % from left] |
| Stroke | [color, width in px] |
| Shadow | [color, offset-x, offset-y, blur] |
| Max width | [% of canvas width] |

### Caption / Subtitle Text

| Property | Value |
|----------|-------|
| Font family | [exact name] |
| Font weight | [100-900] |
| Size | [px at 1080p] |
| Position | [% from top] |
| Highlight style | [color change / background box / underline / scale / bold] |
| Highlight color | [#hex] |
| Non-highlighted color | [#hex] |
| Background box | [color, opacity, padding, border-radius] |
| Words per group | [number] |
| Transition | [how captions swap: cut, fade, slide] |

### Secondary Text (if present)

| Property | Value |
|----------|-------|
| Font family | [name] |
| Font weight | [value] |
| Size | [px] |
| Color | [#hex] |
| Usage | [where it appears] |

## 4. Text Animation

### Entry Animations

| Text Type | Animation | Duration | Easing | Stagger |
|-----------|-----------|----------|--------|---------|
| Headline | [fade / slide-up / scale / typewriter / bounce] | [ms] | [ease-out / spring / linear] | [per-word delay in ms, or "none"] |
| Caption | [animation type] | [ms] | [easing] | [stagger] |
| Secondary | [animation type] | [ms] | [easing] | [stagger] |

### Hold & Exit

| Text Type | Hold Duration | Exit Animation | Exit Duration |
|-----------|--------------|----------------|---------------|
| Headline | [ms] | [fade / slide / scale / none] | [ms] |
| Caption | [ms] | [animation type] | [ms] |
| Secondary | [ms] | [animation type] | [ms] |

## 5. B-Roll & Asset Presentation

### Footage Treatment

| Property | Value |
|----------|-------|
| Framing | [full bleed / inset / picture-in-picture / split screen] |
| Border | [color, width, radius] |
| Shadow | [color, offset, blur, spread] |
| Scale behavior | [static / ken burns / zoom in / zoom out] |
| Scale amount | [start% to end%] |
| Scale duration | [ms] |
| Color treatment | [none / desaturate / warm filter / cool filter / specific LUT] |
| Vignette | [present/absent, settings] |

### Screen Recordings / Screenshots

| Property | Value |
|----------|-------|
| Device frame | [yes/no, type: browser / phone / none] |
| Corner radius | [px] |
| Drop shadow | [color, offset, blur] |
| Scale | [% of canvas] |
| Position | [% from top, % from left] |
| Entry animation | [type, duration, easing] |

## 6. Editing & Cut Pattern

### Timeline Map

| # | Timestamp | Duration | Content Type | Transition In |
|---|-----------|----------|-------------|--------------|
| 1 | [0:00.0] | [ms] | [talking head / B-roll / text card / screen recording] | [hard cut / crossfade / zoom / etc.] |
| 2 | [0:XX.X] | [ms] | [type] | [transition] |
| ... | ... | ... | ... | ... |

### Cut Statistics

| Metric | Value |
|--------|-------|
| Total cuts | [number] |
| Average cut length | [ms] |
| Shortest cut | [ms] |
| Longest cut | [ms] |
| Cut rhythm | [regular / accelerating / decelerating / variable] |
| Primary transition | [hard cut / crossfade / etc.] |
| Transition duration | [ms] |

### Motion Effects

| Effect | When Used | Speed | Direction | Easing |
|--------|-----------|-------|-----------|--------|
| Zoom | [trigger condition] | [ms] | [in / out] | [easing] |
| Pan | [trigger condition] | [ms] | [direction] | [easing] |
| Shake | [trigger condition] | [intensity, duration] | n/a | n/a |
| Background motion | [always / conditional] | [description] | n/a | n/a |

## 7. Audio Production

### Voice

| Property | Value |
|----------|-------|
| Speaker | [human / AI-generated] |
| Voice ID (if AI) | [ElevenLabs voice ID or name] |
| Tone | [authoritative / conversational / excited / calm] |
| WPM (overall) | [number] |
| WPM (hook section) | [number] |
| WPM (body section) | [number] |
| Avg pause between sentences | [ms] |
| Dramatic pause length | [ms] |

### Music

| Property | Value |
|----------|-------|
| Genre / mood | [description] |
| BPM | [number] |
| Volume (relative to voice) | [% or dB] |
| Ducking | [yes/no, drops during speech by X dB] |
| Entry | [fade in over X ms / hard start] |
| Exit | [fade out over X ms / hard stop] |

### Sound Effects

| SFX | Trigger | Timing | Volume |
|-----|---------|--------|--------|
| [whoosh / click / ding / etc.] | [on cut / on text appear / on emphasis] | [timestamp or relative to event] | [% of voice volume] |

## 8. Storytelling Template

### Narrative Structure

| Act | Timestamp | Duration | Purpose | Emotional Beat |
|-----|-----------|----------|---------|---------------|
| Hook | [0:00-0:XX] | [Xs] | [what it accomplishes] | [curiosity / shock / intrigue] |
| Build | [0:XX-0:XX] | [Xs] | [what it accomplishes] | [tension / education / proof] |
| Climax | [0:XX-0:XX] | [Xs] | [what it accomplishes] | [surprise / payoff / revelation] |
| Close | [0:XX-0:XX] | [Xs] | [what it accomplishes] | [satisfaction / urgency / CTA] |

### Psychological Hooks Used

- [ ] Curiosity gap: [how it's implemented]
- [ ] Contrast / before-after: [how it's implemented]
- [ ] Social proof: [how it's implemented]
- [ ] Authority: [how it's implemented]
- [ ] Scarcity / urgency: [how it's implemented]
- [ ] Identity alignment: [how it's implemented]
- [ ] Open loop: [how it's implemented]
- [ ] Pattern interrupt: [how it's implemented]

### Fill-in-the-Blank Script Template

```
[HOOK, X seconds]
[Hook type: question / bold claim / pattern interrupt]
"[Opening line structure with blanks for topic insertion]"

[BUILD, X seconds]
[Build type: proof / education / story]
"[Build structure with blanks]"

[CLIMAX, X seconds]
[Climax type: reveal / payoff / transformation]
"[Climax structure with blanks]"

[CLOSE, X seconds]
[Close type: CTA / callback / cliffhanger]
"[Closing structure with blanks]"
```

### Vernacular Fingerprint

| Pattern | Value |
|---------|-------|
| Avg sentence length | [X words] |
| You:I pronoun ratio | [X:1] |
| Register | [casual / conversational / authoritative / formal] |
| Specificity level | [high (numbers, names) / medium / low (vague)] |
| Signature transitions | [list the most-used transition words/phrases] |
| Rhetorical devices | [questions, lists, repetition, contrast, with examples] |
| Power words | [list the emotionally-loaded words used] |

### Retention Mechanics

| Mechanic | Implementation | Timestamp |
|----------|---------------|-----------|
| Open loop | [description] | [when introduced, when resolved] |
| Pattern interrupt | [description] | [timestamp] |
| Payoff timing | [description] | [timestamp] |
| Visual-audio sync | [description] | [timestamps] |

## 9. Remotion Component Architecture

Recommended component structure for recreating this style in Remotion:

```
src/
├── Root.tsx                    # Composition config (fps, duration, dimensions)
├── Video.tsx                   # Main sequence orchestration
├── components/
│   ├── CaptionOverlay.tsx      # Animated word-by-word captions
│   ├── HeadlineText.tsx        # Hook/headline text with entry animations
│   ├── BRollClip.tsx           # B-roll with framing, scale, color treatment
│   ├── ScreenRecording.tsx     # Screen recordings with device frame
│   ├── TextCard.tsx            # Full-screen text cards
│   ├── BackgroundMusic.tsx     # Music with ducking logic
│   └── SFXLayer.tsx            # Sound effects triggered by frame
├── styles/
│   └── tokens.ts               # All design tokens exported as constants
├── lib/
│   ├── animations.ts           # Reusable spring/interpolation configs
│   ├── timing.ts               # Cut timing map and sequence helpers
│   └── captions.ts             # Caption data and highlight logic
└── assets/
    ├── fonts/                  # Custom fonts
    ├── audio/                  # Music + SFX files
    └── footage/                # B-roll clips
```

### Key Tokens (fill with extracted values)

```typescript
export const TOKENS = {
  // Canvas
  width: [1080],
  height: [1920],
  fps: [30],

  // Colors
  bgPrimary: '[#hex]',
  bgSecondary: '[#hex]',
  textPrimary: '[#hex]',
  textSecondary: '[#hex]',
  accent: '[#hex]',
  captionHighlight: '[#hex]',

  // Typography
  headlineFont: '[font name]',
  headlineWeight: [700],
  headlineSize: [px],
  captionFont: '[font name]',
  captionWeight: [700],
  captionSize: [px],

  // Animation
  textEntryDuration: [ms],
  textEntryEasing: '[easing]',
  cutTransitionDuration: [ms],

  // Audio
  musicVolume: [0-1],
  duckingVolume: [0-1],
  duckingAttack: [ms],
  duckingRelease: [ms],
} as const;
```

## 10. Production Checklist

Use this checklist when producing a new video in this style:

### Pre-Production
- [ ] Script follows the storytelling template (Section 8)
- [ ] Script matches vernacular fingerprint (sentence length, pronouns, register)
- [ ] Script hits target WPM for each section
- [ ] Hook is under [X] seconds
- [ ] Total duration is [X-X] seconds

### Asset Preparation
- [ ] Voiceover recorded/generated matching voice characteristics
- [ ] Voiceover transcribed with word-level timestamps
- [ ] B-roll clips sourced and trimmed
- [ ] Screen recordings captured at correct resolution
- [ ] Background music selected (matching BPM and genre)
- [ ] Sound effects prepared

### Visual Assembly
- [ ] Canvas dimensions match (Section 1)
- [ ] All colors match palette exactly (Section 2)
- [ ] Fonts loaded and match spec (Section 3)
- [ ] Text animations match timing and easing (Section 4)
- [ ] B-roll framing and treatment applied (Section 5)
- [ ] Cut timing follows the pattern (Section 6)
- [ ] Motion effects applied at correct moments (Section 6)

### Audio Mix
- [ ] Voice volume normalized
- [ ] Music volume set relative to voice (Section 7)
- [ ] Ducking active during speech segments
- [ ] SFX triggered at correct timestamps (Section 7)
- [ ] No audio clipping or dead spots

### Final Review
- [ ] Watch full video at 1x speed. Does it "feel" like the reference?
- [ ] Compare side-by-side with reference video
- [ ] Check captions sync with audio
- [ ] Verify safe zones, no content cut off on mobile
- [ ] Export at correct resolution and frame rate
