# video-style-extractor

A [Claude Code](https://claude.com/claude-code) skill that reverse-engineers the complete editing style of a video, or of a whole cohort of videos, into a written `STYLE-GUIDE.md` you can hand to a builder.

Point it at a folder of clips or a list of URLs. It segments each video into scenes, samples keyframes around every cut, measures loudness, and runs Gemini over the frames to pull out palette, typography, motion grammar, overlays, pacing, transcript, and cadence. Claude then reads the actual keyframes to correct the color and font values Gemini gets wrong, and a synthesizer pass turns everything into a guide where each hex code, font, and timing value cites the frame it came from.

When the videos feature a pixel-art mascot, a second track fires automatically. It isolates the character frame by frame, detects its native pixel resolution and animation fps, quantizes its palette in LAB space, clusters its poses, picks a canonical reference still, and distills the result into ready-to-paste prompts for four image generators and five image-to-video generators.

## What's inside

- `SKILL.md`: the 12-step workflow, from ingest to run log.
- `scripts/scene_detect.py`: PySceneDetect wrapper that emits cut timestamps as `scenes.json`.
- `scripts/scene_aware_sample.py`: keyframe per scene plus dense sampling around each cut boundary.
- `scripts/audio_metrics.py`: ffmpeg two-pass loudnorm for integrated LUFS, loudness range, and true peak.
- `scripts/bg_remove.py`: three-stage background removal cascade (chroma-key, then `isnet-anime`, then `u2net`), recording which method won.
- `scripts/native_resolution.py`: dual-method pixel-grid detection (run-length GCD plus downsample/upsample MSE) with a confidence flag.
- `scripts/native_fps_detect.py`: recovers the real animation cadence by finding the modal frame-hold count.
- `scripts/palette_quantize.py`: LAB k-means with an anti-aliasing pre-filter, picking the smallest k that stays under a delta-E of 3.
- `scripts/sprite_sheet.py`: assembles labeled pose frames into a transparent sprite sheet.
- `scripts/run_log.py`: appends step status, token cost, and warnings to a readable run log.
- `references/gemini-prompts.md`: the visual, transcription, and cohort-invariant analysis prompts.
- `references/mascot-prompts.md`: the mascot detection, bounding box, pose, consistency, and prompt-distillation prompts.
- `references/per-generator-syntax.md`: negative-prompt syntax and length limits per generator.
- `references/cohort-style-guide-template.md` and `references/detailed-guide-template.md`: the two output shapes.
- `references/pipeline-design.md`: algorithms, output schemas, and the documented failure modes of each detector.
- `tests/`: pytest coverage for the deterministic helpers, with small generated fixtures.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install the whole collection:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R video-style-extractor ~/.claude/skills/video-style-extractor
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

### Setup

Set a Gemini API key in your environment, and add the line to your shell profile so it persists:

```bash
export GEMINI_API_KEY="..."
```

Then install the tooling:

```bash
brew install ffmpeg yt-dlp                              # or your platform's equivalent
pip install -r video-style-extractor/scripts/requirements.txt
```

`yt-dlp` covers YouTube and most public hosts. For Instagram or TikTok sources, download the files with whatever you already use and point the skill at the folder instead.

## Use

Ask Claude to "extract the style from these videos", "reverse-engineer this video style", or "pull the mascot design from this cohort", and hand it a folder or a list of URLs. The mascot track activates on its own when a pixel-art character is detected; force it with `--force-mascot <hint-image>` if detection misses.

You can also run any helper directly:

```bash
python -m scripts.scene_detect clip.mp4 scenes.json
python -m scripts.scene_aware_sample clip.mp4 scenes.json frames/
python -m scripts.palette_quantize mascot-raw/iso_*.png palette.json
python -m scripts.native_resolution mascot-raw/iso_0001.png native-res.json
```

Run the tests with `pytest` from the skill directory.

**Pairs with [remotion-video-builder](../remotion-video-builder/)**, which takes the `STYLE-GUIDE.md` this skill produces and builds a renderable Remotion composition with new content in that style.

## License

MIT. See [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
