#!/usr/bin/env python3
"""
extract_primitives.py — harvest raw design primitives from HTML/CSS sources.

Output: JSON with frequency-ranked candidates for the categories the
DESIGN.md spec needs (colors, typography, rounded, spacing, components).

Usage:
    python3 extract_primitives.py path/to/file.html [more files...]
    python3 extract_primitives.py path/to/file.html --top 30

The script is intentionally lossy: it surfaces *what's there*, not what
should become a token. A coding agent (Claude) is expected to consume
this JSON, normalize it into a token system, and write the DESIGN.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

# ---------- Regexes ----------

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,4}){1,2}\b")
RGB_RE = re.compile(
    r"rgba?\(\s*([0-9.]+)\s*,?\s*([0-9.]+)\s*,?\s*([0-9.]+)\s*(?:[,/]\s*([0-9.]+%?))?\s*\)"
)
HSL_RE = re.compile(
    r"hsla?\(\s*([0-9.]+)(?:deg)?\s*,?\s*([0-9.]+)%\s*,?\s*([0-9.]+)%\s*(?:[,/]\s*([0-9.]+%?))?\s*\)"
)
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}{]+)", re.IGNORECASE)
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([0-9.]+)(px|rem|em|pt|%)", re.IGNORECASE)
FONT_WEIGHT_RE = re.compile(r"font-weight\s*:\s*([0-9]{3}|bold|normal|lighter|bolder)", re.IGNORECASE)
LINE_HEIGHT_RE = re.compile(r"line-height\s*:\s*([0-9.]+)(px|rem|em|%)?", re.IGNORECASE)
LETTER_SPACING_RE = re.compile(r"letter-spacing\s*:\s*(-?[0-9.]+)(px|rem|em)", re.IGNORECASE)
RADIUS_RE = re.compile(r"border-radius\s*:\s*([^;}{]+)", re.IGNORECASE)
SPACING_RE = re.compile(
    r"(?:padding|margin|gap|row-gap|column-gap)\s*:\s*([^;}{]+)", re.IGNORECASE
)
SHADOW_RE = re.compile(r"box-shadow\s*:\s*([^;}{]+)", re.IGNORECASE)
TEXT_SHADOW_RE = re.compile(r"text-shadow\s*:\s*([^;}{]+)", re.IGNORECASE)
BACKDROP_RE = re.compile(r"backdrop-filter\s*:\s*([^;}{]+)", re.IGNORECASE)
GRADIENT_RE = re.compile(
    r"(?:linear|radial|conic)-gradient\([^)]+\)", re.IGNORECASE
)
INLINE_STYLE_RE = re.compile(r'style\s*=\s*"([^"]+)"', re.IGNORECASE)
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
LINK_HREF_RE = re.compile(
    r'<link[^>]+href\s*=\s*"([^"]+)"[^>]*>', re.IGNORECASE
)
GOOGLE_FONT_RE = re.compile(r"fonts\.googleapis\.com/css[^\"']*family=([^\"'&]+)")
DIMENSION_RE = re.compile(r"(-?[0-9.]+)(px|rem|em)")

# ---------- Color helpers ----------

def normalize_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 4:  # #abc
        h = "#" + "".join(c * 2 for c in h[1:])
    elif len(h) == 5:  # #abcd
        h = "#" + "".join(c * 2 for c in h[1:4])  # drop alpha
    elif len(h) == 9:  # #aabbccdd
        h = h[:7]
    return h


def rgb_to_hex(r: str, g: str, b: str) -> str:
    try:
        return "#{:02x}{:02x}{:02x}".format(
            max(0, min(255, int(round(float(r))))),
            max(0, min(255, int(round(float(g))))),
            max(0, min(255, int(round(float(b))))),
        )
    except ValueError:
        return ""


def hsl_to_hex(h: str, s: str, l: str) -> str:
    try:
        h_v = float(h) % 360 / 360.0
        s_v = float(s) / 100.0
        l_v = float(l) / 100.0
    except ValueError:
        return ""

    def hue_to_rgb(p: float, q: float, t: float) -> float:
        if t < 0:
            t += 1
        if t > 1:
            t -= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p

    if s_v == 0:
        r = g = b = l_v
    else:
        q = l_v * (1 + s_v) if l_v < 0.5 else l_v + s_v - l_v * s_v
        p = 2 * l_v - q
        r = hue_to_rgb(p, q, h_v + 1 / 3)
        g = hue_to_rgb(p, q, h_v)
        b = hue_to_rgb(p, q, h_v - 1 / 3)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def color_luminance(hex_color: str) -> float:
    """Relative luminance for sorting / grouping."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return 0.0
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


# ---------- Extraction ----------

def collect_css_text(html_or_css: str, source_path: Path) -> str:
    """Pull together every chunk of CSS we can see in the source."""
    chunks: list[str] = []
    # Inline style attributes
    chunks.extend(INLINE_STYLE_RE.findall(html_or_css))
    # <style> blocks
    chunks.extend(STYLE_BLOCK_RE.findall(html_or_css))
    # Linked CSS files (relative paths only — we don't fetch over the network)
    for href in LINK_HREF_RE.findall(html_or_css):
        if href.startswith(("http://", "https://", "//")):
            continue
        candidate = (source_path.parent / href).resolve()
        if candidate.exists() and candidate.suffix == ".css":
            try:
                chunks.append(candidate.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    # If the source itself is CSS, include it directly
    if source_path.suffix.lower() in (".css",):
        chunks.append(html_or_css)
    return "\n".join(chunks)


def extract_colors(text: str) -> Counter:
    counter: Counter = Counter()
    for m in HEX_RE.findall(text):
        norm = normalize_hex(m)
        if len(norm) == 7:
            counter[norm] += 1
    for r, g, b, _ in RGB_RE.findall(text):
        hx = rgb_to_hex(r, g, b)
        if hx:
            counter[hx] += 1
    for h, s, l, _ in HSL_RE.findall(text):
        hx = hsl_to_hex(h, s, l)
        if hx:
            counter[hx] += 1
    return counter


def extract_font_families(text: str) -> Counter:
    counter: Counter = Counter()
    for raw in FONT_FAMILY_RE.findall(text):
        # Take the first family in the stack, strip quotes and weights
        first = raw.split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var("):
            counter[first] += 1
    # Also harvest any Google Fonts links
    for fam in GOOGLE_FONT_RE.findall(text):
        name = fam.replace("+", " ").split(":")[0]
        counter[name] += 1
    return counter


def extract_font_sizes(text: str) -> Counter:
    counter: Counter = Counter()
    for value, unit in FONT_SIZE_RE.findall(text):
        counter[f"{value}{unit}"] += 1
    return counter


def extract_font_weights(text: str) -> Counter:
    counter: Counter = Counter()
    for raw in FONT_WEIGHT_RE.findall(text):
        counter[raw.lower()] += 1
    return counter


def extract_line_heights(text: str) -> Counter:
    counter: Counter = Counter()
    for value, unit in LINE_HEIGHT_RE.findall(text):
        counter[f"{value}{unit or ''}".strip()] += 1
    return counter


def extract_letter_spacings(text: str) -> Counter:
    counter: Counter = Counter()
    for value, unit in LETTER_SPACING_RE.findall(text):
        counter[f"{value}{unit}"] += 1
    return counter


def extract_radii(text: str) -> Counter:
    counter: Counter = Counter()
    for raw in RADIUS_RE.findall(text):
        for value, unit in DIMENSION_RE.findall(raw):
            counter[f"{value}{unit}"] += 1
        if "%" in raw:
            for percent in re.findall(r"(\d+%)", raw):
                counter[percent] += 1
        if "9999" in raw or "100%" in raw or "50%" in raw:
            counter["full"] += 1
    return counter


def extract_spacing(text: str) -> Counter:
    counter: Counter = Counter()
    for raw in SPACING_RE.findall(text):
        for value, unit in DIMENSION_RE.findall(raw):
            counter[f"{value}{unit}"] += 1
    return counter


def extract_shadows(text: str) -> Counter:
    counter: Counter = Counter()
    for raw in SHADOW_RE.findall(text):
        cleaned = re.sub(r"\s+", " ", raw.strip())
        counter[cleaned] += 1
    for raw in TEXT_SHADOW_RE.findall(text):
        cleaned = re.sub(r"\s+", " ", raw.strip())
        counter[f"text: {cleaned}"] += 1
    for raw in BACKDROP_RE.findall(text):
        cleaned = re.sub(r"\s+", " ", raw.strip())
        counter[f"backdrop: {cleaned}"] += 1
    return counter


def extract_gradients(text: str) -> Counter:
    counter: Counter = Counter()
    for raw in GRADIENT_RE.findall(text):
        counter[re.sub(r"\s+", " ", raw.strip())] += 1
    return counter


def extract_class_clusters(text: str) -> Counter:
    """Surface common class name patterns to hint at component vocabulary."""
    counter: Counter = Counter()
    for cls in re.findall(r'class\s*=\s*"([^"]+)"', text):
        for token in cls.split():
            # Filter out one-letter tokens, utility-noise like `w-12`, etc.
            if len(token) < 4 or token.startswith(("w-", "h-", "p-", "m-", "pt-", "pb-", "px-", "py-", "mt-", "mb-", "mx-", "my-", "gap-", "text-", "bg-", "border-", "rounded-", "shadow-", "flex-", "grid-")):
                continue
            counter[token] += 1
    return counter


# ---------- Top-level ----------

def topn(counter: Counter, n: int) -> list[dict]:
    return [
        {"value": value, "count": count}
        for value, count in counter.most_common(n)
    ]


def process(paths: list[Path], top: int) -> dict:
    colors: Counter = Counter()
    families: Counter = Counter()
    sizes: Counter = Counter()
    weights: Counter = Counter()
    line_heights: Counter = Counter()
    letter_spacings: Counter = Counter()
    radii: Counter = Counter()
    spacing: Counter = Counter()
    shadows: Counter = Counter()
    gradients: Counter = Counter()
    classes: Counter = Counter()

    for p in paths:
        raw = p.read_text(encoding="utf-8", errors="ignore")
        css = collect_css_text(raw, p)
        # For class clusters we also look at the original HTML
        html_for_classes = raw if p.suffix.lower() in (".html", ".htm") else ""

        colors.update(extract_colors(css))
        families.update(extract_font_families(css + "\n" + raw))
        sizes.update(extract_font_sizes(css))
        weights.update(extract_font_weights(css))
        line_heights.update(extract_line_heights(css))
        letter_spacings.update(extract_letter_spacings(css))
        radii.update(extract_radii(css))
        spacing.update(extract_spacing(css))
        shadows.update(extract_shadows(css))
        gradients.update(extract_gradients(css))
        if html_for_classes:
            classes.update(extract_class_clusters(html_for_classes))

    # Sort colors by luminance to make the inventory easier to read.
    color_items = sorted(
        colors.items(), key=lambda kv: (color_luminance(kv[0]), -kv[1])
    )
    color_top = [
        {"value": value, "count": count}
        for value, count in sorted(colors.items(), key=lambda kv: -kv[1])[:top]
    ]
    color_by_lum = [{"value": v, "count": c} for v, c in color_items[: top * 2]]

    return {
        "sources": [str(p) for p in paths],
        "totals": {
            "colors_distinct": len(colors),
            "font_families_distinct": len(families),
            "font_sizes_distinct": len(sizes),
            "radii_distinct": len(radii),
            "spacing_distinct": len(spacing),
            "shadows_distinct": len(shadows),
        },
        "colors_by_frequency": color_top,
        "colors_by_luminance": color_by_lum,
        "font_families": topn(families, top),
        "font_sizes": topn(sizes, top),
        "font_weights": topn(weights, top),
        "line_heights": topn(line_heights, top),
        "letter_spacings": topn(letter_spacings, top),
        "rounded": topn(radii, top),
        "spacing": topn(spacing, top),
        "shadows": topn(shadows, max(8, top // 2)),
        "gradients": topn(gradients, max(6, top // 3)),
        "class_hints": topn(classes, top),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="HTML or CSS files to analyze")
    parser.add_argument(
        "--top",
        type=int,
        default=25,
        help="How many entries to return per category (default: 25)",
    )
    args = parser.parse_args(argv)

    paths = [Path(p).expanduser() for p in args.paths]
    missing = [p for p in paths if not p.exists()]
    if missing:
        sys.stderr.write(f"Missing files: {', '.join(str(p) for p in missing)}\n")
        return 2

    result = process(paths, args.top)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
