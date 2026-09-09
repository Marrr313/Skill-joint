# Editing AI Voiceover in Post-Production

This workflow applies to any NLE with a timeline (Premiere Pro, DaVinci Resolve, Final Cut, CapCut, etc.).

## Step 1: Organize Files

Put all generated clips in a single folder. Select all and batch rename for organization (e.g., `vo-001.mp3`, `vo-002.mp3`). Group multiple takes of the same sentence together.

## Step 2: Import and Lay Out

Import all voiceover clips into your timeline. Lay them out in script order on the first audio track. Don't worry about timing yet -- just get the order right.

## Step 3: Choose Best Takes

For each section where you have multiple generations:
- Listen to all versions back-to-back
- Choose the one that fits the emotional context of that moment
- Keep the alternates on a muted track -- you may need parts of them

## Step 4: The Frankenstein Technique

This is where the magic happens. For a single sentence with 3 generated versions:

1. Listen to each version and identify which parts sound best
2. Cut the best-sounding segments from different versions
3. Splice them together on the main track

Example: For "But the real magic happens when you chop some parts from each generation and combine them together" --
- Take "But the real magic" from version 1 (best tone)
- Take "happens when you chop some parts" from version 3 (best pacing)
- Take "from each generation and combine them together" from version 2 (best energy)

The slight tonal differences between generations mimic how real humans naturally vary their delivery mid-sentence.

## Step 5: Tighten Pacing

Once you have a single continuous voiceover line:

1. Cut dead air / silence between sentences
2. Use a second audio track to start the next sentence right after the previous one ends
3. **Keep intentional pauses** at important moments (don't cut everything -- pauses = impact)
4. Match pacing to your visuals

## Step 6: Speed Adjustment

If the voiceover is too slow or too fast:
- Don't use your NLE's built-in speed changer -- it distorts pitch even with "maintain pitch" enabled
- Re-generate the problematic sections with adjusted speed slider in ElevenLabs instead
- Or adjust the ElevenLabs speed slider for future batches

## Step 7: EQ and Processing

Apply a voice processing chain to make it sound professional:

1. **Parametric EQ** with high-pass filter (removes low rumble)
2. Increase the Q value to find resonant/echo-y frequencies
3. Drag those frequencies down to clean up the sound
4. Optionally apply a voice preset or chain (compression, de-essing, etc.)

This step transforms "decent AI audio" into "broadcast-quality voiceover."

## Common Mistakes

- Cutting ALL pauses (sounds like a lifeless robot controlled by algorithms)
- Using the same generation for the entire video (creates the uncanny AI pattern)
- Using NLE speed changers instead of re-generating at correct speed
- Not EQ-processing the output (raw AI audio sounds thin and echo-y)
