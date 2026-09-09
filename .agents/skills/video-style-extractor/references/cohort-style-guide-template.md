# Cohort Style Guide (STYLE-GUIDE.md template)

**Source cohort:** <video slugs>
**Extraction run:** <timestamp>
**Mascot detected:** yes | no

---

## Invariants classification

- **Locked** (>=90% of cohort): apply when recreating any asset in this style.
- **Typical** (60 to 89%): apply unless a better signal says otherwise.
- **Variable** (<60%): per-video choice, do not enforce.

## Palette

| Role       | Hex     | Class   | Evidence            |
|------------|---------|---------|---------------------|
| Background | #RRGGBB | locked  | v1/frame_0003.jpg   |
| Accent 1   | #RRGGBB | typical | v2/frame_0011.jpg   |
| ...        |         |         |                     |

## Typography

| Role     | Font        | Weight | Case       | Class  | Evidence           |
|----------|-------------|--------|------------|--------|--------------------|
| Headline | <font name> | 700    | sentence   | locked | v1/frame_0007.jpg  |
| Body     | <font name> | 500    | sentence   | typical| v3/frame_0020.jpg  |

## Motion grammar

- Dominant transition: <cut | whip | zoom | dissolve>  (class)
- Median shot length: <ms>
- Shot length range: <min> to <max> ms
- Cuts per second: <avg>

## Overlays and safe zones

- Lower-third padding: <px> from bottom
- Logo placement: <coords or rule-of-thirds cell>
- Caption style: <description>

## Pacing fingerprint

- Cuts/sec: <avg> (cohort sigma <value>)
- Words/sec: <avg>
- Front-loaded / steady / crescendo: <classification>

## Audio targets

- Integrated LUFS: <avg> (range <min> to <max>)
- LRA: <avg>
- True peak: <max>

## Mascot cross-reference

If a mascot was detected: `MASCOT-KIT/mascot-profile.json`, consistent or variants flagged in `MASCOT-VARIANTS.md`.

## One-off choices

Per-video observations that did not meet invariant thresholds:

- <video_slug>: <observation>

## Evidence index

All cited frames: <list of evidence frame paths>
