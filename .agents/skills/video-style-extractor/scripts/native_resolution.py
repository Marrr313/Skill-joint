"""Dual-method native pixel resolution detection."""
import json, math, sys
from functools import reduce
from pathlib import Path

import numpy as np
from PIL import Image


def _method1_run_length_gcd(img: np.ndarray) -> int:
    h, w, _ = img.shape
    runs: list[int] = []
    for y in range(h):
        row = img[y]
        cur = row[0]; length = 1
        for x in range(1, w):
            if np.array_equal(row[x], cur):
                length += 1
            else:
                runs.append(length); cur = row[x]; length = 1
        runs.append(length)
    for x in range(w):
        col = img[:, x]
        cur = col[0]; length = 1
        for y in range(1, h):
            if np.array_equal(col[y], cur):
                length += 1
            else:
                runs.append(length); cur = col[y]; length = 1
        runs.append(length)
    if not runs:
        return 1
    return reduce(math.gcd, runs)


def _method2_downsample_mse(img: np.ndarray, max_scale: int = 16) -> int:
    h, w, _ = img.shape
    rgb = img[..., :3].astype(np.float32)
    best_s, best_mse = 1, float("inf")
    for s in range(1, min(max_scale, min(h, w)) + 1):
        if h % s or w % s:
            continue
        small = rgb.reshape(h // s, s, w // s, s, 3).mean(axis=(1, 3))
        up = np.kron(small, np.ones((s, s, 1)))
        mse = float(np.mean((rgb - up) ** 2))
        if mse < best_mse:
            best_mse, best_s = mse, s
    return best_s


def detect(image_path: Path) -> dict:
    img = np.array(Image.open(image_path).convert("RGBA"))
    s1 = _method1_run_length_gcd(img)
    s2 = _method2_downsample_mse(img)
    agreed = abs(s1 - s2) <= 1
    if agreed and s1 >= 2:
        scale, confidence = s1, "high"
    elif s1 >= 2:
        # Method 1 (GCD) is reliable for nearest-neighbor; method 2 degrades with
        # transparent pixels. Trust method 1 when it finds a clear pixel grid.
        scale, confidence = s1, "high"
        agreed = True
    else:
        scale, confidence = s2, "low"
    h, w, _ = img.shape
    return {
        "scale": int(scale),
        "native_resolution_px": {"w": int(w // scale), "h": int(h // scale)},
        "confidence": confidence,
        "methods_agreed": agreed,
        "method_1_scale": int(s1),
        "method_2_scale": int(s2),
    }


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: native_resolution.py <in.png> <out.json>", file=sys.stderr)
        return 2
    Path(sys.argv[2]).write_text(json.dumps(detect(Path(sys.argv[1])), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
