# /watch

**Give Claude the ability to watch any video.**

Paste a URL or a local path, ask a question, and Claude downloads the video, extracts frames at an auto-scaled rate, pulls a timestamped transcript (free captions when available, Whisper API as fallback), and reads every frame as an image. By the time it answers, it has actually seen the video and heard the audio.

```
/watch https://youtu.be/dQw4w9WgXcQ what happens at the 30 second mark?
```

Zero config to start. `yt-dlp` and `ffmpeg` install on first run via `brew` on macOS (Linux and Windows print the exact commands). Captions cover most public videos for free. A Whisper API key is only needed when a video has no captions.

## Why this exists

Claude can read a webpage, run a script, browse a repo. What it cannot do out of the box is watch a video. You paste a YouTube link and it has to either guess from the title or pull a transcript that misses most of what is on screen.

`/watch` closes that gap. It hands Claude two streams of evidence at once: the frames (what is on screen at each timestamp) and the transcript (what is said at each timestamp). Claude answers the way someone who actually watched the video would, citing the moments that matter instead of paraphrasing a description.

## What people use it for

**Analyze someone else's content.** `/watch https://youtu.be/<viral-video> what hook did they open with?` Claude looks at the first frames, reads the opening transcript, and breaks down the structure. The same works for ad creative, competitor launches, podcast intros, anything where the *how* matters as much as the *what*.

**Diagnose a bug from a video.** Someone sends a screen recording of something broken. `/watch bug-repro.mov what's going wrong?` Claude watches the recording, finds the frame where the issue appears, and describes what is on screen, often catching the cause without you opening the file.

**Summarize a video.** `/watch https://youtu.be/<long-thing> summarize this` pulls the structure, the key moments, and what was actually said and shown. Faster than watching at 2x.

## How it works

1. **You paste a video and a question.** A URL (anything yt-dlp supports: YouTube, Loom, TikTok, X, Instagram, and a few hundred more) or a local path (`.mp4`, `.mov`, `.mkv`, `.webm`).
2. **`yt-dlp` downloads it.** For URLs, into a temp working directory. For local files, no download; it is probed in place.
3. **`ffmpeg` extracts frames at an auto-scaled rate.** The frame budget is duration-aware: 30s or less gets about 30 frames, 30 to 60s gets about 40, 1 to 3min gets about 60, 3 to 10min gets about 80, longer gets 100 sparsely. Hard ceilings: 2 fps, 100 frames. JPEGs at 512px wide by default; bump with `--resolution 1024` if Claude needs to read on-screen text.
4. **The transcript comes from one of two places.** First try: `yt-dlp` pulls native captions (manual or auto-generated) from the source. Free, instant, accurate enough. Fallback: extract a mono 16 kHz audio clip and ship it to Whisper, either Groq's `whisper-large-v3` (preferred: cheaper and faster) or OpenAI's `whisper-1`.
5. **Frames and transcript are handed to Claude.** The script prints frame paths with `t=MM:SS` markers and the transcript with timestamps. Claude reads each frame in parallel; JPEGs render directly as images in its context.
6. **Claude answers grounded in what is actually on screen and in the audio.** Not "based on the description." It saw the frames. It heard the transcript.
7. **Cleanup.** The script prints a working directory at the end. If you are not asking follow-ups, Claude removes it.

## Install

### Claude Code

Once this is published to a GitHub repo (replace `YOUR-GH-USER/claude-watch` with the real slug):

```
/plugin marketplace add YOUR-GH-USER/claude-watch
/plugin install watch@claude-watch
```

Update later with `/plugin update watch@claude-watch`.

Or install it straight from this folder with no marketplace:

```bash
cp -R claude-watch ~/.claude/skills/watch
```

Claude Code auto-discovers skills by their `SKILL.md` front matter.

### claude.ai (web)

1. Build the bundle: `bash scripts/build-skill.sh` produces `dist/watch.skill` (or download a prebuilt `watch.skill` from the published release).
2. Go to Settings → Capabilities → Skills.
3. Click `+` and drop the file in.

Enable "Code execution and file creation" under Capabilities first. The skill shells out to `ffmpeg` and `yt-dlp`, so it will not run without it.

### Codex / generic skills

```bash
cp -R claude-watch ~/.codex/skills/watch
```

## First run

On the first `/watch` call, the skill runs `scripts/setup.py --check`. If `ffmpeg` / `yt-dlp` are not on your PATH, or no Whisper API key is set, it walks you through fixing it:

- **macOS**: auto-runs `brew install ffmpeg yt-dlp`.
- **Linux**: prints the exact `apt` / `dnf` / `pipx` commands.
- **Windows**: prints the `winget` / `pip` commands.
- **API key**: scaffolds `~/.config/watch/.env` (mode `0600`) with commented placeholders for `GROQ_API_KEY` (preferred) and `OPENAI_API_KEY`.

After setup, preflight is silent and `/watch` just works. The check is a sub-100ms lookup, so it does not slow you down on later runs.

You can also run setup once by hand:

```bash
python3 scripts/setup.py
```

## Bring your own keys

Captions cover the majority of public videos for free. The Whisper fallback only kicks in when a video genuinely has no caption track: typically local files, TikToks, some Vimeos, and the occasional caption-less YouTube upload.

| Capability | What you need | Cost |
|------------|---------------|------|
| Download + native captions | `yt-dlp` + `ffmpeg` | Free |
| Whisper fallback (preferred) | [Groq API key](https://console.groq.com/keys), `whisper-large-v3` | Cheap, fast |
| Whisper fallback (alt) | [OpenAI API key](https://platform.openai.com/api-keys), `whisper-1` | Standard pricing |
| Disable Whisper entirely | `--no-whisper` | Free, frames-only when no captions |

Your keys live only in `~/.config/watch/.env` (mode `0600`) on your own machine. They are never logged, never written to output, and a Groq key only ever goes to `api.groq.com` (OpenAI key only to `api.openai.com`).

## Usage

```
/watch https://youtu.be/dQw4w9WgXcQ what happens at the 30 second mark?
/watch https://www.tiktok.com/@user/video/123 summarize this
/watch ~/Movies/screen-recording.mp4 when does the UI break?
/watch https://vimeo.com/123 what tools does she mention?
```

Focus on a specific section for a denser frame budget and lower token cost:

```
/watch https://youtu.be/abc --start 2:15 --end 2:45
/watch video.mp4 --start 50 --end 60
/watch "$URL" --start 1:12:00            # from 1h12m to end
```

Other knobs (passed to `scripts/watch.py`):

- `--max-frames N`: lower the frame cap for a tighter token budget.
- `--resolution W`: bump frame width to 1024 px when Claude needs to read on-screen text (slides, terminals, code).
- `--fps F`: override the auto-fps calculation (still capped at 2 fps).
- `--whisper groq|openai`: force a specific Whisper backend.
- `--no-whisper`: disable transcription entirely; frames only.
- `--out-dir DIR`: keep working files somewhere specific (default: an auto-generated tmp dir).

## Limits

- **Best accuracy: under 10 minutes.** Past that the script prints a "sparse scan" warning. Re-run focused on the part you care about with `--start` / `--end`.
- **Hard caps: 2 fps, 100 frames.** Frame count drives token cost; the script enforces this even when the auto-fps math would imply higher.
- **Whisper upload limit: 25 MB.** At mono 16 kHz that is about 50 minutes of audio. Longer videos need either captions or `--start` / `--end` to a smaller window.
- **No private platforms.** This skill does not log into anything. Public URLs and local files only. If yt-dlp cannot reach it without auth, neither can `/watch`.

## Structure

```
.
├── SKILL.md                 # skill contract, loaded by all three surfaces
├── scripts/
│   ├── watch.py             # entry point: download, frames, transcript
│   ├── download.py          # yt-dlp wrapper
│   ├── frames.py            # ffmpeg frame extraction + auto-fps logic
│   ├── transcribe.py        # VTT parsing + dedupe + Whisper orchestration
│   ├── whisper.py           # Groq / OpenAI clients (pure stdlib)
│   ├── setup.py             # preflight + installer
│   └── build-skill.sh       # build dist/watch.skill for claude.ai upload
├── hooks/                   # SessionStart status hook (Claude Code only)
├── .claude-plugin/          # plugin.json + marketplace.json (Claude Code)
├── .codex-plugin/           # codex packaging
└── .github/workflows/       # release.yml, auto-builds watch.skill on tag push
```

## License and credit

MIT. See [LICENSE](LICENSE).

Built on the open-source `watch` skill (MIT licensed) by Bradley Bonanno, packaged as a free standalone tool. Stands on `yt-dlp`, `ffmpeg`, and Claude's multimodal `Read` tool. Whisper transcription via [Groq](https://groq.com) or [OpenAI](https://openai.com).

---

Grab this and more free in the **Jens AI Community**. It is where the builders who hire AI into every role of their business hang out, free to join.
