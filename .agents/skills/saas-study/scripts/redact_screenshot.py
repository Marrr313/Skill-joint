#!/usr/bin/env python3
"""Best-effort OCR-based screenshot redaction. Optional.

Reads:
  <study>/screenshots/*.png
  --redact "name=Ada Lovelace,email=ada@example.com" (any number of k=v pairs)

Writes:
  <study>/screenshots/<file>.png  (overwritten with blurred regions)
  <study>/raw/screenshots-original/<file>.png  (originals preserved)

Requires pytesseract + tesseract installed on the system. If unavailable, skips
gracefully with a clear message and does NOT block the rest of the pipeline.

Usage:
  redact_screenshot.py <study-folder> --redact "name=X,email=Y"
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("study")
    p.add_argument("--redact", required=True,
                   help='Comma-separated k=v pairs of literal strings to blur, e.g. "name=Ada Lovelace,email=ada@example.com"')
    args = p.parse_args()

    study = Path(args.study)
    shots = study / "screenshots"
    backup = study / "raw" / "screenshots-original"
    backup.mkdir(parents=True, exist_ok=True)

    targets = [v.strip() for pair in args.redact.split(",")
               for k, _, v in [pair.partition("=")] if v.strip()]
    if not targets:
        print("error: --redact had no usable values", file=sys.stderr)
        return 2

    try:
        from PIL import Image, ImageDraw, ImageFilter  # type: ignore
        import pytesseract  # type: ignore
    except ImportError as e:
        print(f"warn: redaction requires pillow + pytesseract ({e}); skipping", file=sys.stderr)
        print("       install: pip install pillow pytesseract && brew install tesseract", file=sys.stderr)
        return 0

    processed = 0
    for png in sorted(shots.glob("*.png")):
        try:
            img = Image.open(png).convert("RGB")
        except Exception as e:
            print(f"warn: {png.name}: {e}", file=sys.stderr)
            continue
        # Back up original (only if not already backed up)
        bkp = backup / png.name
        if not bkp.exists():
            img.save(bkp)

        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        draw = ImageDraw.Draw(img)
        hits = 0
        n = len(data.get("text", []))
        for i in range(n):
            text = (data["text"][i] or "").strip()
            if not text:
                continue
            for needle in targets:
                if needle.lower() in text.lower() or text.lower() in needle.lower():
                    x = data["left"][i]
                    y = data["top"][i]
                    w = data["width"][i]
                    h = data["height"][i]
                    # Black box with small padding
                    draw.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], fill=(0, 0, 0))
                    hits += 1
                    break
        if hits:
            img.save(png)
            processed += 1
            print(f"  redacted {hits} regions in {png.name}", file=sys.stderr)

    print(f"✓ redacted {processed}/{len(list(shots.glob('*.png')))} screenshots "
          f"(originals preserved in raw/screenshots-original/)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
