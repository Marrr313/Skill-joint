"""LAB-space k-means palette quantization with AA pre-filter."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.color import rgb2lab, deltaE_cie76
from sklearn.cluster import KMeans


def _prefilter_aa(rgba: np.ndarray) -> np.ndarray:
    h, w, _ = rgba.shape
    alpha = rgba[..., 3]
    rgb = rgba[..., :3]
    keep = np.zeros((h, w), dtype=bool)
    for y in range(h):
        for x in range(w):
            if alpha[y, x] == 0:
                continue
            c = rgb[y, x]
            ok = True
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w:
                    if alpha[ny, nx] == 0:
                        continue
                    if not np.array_equal(rgb[ny, nx], c):
                        ok = False
                        break
            keep[y, x] = ok
    return rgb[keep]


def _rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    return rgb2lab((rgb / 255.0).reshape(1, -1, 3)).reshape(-1, 3)


def _lab_to_rgb_hex(lab: np.ndarray) -> list[str]:
    from skimage.color import lab2rgb
    rgb = lab2rgb(lab.reshape(1, -1, 3)).reshape(-1, 3)
    rgb = (np.clip(rgb, 0, 1) * 255).astype(int)
    return [f"#{r:02X}{g:02X}{b:02X}" for r, g, b in rgb]


def quantize(image_paths: list[Path], k_candidates=(4, 6, 8, 12, 16), max_de=3.0) -> dict:
    pixels = []
    for p in image_paths:
        im = np.array(Image.open(p).convert("RGBA"))
        filtered = _prefilter_aa(im)
        if filtered.size:
            pixels.append(filtered)
    if not pixels:
        raise ValueError("no non-AA pixels found across inputs")
    rgb = np.concatenate(pixels, axis=0)
    lab = _rgb_to_lab(rgb)
    best = None
    for k in k_candidates:
        if len(lab) < k:
            continue
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(lab)
        recon = km.cluster_centers_[km.labels_]
        de = float(np.mean(deltaE_cie76(lab, recon)))
        if best is None or de < best["de"]:
            best = {"k": k, "de": de, "centers": km.cluster_centers_}
        if de < max_de:
            best = {"k": k, "de": de, "centers": km.cluster_centers_}
            break
    hex_list = _lab_to_rgb_hex(best["centers"])
    return {
        "k": best["k"],
        "hex": hex_list,
        "reconstruction_delta_e_mean": round(best["de"], 3),
        "space": "LAB",
    }


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: palette_quantize.py <in.png> [<in2.png> ...] <out.json>", file=sys.stderr)
        return 2
    *inputs, out = sys.argv[1:]
    result = quantize([Path(p) for p in inputs])
    Path(out).write_text(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
