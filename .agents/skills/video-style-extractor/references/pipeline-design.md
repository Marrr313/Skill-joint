# Pipeline Design

How the extractor is put together: what each stage does, what it outputs, and where each algorithm breaks down. Read this when you need to reason about a result rather than just produce one.

## Mission

Extract a brand's short-form video aesthetic (colors, typography, motion grammar, pacing, overlays) from a cohort of reference videos, and extract a pixel-art mascot animation profile detailed enough to drive AI image generators (static assets) and AI image-to-video generators (animated assets) without manual prompt tuning.

The output is two classes of artifact:
- **A, text prompts**: ready-to-paste blocks for Midjourney/Ideogram/FLUX/Nano Banana (static) and Runway/Kling/Pika/Veo/Sora (animated).
- **B, reference image kit**: isolated mascot PNGs, sprite sheet, canonical reference frame, palette file.

## Non-goals

- Audio feel cloning (source separation, audio tagging). The mission is visual.
- Loop and retention structural analysis.
- Remotion code generation, which belongs to a video-building skill such as `remotion-video-builder`.
- Video generation itself. This skill is analyzer-only.
- Full motion-spec JSON for a manual animator rebuild. The deliverable is text plus reference images.
- Kinetic typography timing extraction via OCR.

## Architecture

Deterministic Python helpers under `scripts/` (scene detection, background removal, palette quantization, resolution and fps detection, sprite sheet, audio metrics, run log) wrapped by an instruction-driven workflow in `SKILL.md`. Gemini 2.5 Pro is the reasoning engine for everything that is a vision-language judgment.

Dependencies: `scenedetect`, `rembg`, `Pillow`, `scikit-learn`, `scikit-image`, `opencv-python`, `numpy`, `imagehash`, `google-genai`, plus `ffmpeg` on the PATH.

### Pipeline (per run)

```
1. Ingest                 Accept folder of .mp4/.mov OR URL list.
                          Build <working-dir>/per-video/<slug>/.

2. Scene segmentation     PySceneDetect ContentDetector per video ->
                          scenes.json with [start_ms, end_ms] ranges.

3. Scene-aware sampling   1 frame per scene + 2fps dense sampling
                          in a 500ms window around each cut boundary.
                          Replaces a blind 1fps sample.

4. Gemini pass A          Cohort visual analysis, FRAMES-ONLY upload
                          (not full videos, to stay under token limits).
                          Frame budget: 1 keyframe per scene, capped at
                          20 frames per video, capped at 200 frames
                          total across the cohort. If the cohort exceeds
                          that, downsample proportionally per video.
                          Extract cross-video invariants: palette,
                          typography, motion grammar, overlays, safe
                          zones, pacing targets.

5. Gemini pass B          Per-video transcript + cadence + storytelling
                          beats (using the word timestamps Gemini gives).

6. Gemini pass C          Mascot detection: "Does this clip contain a
                          pixel-art mascot? Return frame timestamps and
                          bounding boxes where present."
                          If at least 1 video returns positive, activate
                          the Mascot Track (see below).

7. Audio metrics          ffmpeg loudnorm two-pass to LUFS_integrated,
                          LRA, true peak. No voice cloning, just target
                          numbers for recreation.

8. Frame verification     The main session reads keyframes with the
                          Read tool to ground-truth pass A and B
                          claims. Frame selection is deterministic:
                            - For each video: frame at 10%, 25%, 50%,
                              75%, 90% of duration (scene-snapped to
                              the nearest sampled frame).
                            - Plus every frame cited by pass A as
                              evidence for a palette hex or typography
                              claim.
                            - Plus 3 random mascot-containing frames
                              per mascot-bearing video.
                          Each correction is appended to corrections.md
                          as a YAML block:
                            - claim_id: <pass-A or pass-B section ref>
                              original: "..."
                              corrected: "..."
                              evidence_frame: frames/frame_0034.jpg
                          The synthesizer parses this YAML and applies
                          corrections before writing STYLE-GUIDE.md.

9. Synthesizer            A dispatched subagent receives:
                           - cohort-analysis (pass A)
                           - per-video analyses (pass B)
                           - frame corrections
                           - mascot detection results
                          Produces STYLE-GUIDE.md with the invariants,
                          flags one-off choices, and cites evidence
                          frames.

10. Mascot Track          Only runs if pass C found mascot frames.
                          See the dedicated section below.
```

### Mascot Track

Runs when Gemini pass C confirms mascot presence in at least one video. All steps operate only on mascot-containing frames.

```
M1. Dense extraction      4fps extraction across mascot-containing
                          ranges (not the whole video, just the spans
                          where pass C flagged the mascot).

M2. Bounding box pass     Gemini returns {frame_id, bbox, confidence}
                          per frame for the mascot character. Drop
                          frames with confidence < 0.6 (occlusion or
                          partial visibility). Keep the rest.

M3. Crop + isolate        Pillow crops to bbox + 10% padding.
                          Background removal strategy (try in order):
                            (a) Chroma-key PRIMARY, if the cohort
                                background is a known solid (sample 8
                                corner pixels across all kept frames,
                                check stddev < 5 in RGB). Threshold
                                within delta-E < 8 in LAB space against
                                the sampled bg color.
                            (b) rembg with the `isnet-anime` model,
                                trained on stylized art, which
                                preserves sharp edges far better than
                                u2net on pixel art.
                            (c) rembg with `u2net`, last resort.
                          Record which method was used per video in
                          mascot-profile.json.
                          Save each crop to per-video/<slug>/mascot-raw/.

M4. Native resolution     Two-method consensus:
    detection               Method 1, scanline run-length GCD:
                              For each row and column of isolated
                              mascot pixels, compute run-lengths of
                              constant-color spans (ignoring alpha=0).
                              Take the GCD of all runs across the
                              image; that GCD is the scale factor.
                              Native resolution = crop_size / scale.
                            Method 2, downsample-upsample error:
                              For candidate scale s in [1..16],
                              downsample the crop by s with a box
                              filter, upsample by s with
                              nearest-neighbor, compute MSE vs the
                              original. Pick s with minimum MSE.
                          If the methods agree within 1 scale step,
                          record native_resolution_px confidently. If
                          they disagree, prefer the method that found a
                          clear pixel grid and set
                          native_resolution_confidence accordingly.
                          Failure mode: if the source video was
                          re-encoded with bilinear scaling (most
                          platform re-encodes do this), edges are no
                          longer clean and both methods can miss. When
                          native_resolution_confidence is low, prompt
                          distillation (M12) falls back to a
                          qualitative description ("low-res pixel art,
                          approx 32 to 48px tall") rather than a
                          specific grid size.

M5. Palette quantization  Pipeline:
                            1. Pool non-alpha pixels from ALL isolated
                               mascot frames (across kept videos).
                            2. Pre-filter anti-aliased pixels: for each
                               pixel, check its 4-neighborhood. If all
                               neighbors are the same color OR alpha=0,
                               keep it; else drop it. This removes
                               blended AA pixels that would bloat k.
                            3. Convert RGB to LAB (perceptually
                               uniform; k-means in RGB over-weights
                               green).
                            4. k-means for k in {4, 6, 8, 12, 16}. Pick
                               the smallest k where LAB delta-E mean
                               reconstruction error < 3 (below the
                               just-noticeable-difference threshold).
                            5. Convert cluster centers back to RGB hex.
                          Output: palette.json (hex list, k value,
                          reconstruction delta-E), palette.gpl
                          (GIMP/Aseprite format), palette-swatch.png.

M6. Native fps detection  Algorithm:
                            1. Sample the mascot bbox region at source
                               video fps (typically 30 or 60).
                            2. For each consecutive frame pair (i, i+1),
                               compute per-pixel mean absolute diff in
                               the bbox. Call this delta_i.
                            3. Classify delta_i as "distinct" if
                               delta_i > threshold (5/255), else
                               "near-duplicate" (a held frame).
                            4. Find the modal run-length of
                               near-duplicates between distinct
                               transitions. That modal gap G is the
                               frame-hold count.
                            5. native_animation_fps = source_fps / G.
                          Failure mode: if the video was re-encoded
                          with motion interpolation, or if the mascot
                          has continuous sub-pixel motion, G collapses
                          to 1 and native fps equals source fps, which
                          is wrong for pixel art. When the inferred fps
                          is above 20, flag
                          native_animation_fps_confidence = "low" and
                          have prompt distillation describe it as
                          "held frame animation, approx 8 to 12fps
                          pixel cadence" qualitatively.

M7. Pose clustering       Gemini receives all isolated frames in a
                          single request and clusters them into labeled
                          poses (idle, talking, walking, reaction).
                          Returns a frame-to-pose_label mapping.

M8. Consistency check     Gemini cross-compares the mascot across
                          videos: single consistent design, or
                          variants? If variants, flag them in
                          MASCOT-VARIANTS.md rather than blending them
                          into one profile.

M9. Canonical frame       Gemini selects the best single reference
    selection             still per consistent design: front-facing,
                          neutral pose, centered, no motion blur, clean
                          edges. Saved as canonical-reference.png.

M10. Sprite sheet         Pillow grid: one column per pose, frames as
                          rows, transparent background.
                          Saved as sprite-sheet.png.

M11. Constraint pass      Gemini produces a STRUCTURED constraints
                          object, not free text, with slots:
                            render_taboos: [3D, vector-smooth, painterly,
                                            photoreal, airbrushed, ...]
                            aa_budget: "none" | "1px-edge-only" | "soft"
                            color_taboos: [gradients, dithering, ...]
                            proportion_taboos: [anime-eyes, chibi, ...]
                          M12 maps these into each generator's
                          negative-prompt syntax.

M12. Prompt distillation  Gemini writes two prompt documents from all
                          accumulated evidence.

                          STATIC-PROMPT.md
                            Sections:
                              - Character description
                              - Art style (with native_resolution_px
                                or the qualitative fallback if
                                confidence is low)
                              - Palette block (hex list from M5)
                              - Pose options (from M7 labels)
                              - Constraints (from M11, per generator)
                            Per-generator variants with length targets:
                              - Midjourney v7: 60 words max,
                                uses `--no <term1>, <term2>` for taboos
                              - Ideogram 2.0: 120 words max,
                                uses the negative prompt field
                              - FLUX.1 (dev/pro): 200 words max,
                                uses the negative prompt field
                              - Nano Banana (Gemini native image):
                                300 words max, constraints inline as
                                "must not be / avoid" phrases

                          ANIMATED-PROMPT.md
                            Sections:
                              - Reference image: canonical-reference.png
                                (path noted; the user uploads it to the
                                generator)
                              - Animation style (with
                                native_animation_fps or the qualitative
                                fallback)
                              - Motion descriptors per pose transition
                              - Loop length guidance
                              - Easing and hold notes
                              - Constraints (from M11, per generator)
                            Per-generator variants with length targets:
                              - Runway Gen-4 I2V: 500 chars max, no
                                native negative prompt, so fold taboos
                                into the positive prompt as "avoid ..."
                              - Kling 2.0: 500 chars max, separate
                                negative prompt field
                              - Pika 2.2: 400 chars max, uses the
                                `-neg` flag
                              - Veo 3: 1000 chars max, negative via
                                natural language
                              - Sora 2: 1000 chars max, negative via
                                natural language
```

## Output structure

```
<working-dir>/
├── STYLE-GUIDE.md                  <- cohort invariants (primary deliverable)
├── MASCOT-KIT/                     <- only if a mascot was detected
│   ├── STATIC-PROMPT.md            <- goal A (static)
│   ├── ANIMATED-PROMPT.md          <- goal A (animated)
│   ├── canonical-reference.png     <- goal B, THE reference image
│   ├── sprite-sheet.png            <- goal B
│   ├── poses/
│   │   ├── idle-01.png ... idle-N.png
│   │   ├── talking-01.png ...
│   │   └── reaction-01.png ...
│   ├── palette.json
│   ├── palette.gpl
│   ├── palette-swatch.png
│   ├── mascot-profile.json         <- native_resolution_px, native_animation_fps, k
│   ├── MASCOT-EVIDENCE.md          <- every claim cites source frames
│   └── MASCOT-VARIANTS.md          <- only if the consistency check found variants
├── per-video/
│   └── <video-slug>/
│       ├── scenes.json
│       ├── gemini-visual.md
│       ├── gemini-transcript.md
│       ├── frames/                 <- scene-aware sampling
│       ├── mascot-raw/             <- isolated crops before curation
│       ├── audio-metrics.json
│       └── corrections.md          <- frame verification deltas
├── cohort-analysis.md              <- synthesizer raw input
├── STYLE-GUIDE-DETAILED.md         <- optional single-video deep dive
└── run-log.md                      <- what ran, what was skipped, cost tally
```

### Schemas

**`mascot-profile.json`** (canonical; required fields noted):

```json
{
  "variant_id": "primary",
  "source_videos": ["<slug>", "..."],
  "frame_count_used": 124,
  "bg_removal_method": "chroma-key | isnet-anime | u2net",
  "native_resolution_px": { "w": 32, "h": 32 },
  "native_resolution_confidence": "high | low",
  "native_resolution_methods_agreed": true,
  "native_animation_fps": 10,
  "native_animation_fps_confidence": "high | low",
  "palette": {
    "k": 8,
    "hex": ["#...", "..."],
    "reconstruction_delta_e_mean": 2.1,
    "space": "LAB"
  },
  "poses": [
    { "label": "idle", "frames": ["poses/idle-01.png", "..."] },
    { "label": "talking", "frames": ["..."] }
  ],
  "canonical_reference": "canonical-reference.png",
  "constraints": {
    "render_taboos": ["3D", "vector-smooth", "painterly"],
    "aa_budget": "1px-edge-only",
    "color_taboos": ["gradients"],
    "proportion_taboos": ["anime-eyes", "chibi"]
  },
  "evidence_refs": ["MASCOT-EVIDENCE.md#palette", "..."]
}
```

**`run-log.md`** (required contents, not optional):

- Run timestamp, input videos, working directory
- Per-step status: ran | skipped (reason) | failed (error)
- Per-step token usage and dollar cost (Gemini pass A/B/C/M2/M7/M8/M9/M11/M12)
- Mascot track activation status and detection counts per video
- Total cost tally in USD
- Warnings: low-confidence native_resolution or native_fps, rembg fallback triggered, variants detected

## Key design decisions

1. **Cohort-first, per-video second.** The primary deliverable is `STYLE-GUIDE.md` (invariants across the set), not per-video style guides. Per-video analyses remain as supporting evidence.

2. **Gemini as workhorse, local tools only where Gemini cannot deliver.** PySceneDetect for cut timestamps (Gemini timestamps are approximate), rembg for background removal (Gemini cannot), ffmpeg for LUFS (not a vision task), scikit-learn for palette quantization (deterministic task). Everything else, meaning OCR, motion description, pose labeling, consistency checks, and prompt distillation, is Gemini.

3. **Pixel-art extraction is first-class, not an afterthought.** Native resolution, palette quantization, and native fps are required steps, not optional. Without them the prompts are too generic to reliably drive a generator toward a pixel-art result instead of a "pixel-art-ish" smooth render.

4. **Evidence-cited prompts.** Every line in STATIC-PROMPT.md and ANIMATED-PROMPT.md is traceable to a specific frame or measurement in `MASCOT-EVIDENCE.md`. That makes the skill debuggable when a generated asset comes out wrong.

5. **Variants are flagged, not blended.** If the mascot design drifted across clips, the consistency check (M8) splits them rather than averaging. Averaging visual design across variants produces unusable profiles.

6. **Frame verification stays in the main thread.** The synthesizer runs as a subagent, but the keyframe ground-truth check runs in the main session, because a model looking at the actual pixels is the authoritative correction layer for Gemini's color and font errors.

## Acceptance criteria for a good run

- `STYLE-GUIDE.md` produced with palette, typography, motion grammar, pacing fingerprint, and cohort-level invariants (not per-video averages).
- `MASCOT-KIT/canonical-reference.png` exists and is a clean front-facing still with a transparent background.
- `palette.json` contains 4 to 16 hex values (not hundreds, which would mean quantization failed) and reports `reconstruction_delta_e_mean < 3`.
- `mascot-profile.json` matches the schema above, with required fields present and either a resolved value or an explicit confidence="low" flag.
- `STATIC-PROMPT.md` contains all four per-generator variants within their length limits (Midjourney 60 words, Ideogram 120, FLUX 200, Nano Banana 300).
- `ANIMATED-PROMPT.md` contains all five per-generator variants within their character limits (Runway and Kling 500, Pika 400, Veo and Sora 1000).
- `run-log.md` exists with per-step status, cost tally, and a warnings block.
- Human spot-check: paste each generator's prompt block into its target tool and confirm the generated mascot resembles the reference within qualitative tolerance.

## Risks and known failure modes

- **Mascot detection false negatives.** If Gemini pass C misses the mascot, the Mascot Track will not fire. Mitigation: the `--force-mascot` flag accepts a user-supplied hint image as a seed for M2's bbox pass.
- **Background removal quality on pixel art.** Addressed in M3 via the three-method cascade (chroma-key, isnet-anime, u2net). Residual risk: if none produces clean alpha, `canonical-reference.png` will have halo artifacts. Mitigation: M9 scores candidates on edge cleanliness and can reject frames entirely, falling back to a manually selectable candidate list in `MASCOT-EVIDENCE.md`.
- **Native resolution and native fps on re-encoded source.** Both pipelines have documented failure modes when the source was bilinear-scaled or motion-interpolated, which platform re-encodes commonly do. Explicit handling in M4 and M6: the low-confidence flag triggers a qualitative fallback in M12 and never silently produces wrong numbers.
- **Palette k over- or under-selection.** The elbow search via LAB delta-E is robust but not perfect on cohorts that mix UI screencasts (many colors) with mascot-only scenes (few colors). Mitigation: M5 pools only isolated-mascot pixels after M3, not full frames, which keeps the quantization focused. Human review of `palette-swatch.png` remains the safety net.
- **Cohort size sensitivity.** Fewer than 3 videos weakens cross-video invariants. The synthesizer must handle a single mascot clip gracefully: single-source profile, no cross-check, variants block marked N/A.
- **Gemini schema drift.** Gemini occasionally returns malformed JSON for structured prompts (M2 bbox, M7 pose mapping, M11 constraints). Mitigation: every structured Gemini pass uses `response_schema` plus one retry on parse failure before surfacing the error.
