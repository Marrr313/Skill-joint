# Mascot Track Gemini Prompts

All prompts use `gemini-2.5-pro`. Where structured output is required, pass a `response_schema` matching the JSON sketch; retry ONCE on parse failure before surfacing the error to the user.

## Pass C: Mascot Detection (per video)

Input: full video via Files API.

> Does this video contain a pixel-art mascot character? If yes, return a JSON list of frame timestamps (in milliseconds) where the mascot is clearly visible, along with confidence [0, 1]. If no mascot, return an empty list.

Response schema: `{"mascot_present": bool, "frames": [{"ts_ms": int, "confidence": float}]}`

## M2: Bounding Boxes

Input: the dense-sampled frames from M1 (isolated to mascot-containing ranges), uploaded as images.

> For each frame, return the bounding box of the pixel-art mascot character in pixel coordinates (x, y, w, h) with a confidence score [0, 1]. If the mascot is occluded, partial, or absent in a frame, return confidence < 0.6.

Response schema: `{"frames": [{"frame_id": str, "bbox": {"x": int, "y": int, "w": int, "h": int}, "confidence": float}]}`

## M7: Pose Clustering

Input: isolated mascot crops (post-M3 background removal).

> Cluster these frames into distinct animation POSES. Typical labels include idle, talking, walking, reaction, pointing, and sleeping, but use whatever is appropriate. Return a mapping of frame filename to pose label. Aim for 3 to 8 pose clusters.

Response schema: `{"poses": [{"label": str, "frames": [str]}]}`

## M8: Consistency Check

Input: one representative isolated crop per video.

> Are these mascot renditions the SAME character design, or are there visual variants? Consider: proportions, palette, art style, pixel grid, head/body ratio. If all consistent, return `{"consistent": true, "variants": []}`. If variants exist, group videos by variant.

Response schema: `{"consistent": bool, "variants": [{"id": str, "video_slugs": [str], "description": str}]}`

## M9: Canonical Reference Selection

Input: all isolated crops from the dominant variant's videos.

> From these frames, pick the SINGLE BEST canonical reference still for driving an image-to-video generator. Criteria in priority order:
> 1. Front-facing, neutral pose
> 2. Full body visible, centered, no crop
> 3. No motion blur, crisp edges
> 4. Representative palette coverage
> 5. Minimal background halo from segmentation
>
> Return the filename plus a 1-sentence rationale.

Response schema: `{"filename": str, "rationale": str}`

## M11: Constraint Extraction

Input: 5 to 10 isolated crops plus the palette hex list.

> List what this mascot is NOT, to feed downstream negative prompts. Fill these slots with an array of terms each:
> - `render_taboos`: 3D-rendered, vector-smooth, painterly, photorealistic, airbrushed, etc.
> - `aa_budget`: one of "none" | "1px-edge-only" | "soft"
> - `color_taboos`: gradients, dithering, noise, etc.
> - `proportion_taboos`: anime-eyes, chibi, mecha, etc.
>
> Only include taboos that are visually DEFENSIBLE from the frames provided. Do not invent taboos.

Response schema: `{"render_taboos": [str], "aa_budget": str, "color_taboos": [str], "proportion_taboos": [str]}`

## M12: Prompt Distillation (Static + Animated)

Input: all accumulated mascot evidence, meaning palette, native_resolution_px (or qualitative fallback), poses, canonical reference, and constraints.

### Static prompt: M12a

> Write a STATIC-PROMPT.md covering all four generators. Use the provided evidence. Each generator variant must stay under its length limit. Constraints must use each generator's correct negative-syntax per `per-generator-syntax.md`.
>
> Generators and limits:
> - Midjourney v7: 60 words max, `--no <term1>, <term2>` for taboos
> - Ideogram 2.0: 120 words max, negative prompt field
> - FLUX.1: 200 words max, negative prompt field
> - Nano Banana (Gemini): 300 words max, inline "must not be / avoid" phrases
>
> Sections within each variant, in order: character description, art style (with native_resolution), palette block, pose options, constraints.

### Animated prompt: M12b

> Write an ANIMATED-PROMPT.md covering all five generators. Each variant stays under its character limit. Reference image is `canonical-reference.png`.
>
> Generators and limits:
> - Runway Gen-4 I2V: 500 chars max, fold taboos into the positive prompt as "avoid ..."
> - Kling 2.0: 500 chars max, separate negative prompt field
> - Pika 2.2: 400 chars max, uses the `-neg` flag
> - Veo 3: 1000 chars max, natural language negative
> - Sora 2: 1000 chars max, natural language negative
>
> Sections within each variant, in order: animation style (with native_animation_fps), motion descriptors per pose transition, loop length guidance, easing and hold notes, constraints.
