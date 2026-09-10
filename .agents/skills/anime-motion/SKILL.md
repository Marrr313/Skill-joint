---
name: anime-motion
description: Build web animation with anime.js v4 — scroll-driven narratives, timelines, text splitting, SVG line drawing and counters. Covers the v3→v4 API break, verified CDN URLs, and the scroll-scrub pattern that survives reverse scroll.
when_to_use: When adding animation to a web page or app — scroll-triggered reveals, scrubbed scroll narratives, staggered entrances, animated counters, SVG drawing, or draggable UI. Also when migrating anime.js v3 code to v4.
---

# anime.js v4 motion

MIT licensed. Source: https://github.com/juliangarnier/anime

## Loading it

**npm** — `npm i animejs` then `import { animate, createTimeline, onScroll, stagger, utils } from 'animejs'`.

**Browser script tag** — jsDelivr only. **cdnjs does not host v4** (its `animejs` package
stops at v2.x; `3.2.2/anime.min.js` is the newest file that resolves there):

```html
<script src="https://cdn.jsdelivr.net/npm/animejs@4.5.0/dist/bundles/anime.umd.min.js"></script>
```

118KB minified, global `anime`. In a CSP-restricted context (Claude Artifacts, for example)
jsDelivr `/npm/` is usually allowed where other hosts are not — check before assuming.

## v3 → v4 is a hard break

v3's single default-export `anime({...})` is gone. v4 is a set of named exports:

```
animate  createTimeline  createTimer  createAnimatable  createDraggable  createScope
createSpring  onScroll  stagger  svg  text  utils  waapi  eases  engine
split  splitText  scrambleText  morphTo  createDrawable  createMotionPath  createLayout
```

Other traps when porting:
- `easing: 'easeOutExpo'` → `ease: 'out(4)'` (or pass a `cubicBezier(...)`).
- Targets are the first positional argument: `animate(target, params)`, not `{targets: …}`.
- `anime.timeline()` → `createTimeline()`; still `.add()`, `.seek()`, `.play()`, `.pause()`, `.label()`.
- Helpers moved onto `utils`: `utils.clamp`, `utils.lerp`, `utils.mapRange`, `utils.round`,
  `utils.random`, `utils.snap`, `utils.get`, `utils.$`.

## The scroll-scrub pattern

`onScroll({ sync: true, … })` binds an animation to scroll position. It is the ergonomic path,
but for a multi-stage narrative prefer **deriving state as a pure function of scroll position**
and driving anime.js from that:

```js
function tick() {
  const r = stage.getBoundingClientRect();
  const span = r.height - window.innerHeight;
  const p = utils.clamp(-r.top / span, 0, 1);   // 0→1 across the stage
  paint(p);                                      // pure: same p always gives same frame
}
window.addEventListener('scroll', () => {
  if (queued) return;
  queued = true;
  requestAnimationFrame(() => { queued = false; tick(); });
}, { passive: true });
```

**Why bother:** a scrubbed page has to survive reverse scroll, trackpad momentum, and
restoring mid-page on reload. If every visual is a pure function of `p`, reverse scroll is
correct by construction — there is no state to unwind. Timelines that `.play()` on an
IntersectionObserver do not have this property and desynchronise on the way back up.

Park a stage on the active step rather than sliding continuously, or the panel drifts past
the content it belongs to:

```js
const STARTS = [0, 0.20, 0.40, 0.58, 0.86, 1.0001];
let i = 0; for (let k = 0; k < 5; k++) if (p >= STARTS[k]) i = k;
const local = (p - STARTS[i]) / (STARTS[i+1] - STARTS[i]);
const f = i + utils.clamp((local - 0.8) / 0.2, 0, 1);  // slide only in the last 20%
```

## Recipes

**Staggered entrance**
```js
animate('.card', { y: [14, 0], opacity: [0, 1], delay: stagger(80), ease: 'out(3)', duration: 420 });
```

**Masked line reveal** — wrap each line in an `overflow:hidden` block, animate the inner span.
Give the wrapper `padding-bottom:.11em; margin-bottom:-.11em` or descenders and any
`background-clip:text` gradient get clipped.
```js
animate('.line .word', { y: ['110%', 0], opacity: [0, 1], duration: 900, ease: 'out(3)' });
```

**Counter** — animate a proxy object, format in `onUpdate`. Always pair with
`font-variant-numeric: tabular-nums` so digit widths don't jitter.
```js
const o = { v: 0 };
animate(o, { v: 24180, duration: 1400, ease: 'out(3)',
  onUpdate: () => el.textContent = Math.round(o.v).toLocaleString('en-US') });
```

**SVG line drawing**
```js
animate(svg.createDrawable('.path'), { draw: ['0 0', '0 1'], duration: 1500, ease: 'out(3)' });
```

**Text splitting** — `text.split(el, { words: true, chars: true })`, then animate the returned nodes.

## Non-negotiables

- **Respect `prefers-reduced-motion`.** Check it once, and render the *end state* — content fully
  visible, counters at final value, nothing mid-transition. Never just disable the animation and
  leave elements parked at `opacity: 0`.
- **Never gate content on an observer without a failsafe.** Add the reveal class behind a `js`
  class and a timeout, so a failed observer cannot leave the page blank.
- **Pause offscreen loops.** An IntersectionObserver that clears timers and cancels the rAF when
  the element leaves the viewport costs nothing and stops burning battery.
- **Cap canvas cost.** Render decorative canvas at a fraction of device resolution and scale up
  with a CSS blur; watch frame time and stop the loop if it degrades, leaving the last frame painted.
