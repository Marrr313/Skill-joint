# Changelog

All notable changes to `/watch` are documented here.

## Unreleased

### Changed
- Repackaged as a clean, standalone, brand-neutral tool: removed distribution coupling to the original author's GitHub repo, sharpened the README and quickstart, and made every user-facing string em-dash-free. No runtime logic changed. Original tool by Bradley Bonanno, MIT licensed.

## [0.1.3] - 2026-05-09

### Fixed
- Windows: `video.info.json` is read as UTF-8. Previously `Path.read_text()` defaulted to cp1252 on Windows and crashed on yt-dlp's UTF-8 output, silently dropping Title/Uploader from the report. Same fix applied to `.env` reads/writes in `whisper.py` and `setup.py`.
- `download.py` now logs info.json parse failures to stderr instead of swallowing them.

### Security
- Hardened subprocess argv against option injection: inserted `--` before the URL in the yt-dlp argv, and tightened `is_url` to reject `-`-prefixed sources and require a non-empty netloc. Resolved video/audio paths to absolute via `Path.resolve()` before passing to `ffmpeg`/`ffprobe`, so a relative path starting with `-` cannot be misinterpreted as a flag.

## [0.1.2] - 2026-04-24

### Fixed
- Windows console crash: removed the emoji from the long-video warning in `watch.py`; cp1252 consoles could not encode it.
- `setup.py` now prints `winget` / `pip` install commands on Windows instead of "unsupported platform", matching what the README already promised.

### Changed
- `SKILL.md` notes that on Windows the scripts must be invoked with `python`, not `python3` (the latter is the Microsoft Store stub on Windows).

## [0.1.1] - 2026-04-24

### Fixed
- Added `commands/watch.md` shim so `/watch` is callable when installed as a Claude Code plugin. Without it, the plugin loaded but the skill was not exposed as a slash command.
- `scripts/build-skill.sh` now strips `commands/` from the claude.ai `.skill` bundle alongside `hooks/` and `.claude-plugin/`.

## [0.1.0] - 2026-04-24

Initial release.

### Added
- `/watch <url-or-path> [question]` slash command.
- yt-dlp download with native caption extraction (manual + auto-subs).
- ffmpeg frame extraction with auto-scaled fps (2 fps and 100 frames max, duration-aware budget).
- `--start` / `--end` focused mode with denser frame budget and transcript range filtering.
- Whisper fallback (Groq preferred, OpenAI secondary) for videos without captions.
- `setup.py` preflight: silent `--check`, structured `--json`, and installer that auto-runs `brew install` on macOS.
- Session-start hook that prints a one-line status on first run or partial config.
- `.skill` bundle packaging for claude.ai upload via `scripts/build-skill.sh`.
