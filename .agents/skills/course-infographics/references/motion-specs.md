# Motion Specs

Specifications for animated compositions rendered via Remotion, output as looping GIFs (3-8
seconds). Every animated composition must also render cleanly as a static still (final
frame).

"Accent" below means whatever `c10` resolves to for the project (default `#0d8aff`,
configurable). See `design-tokens.md`.

---

## Output Format

| Property | Value |
|----------|-------|
| Format | GIF (loopable) |
| Resolution | 1920x1080 |
| Duration | 3-8 seconds |
| FPS | 30 (60fps is wasted on the GIF format) |
| Loop | Seamless or hold-on-final-frame |

---

## Animation Vocabulary

Six approved motion types. No others without explicit discussion.

### 1. Fade + TranslateY (primary)
- Elements fade in from `opacity: 0` + `translateY(20px)` to final position
- Left column animates first, right column follows
- Stagger: 100-150ms between elements

### 2. Line Draw
- Accent line grows from `width: 0` to final width
- Vertical divider draws from `height: 0` (top) to full height
- Arrow lines draw on in the direction of flow

### 3. Accent Glow
- Soft bloom behind accent elements
- Implementation: duplicate the accent element, apply gaussian blur (radius 20-30px), set
  opacity 0.2-0.3, position behind
- Static. Does not animate, just adds depth.

### 4. Vignette
- Subtle radial gradient overlay darkening the canvas edges
- Implementation: full-canvas div with
  `radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.3) 100%)`
- Static. Always present, never animates.

### 5. Film Grain (optional)
- 3-5% noise overlay for cinematic texture
- Implementation: CSS `filter: url(#noise)` with an SVG turbulence filter, or a pre-rendered
  noise PNG at low opacity
- Static, or very slow animation (if animating, 0.5fps shift)

### 6. Schematic Animation (motion graphics only)
- Icons slide in from off-screen or scale from 0.9 to 1.0
- Arrows draw on with directional flow (left-to-right, or following the process direction)
- Labels fade in after their icon settles
- Process steps animate sequentially, not simultaneously

---

## Timing Table

| Element | Duration | Easing | Delay from start |
|---------|----------|--------|-----------------|
| Left column label | 300ms | ease-out | 0ms |
| Left column headline | 400ms | ease-out | 100ms |
| Accent line draw | 400ms | ease-out | 300ms |
| Left column body text | 400ms | ease-out | 500ms |
| Vertical divider draw | 500ms | ease-out | 400ms |
| Right column content | 400ms | ease-out | 700ms |
| Right column stagger (per item) | 300ms | ease-out | +120ms each |
| Schematic icon entrance | 400ms | ease-out | 800ms+ |
| Arrow draw-on | 300ms | ease-out | after icons settle |
| Hold at final state | 1500-3000ms | n/a | after all reveals |

Total reveal sequence: ~1.5-2.5s. Hold for 1.5-3s. Loop or hold.

---

## Easing

- **Primary:** `ease-out` (deceleration, calm and confident)
- **Never use:** `linear` (mechanical), `spring` or `elastic` (chaotic for educational
  content)
- **Remotion implementation:** use `interpolate()` with `Easing.out(Easing.cubic)` for
  smooth deceleration
- **Minimum duration:** 250ms per element. Anything faster feels anxious.

---

## Animation Rules

1. **GPU-only properties:** only animate `transform` and `opacity`. Never animate `width`,
   `height`, `margin`, `padding`.
2. **Stagger, don't simultaneous:** elements reveal in sequence, left-to-right,
   top-to-bottom.
3. **Still fallback:** every composition's final frame must work as a standalone PNG.
4. **Smooth loops:** if looping, either fade all elements out in reverse order before
   looping, or hold the final frame and let the GIF loop back to frame 1.
5. **No typewriter effect:** terminal blocks show content via fade-in, not character-by-
   character typing. Keeps the minimal aesthetic.
6. **One motion per element:** each element gets one animation (fade + translate). No
   element bounces, pulses, or has compound motion.

---

## Remotion Configuration

```ts
// For GIF output
{
  fps: 30,
  width: 1920,
  height: 1080,
  durationInFrames: fps * durationSeconds, // 90-240 frames for 3-8s
}
```

### Render Commands

```bash
cd "$REMOTION_PROJECT"

# GIF output
npx remotion render src/infographics/Root.tsx <CompositionId> \
  --output=out/<name>.gif \
  --image-format=png \
  --props='<json>'

# Still (final frame)
npx remotion still src/infographics/Root.tsx <CompositionId> \
  --output=out/<name>.png \
  --props='<json>'

# Preview
npx remotion preview src/infographics/Root.tsx
```

---

## Cinematic Depth

Three static depth layers applied to all compositions:

1. **Vignette:** darkens edges, draws the eye to content center
2. **Accent glow:** soft bloom behind accent elements, adds dimensionality
3. **Film grain:** optional 3-5% noise, breaks the "too digital" feel

These are NOT animated. They are static overlays that add production value without adding
motion complexity.
