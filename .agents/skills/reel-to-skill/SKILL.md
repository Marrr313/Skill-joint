---
name: reel-to-skill
description: triggers when the user pastes an instagram.com/reel or instagram.com/p link and asks to turn it into a skill, agent, or lesson. Also triggers on "reel this", "skill this reel", "learn this reel".
allowed-tools: Bash, Read, AskUserQuestion
---

# Reel to Skill

Turn an Instagram reel (or photo post) into a Claude skill, agent, or lesson by
transcribing it and handing the content to `skill-creator`.

## 1. Fetch metadata (no download yet)

Run:

```bash
uvx yt-dlp --skip-download --dump-json "<REEL_URL>"
```

From the JSON, keep: `description` (this is the caption), `uploader`, `channel`,
`like_count`, `comment_count`. Save them to a working folder at
`~/reel-to-skill-runs/<shortcode>/` (the shortcode is the id in the reel URL).

## 2. Download the video

Run:

```bash
uvx yt-dlp -f "best[ext=mp4]/best" -o "<workdir>/reel.%(ext)s" "<REEL_URL>"
```

## 3. Transcribe locally

On Apple Silicon:

```bash
uvx --from mlx-whisper mlx_whisper "<workdir>/reel.mp4" \
  --model mlx-community/whisper-large-v3-turbo \
  --output-format txt --output-dir "<workdir>"
```

On other machines:

```bash
uvx --from openai-whisper whisper "<workdir>/reel.mp4" \
  --model turbo --output_format txt --output_dir "<workdir>"
```

## 4. Sanity-check the transcript

If the transcript is empty, or one short phrase repeats for most of the file,
the reel is music-only. Say so, and continue with caption text only instead
of failing.

## 5. Build the new skill

Invoke the `skill-creator` skill. Give it: the transcript, the caption, the
author handle, and the link. Ask the user one question first: "skill or
agent?" Then let `skill-creator` run its own process and write the result
into `~/.claude/skills/` (or an agent file if they chose agent).

## 6. Clean up

Delete the video file after transcription succeeds. Keep the transcript and
metadata in the working folder as the archive.

## Error handling

- If yt-dlp returns a login or rate-limit error, retry once with
  `--cookies-from-browser chrome` (uses the user's existing logged-in
  browser, read-only).
- If the link is a photo post or carousel, say it has no audio track and
  offer to build from the caption alone.
- Never crash the session. Report the failing step and stop cleanly.
