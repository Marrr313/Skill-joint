# remotion-video-builder

A [Claude Code](https://claude.com/claude-code) skill that turns a written style guide into a finished [Remotion](https://www.remotion.dev) composition: script, voiceover, word-level caption sync, B-roll, components, and a rendered video.

You bring a STYLE-GUIDE.md describing the look you want (canvas, colors, fonts, text animation, cut rhythm, audio) and a topic. The skill writes the script against a beat template, generates the voiceover, transcribes it for word-level timestamps, sources the B-roll, builds the React components, and wires up the composition. The rule that holds it together is that every frame number is derived from `audioTimestamp * fps`, never hard-coded, so re-recording the voiceover re-syncs the whole video instead of breaking it.

It reads your existing project structure and follows its conventions rather than imposing a folder layout, so it works on a fresh `create-video` scaffold or an established Remotion repo.

## What's inside

- `SKILL.md`: the eight-step workflow, from parsing the style guide through script, voiceover, transcription, asset collection, component build, scene sequencing, and the preview-and-render loop. Includes the graded scene-by-scene recreation loop for matching a reference video, plus a troubleshooting table for the usual failures (captions out of sync, fonts not rendering, white flash between scenes).
- `references/component-patterns.md`: eight self-contained TypeScript patterns ready to copy and adapt. FloatingCard with optional Ken Burns, KaraokeCaption for word-by-word reveal, a phrase-pill caption variant, HardCutSequencer, MusicBed with fades, HookScene, SplitLayout, SlowZoom, and the composition assembly pattern that stacks them in the right layer order.
- `references/storytelling-templates.md`: five beat formulas with timing distributions and fill-in-the-blank scripts. Brand Documentary, Proof Drop, Contrarian Filter, Trend Jack, and Listicle, each with its own TTS writing rules, plus a universal set of rules for writing copy a speech model reads well.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install everything at once:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R remotion-video-builder ~/.claude/skills/remotion-video-builder
```

Claude Code auto-discovers skills by their `SKILL.md` front matter, so it works from a plugin's `skills/` directory too.

### Keys

Set only the keys the run actually needs, as environment variables:

```bash
export ELEVENLABS_API_KEY="..."   # voiceover generation
export GEMINI_API_KEY="..."       # word-level transcription
export PEXELS_API_KEY="..."       # automated B-roll fetching
```

Each one is optional. Bring your own voiceover and captions, or supply assets by hand, and a run can need no keys at all. whisper.cpp works as a local, offline substitute for the transcription step.

## Use

Ask Claude to "build a video in this style", "make a video like this reference", "create a new reel", or "produce a Remotion video", and point it at your style guide.

The skill stops for approval at the two checkpoints that matter: after it summarizes the parsed style guide, and after it drafts the script. The script is the contract, since it determines the timing, the assets, and the final duration, so it is worth getting right before any audio is generated.

If you are recreating a specific reference video rather than working from a written spec, say so. The skill switches to a graded loop that rebuilds one scene at a time, renders stills at timestamps matching the source, compares them side by side against the real frames, and iterates until the match scores 9 out of 10 before advancing. Whole-video passes do not converge.

## License

MIT, see [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
