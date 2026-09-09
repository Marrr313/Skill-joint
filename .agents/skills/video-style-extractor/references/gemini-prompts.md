# Gemini Prompts for Video Style Extraction

## 1. Visual Analysis Prompt

Use this prompt with `gemini-2.5-pro` after uploading video file(s). When multiple videos are uploaded, Gemini will cross-compare them automatically.

```
You are a video editing analyst specializing in reverse-engineering production styles for programmatic recreation. Analyze the uploaded video(s) with extreme precision. I need exact, measurable values, not subjective descriptions.

## Canvas & Dimensions

- Aspect ratio (e.g., 9:16, 16:9, 1:1)
- Resolution if determinable
- Safe zone margins (how close do elements get to edges?)

## Color Palette

For EVERY distinct color used, provide:
- Hex code
- Where it appears (background, text, accent, overlay, border)
- Opacity if not 100%

Specifically identify:
- Primary background color(s): solid or gradient? If gradient, list stops and direction
- Text colors (headline, body, accent text)
- Overlay/filter colors applied to footage
- Any color transitions or shifts during the video

## Typography

For EVERY text element that appears:
- Font identification (name the exact font or closest match: e.g., "Anton", "Montserrat Bold", "Impact")
- Weight (100-900 scale)
- Size relative to canvas height (percentage or estimated px at 1080p)
- Case: uppercase, lowercase, mixed, sentence case
- Letter spacing: tight, normal, wide (estimate in px or em)
- Line height
- Color (hex)
- Stroke/outline: color, width
- Shadow: color, offset, blur
- Position on canvas (top third, center, lower third; be specific with estimated percentages from top/left)
- Text alignment (left, center, right)

## Text Animation & Motion

For EVERY text appearance:
- Entry animation (fade, slide from direction, scale up/down, typewriter, bounce, none)
- Entry duration (ms)
- Hold duration (ms): how long text stays fully visible
- Exit animation
- Exit duration (ms)
- Easing curve (linear, ease-in, ease-out, ease-in-out, spring/bounce)
- Any per-word or per-character staggering? If so, delay between units

## Caption/Subtitle Style (if present)

- Position (center, lower third, etc.)
- Words per highlight group
- Highlight style (color change, background box, underline, scale, bold)
- Highlight color (hex)
- Non-highlighted text color (hex)
- Background box: color, opacity, padding, border-radius
- Animation: how do captions transition between phrases?

## B-Roll & Asset Presentation

- How is B-roll footage framed? (full bleed, inset with border, picture-in-picture, split screen)
- Border/frame styling if present (color, width, radius, shadow)
- Scaling/crop behavior (ken burns, zoom in/out, static)
- Overlay effects on B-roll (color grade, vignette, blur)
- Screen recording presentation (device frame? drop shadow? rounded corners?)
- Image/screenshot treatment (scale, position, animation)

## Editing & Cut Pattern

Map out the COMPLETE edit timeline:
- Total duration
- Number of distinct cuts/segments
- For each cut: timestamp, duration, what type of content (talking head, B-roll, text card, screen recording, etc.)
- Average cut length
- Shortest and longest cuts
- Cut rhythm pattern (regular intervals? accelerating? random?)
- Transition types between cuts (hard cut, crossfade, zoom, whip pan, match cut)
- Transition durations (ms)

## Motion & Camera

- Any zoom effects? (speed, direction, easing)
- Pan/tilt movements
- Shake/handheld simulation
- Parallax or depth effects
- Background motion (animated particles, gradients, patterns)

## Audio Production (what you can observe)

- Music: genre, energy level, BPM estimate
- Music volume relative to voice (percentage or dB estimate)
- Sound effects: what types, when do they occur, how prominent
- Audio ducking behavior (does music drop during speech?)
- Any silence/pause used as a device?

## Storytelling Structure

- How does the video open? (hook type: question, statement, visual shock, pattern interrupt)
- Number of distinct "acts" or segments
- Where is the climax/peak moment?
- How does it close? (CTA, punchline, cliffhanger, loop back to start)
- Pacing: does the energy build, stay flat, or oscillate?

## Multi-Video Comparison (if multiple videos uploaded)

- What elements are CONSISTENT across all videos? (these define the "style")
- What elements VARY between videos? (these are content-dependent, not style)
- Which visual/editing choices appear to be intentional brand elements vs. one-off creative decisions?
- Rate consistency (1-10) for: colors, typography, cut rhythm, motion style, audio approach

Respond in structured markdown with clear headers. Use exact values everywhere, no "approximately" or "around." If you're uncertain about a specific value, state your best estimate and flag it with [ESTIMATED].
```

## 2. Transcription & Cadence Prompt

Use this prompt with `gemini-2.5-pro` using the same uploaded video file(s). The video files contain the audio track.

```
You are a speech and voice analyst. Analyze the audio from the uploaded video(s) with precision. I need both the exact transcript and a detailed analysis of HOW the words are delivered.

## Full Transcript

Provide the complete transcript with:
- Word-level timestamps: [HH:MM:SS.ms] word
- Speaker identification if multiple speakers
- Mark any non-speech audio events: [MUSIC], [SFX: description], [SILENCE: duration], [BREATH]
- Mark emphasis: **word** for stressed words
- Mark pace changes: {FAST} or {SLOW} before sections where pace shifts

## Voice Characteristics

- Gender and estimated age range of speaker
- Vocal register (chest voice, head voice, mixed)
- Tone: authoritative, conversational, excited, calm, urgent, conspiratorial, teaching
- Energy level pattern across the video (1-10 scale at key moments)
- Any vocal fry, upspeak, or distinctive speech patterns

## Cadence Analysis

- Overall words per minute (WPM)
- WPM by segment (break the video into logical sections and measure each)
- Pause patterns:
  - Average pause between sentences (ms)
  - Longest pause and what it preceded (dramatic effect?)
  - Shortest pauses (rapid-fire sections)
- Rhythm pattern: steady, accelerating, decelerating, oscillating, staccato
- Beat alignment: do cuts or visual changes sync with speech rhythms?

## Vernacular Analysis

- Average sentence length (word count)
- Sentence structure patterns (simple, compound, complex): give the ratio
- Pronoun usage: count of "you," "I," "we," "they," then calculate the you:I ratio
- Specificity markers: count instances of specific numbers, names, tools, vs. vague generalizations
- Transition words/phrases used (list them all with frequency)
- Filler words or verbal tics (um, uh, like, right, you know), with frequency
- Register: formal vocabulary vs. casual/slang, with examples of each
- Rhetorical devices: questions asked, lists used, repetition, contrast/antithesis
- Power words: words chosen for emotional impact (list them)

## Delivery-to-Edit Sync

- Map moments where voice emphasis aligns with visual cuts or text appearances
- Identify any "hit points," meaning moments where audio and visual change simultaneously
- Note any deliberate mismatch between audio energy and visual pacing

## TTS Recreation Notes (if voiceover appears AI-generated)

- Estimated TTS engine (ElevenLabs, Play.ht, etc.)
- Voice characteristics that suggest AI vs. human
- Formatting patterns that would affect TTS output:
  - Use of periods vs. commas for pause control
  - Sentence length patterns for natural breathing
  - Any SSML-like markers or emphasis patterns
  - Recommended ElevenLabs settings (stability, similarity, style)

Respond in structured markdown. Timestamps must be precise to the nearest 100ms at minimum.
```

## Pass A: Cohort Visual Invariants

**When to use:** Frames-only cohort analysis. Invoke with all sampled keyframes across ALL videos in one request (200 frames total maximum). Do NOT upload full videos here.

**Prompt:**

> You are analyzing a cohort of short-form marketing videos produced by a single brand. I am providing one keyframe per scene from each video, labeled with `<video_slug>/<frame_file>`. Your job is to identify the INVARIANTS across this cohort, meaning the style choices that recur, and to flag one-off choices separately.
>
> Return structured markdown with these sections:
>
> 1. **Palette**: the repeating background and accent colors as hex codes. For each, cite at least 2 evidence frames. Flag any color that appears in only one video.
> 2. **Typography**: font families (guess by visual match), weights, letter-spacing notes, sentence-case vs ALL CAPS. Cite evidence frames.
> 3. **Motion grammar**: the cohort's default transitions (cut, whip pan, zoom, dissolve), typical shot length range, pacing pattern (front-loaded / steady / crescendo).
> 4. **Overlays and UI chrome**: lower thirds, captions, logo placement, safe-zone conventions. Cite evidence frames.
> 5. **Mascot presence**: for each video slug, does a pixel-art mascot appear? List the frames where visible.
> 6. **One-off choices**: anything that appears in only ONE video and is NOT an invariant. List as "<video_slug>: <observation>".
>
> Be precise. If you cannot determine a value, say so. Do not invent hex codes.
