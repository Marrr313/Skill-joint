# ai-voice-humanizer

A [Claude Code](https://claude.com/claude-code) skill that makes AI-generated voiceovers sound like real human speech, from script formatting through generation, editing, and final audio processing.

It covers the four things that separate a convincing AI voiceover from an obviously synthetic one: tone variation, strategic pauses, word emphasis, and human-written scripts. The skill turns those into concrete steps, ElevenLabs slider settings, punctuation and capitalization markup that the voice engine reads as performance cues, a small-batch generation technique that avoids the uncanny "same voice all the way through" pattern, a post-production editing pipeline, and a set of FFmpeg processing chains you can apply without opening a DAW.

## What's inside

- `SKILL.md`: the skill definition, voice setup, script markup quick reference, and the small-batch generation workflow.
- `scripts/voice_preset.py`: a zero-dependency Python CLI that applies 14 voice processing presets as FFmpeg filter chains. Seven production presets (voice enhancer, movie trailer, deeper voice, echo, muffled, noise remover, phone call) and seven creative ones (90s, alien, chipmunk, inner monologue, pilot, robot, villain). Stdlib only; needs Python 3.9+ and FFmpeg. Processing chain adapted from Isaac's (ISAACVERSE) Premiere presets.
- `references/script-formatting.md`: the full markup guide with before/after examples for emphasis, excitement, hesitation, and pacing.
- `references/editing-workflow.md`: post-production in any NLE, covering how to choose takes, splice the best parts of multiple generations into a single line, tighten pacing, and run the EQ pass.
- `references/dubbing-workflow.md`: dubbing a video into other languages and publishing the alternate audio tracks.
- `references/premiere-pro-presets-raw.md`: the measured parameter values behind every preset (frequencies, gains, ratios, transfer curves) so the same processing can be rebuilt in any tool. Values adapted from Isaac's (ISAACVERSE) Premiere presets.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install it with the `skills` CLI:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy this folder into your Claude Code skills directory:

```bash
cp -R ai-voice-humanizer ~/.claude/skills/ai-voice-humanizer
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

## Use

Ask Claude to "make this AI voiceover sound human", "format this script for ElevenLabs", "clean up my AI voice audio", or "dub this video into Spanish". The skill also triggers on mentions of AI voice, voiceover, TTS, text to speech, voice cloning, and dubbing.

You can run the preset processor directly:

```bash
# Apply the main production preset
python3 scripts/voice_preset.py input.wav voice-enhancer

# See every available preset
python3 scripts/voice_preset.py --list

# Print the FFmpeg command without running it
python3 scripts/voice_preset.py input.wav movie-trailer --dry-run
```

If you use the ElevenLabs API directly, supply your credentials through standard environment variables such as `ELEVENLABS_API_KEY`, and pass your own voice identifier where a voice is required (for example `<your-voice-id>`).

## Credits

Processing chain adapted from Isaac's (ISAACVERSE) Premiere presets. The FFmpeg filter chains in `scripts/voice_preset.py` and the parameter tables in `references/premiere-pro-presets-raw.md` are derived from that preset pack.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
