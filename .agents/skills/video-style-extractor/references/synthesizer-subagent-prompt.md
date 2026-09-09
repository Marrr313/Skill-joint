# Synthesizer Subagent Prompt

Dispatched at Step 10 of the pipeline. Consumes all per-video analyses, corrections, and mascot results, then produces `STYLE-GUIDE.md`.

---

You are synthesizing a cohort style guide from a video-style-extractor pipeline run.

**Inputs available in `<working-dir>/`:**
- `cohort-analysis.md`: raw Pass A output (cohort invariants)
- `per-video/<slug>/gemini-visual.md`: per-video visual pass
- `per-video/<slug>/gemini-transcript.md`: transcripts and cadence
- `per-video/<slug>/corrections.md`: frame-verification YAML corrections
- `per-video/<slug>/audio-metrics.json`: LUFS values
- `per-video/<slug>/scenes.json`: cut timestamps
- `MASCOT-KIT/mascot-profile.json` (if mascot detected)

**Your task:**
Read all inputs. Parse `corrections.md` as YAML and apply each correction to the claim it references before using that claim. Then write `STYLE-GUIDE.md` using the template at `references/cohort-style-guide-template.md`.

**Rules:**
1. Report INVARIANTS, meaning style choices appearing in >=60% of the cohort. Flag >=90% as "locked," 60 to 89% as "typical," <60% as "variable."
2. Every hex, font name, and timing value must cite at least one evidence frame from `per-video/<slug>/frames/`.
3. If the cohort has mascot-bearing videos, cross-reference the MASCOT-KIT profile in a dedicated section.
4. Pacing fingerprint: compute average cuts/second, median shot length, and words-per-second from transcripts. Report as a range, not a single number.
5. Do NOT average palettes across variants. If MASCOT-VARIANTS.md exists, preserve variant separation.
6. Do NOT infer values Gemini did not report. If a value is missing, write "not determined" and note which video would clarify it.

Output `STYLE-GUIDE.md` only. Do not touch other files.
