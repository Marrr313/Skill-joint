# mascot-processor

A [Claude Code](https://claude.com/claude-code) skill that turns animated character MP4s into transparent-background assets (GIF, APNG, and WebM), at both 160px and original resolution.

It detects whether the source is shot on a green screen or on a white background, then applies the matching removal method. Green screen mode kills every green pixel and dilates 2px to eat compression fringe. White background mode isolates the character by saturation and value, then audits every single frame for surviving gray halo pixels before anything is written. The recipe is plain ffmpeg, NumPy, SciPy, and Pillow, with no AI matting model involved, because photo-trained background removers leave shading and halos on flat 2D art.

## What's inside

- `SKILL.md` contains the whole recipe: background auto-detection, the two default removal functions, the mandatory per-frame audit, the ffmpeg and Pillow output commands for all five variants, and four fallback methods for when the defaults misbehave (edge flood-fill, exact hex match, white flood-fill, Gaussian alpha anti-aliasing).

No character art ships with this skill. It is a recipe, and you bring your own footage.

## Install

This skill ships inside the [NulightJens/jensai-skills](https://github.com/NulightJens/jensai-skills) monorepo. Install everything with:

```bash
npx skills@latest add NulightJens/jensai-skills
```

Or copy just this folder into your Claude Code skills directory:

```bash
cp -R mascot-processor ~/.claude/skills/mascot-processor
```

You will also need the Python dependencies and ffmpeg on your PATH:

```bash
pip install numpy scipy pillow
brew install ffmpeg   # or: apt install ffmpeg
```

## Use

Hand Claude one or more MP4s and ask it to "remove the background from these mascot animations", "make transparent GIFs from this footage", or "build a mascot asset pack". The skill picks the removal mode from the footage itself, so you do not need to say whether it is green screen or white.

Point it at an output directory if you want one; otherwise it writes to `./mascot-pack/` with `source/`, `gif/`, `apng/`, `webm/`, `gif-hd/`, and `apng-hd/` subfolders. Name each clip after the action it shows (`walking.gif`, `waving.gif`) so the pack stays browsable.

If a white-background clip comes out with a faint halo, the skill's audit should have caught it. If a green-screen clip loses a green prop, switch to the flood-fill or exact-hex fallback documented in `SKILL.md`.

## License

MIT. See [LICENSE](LICENSE).

Built by [Jens Heitmann](https://www.instagram.com/jens.heitmann), part of the JensAI skills collection.
