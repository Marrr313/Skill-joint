"""Cascade background removal: chroma-key → isnet-anime → u2net."""
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.color import rgb2lab


def _sample_corner_bg(rgb: np.ndarray, size: int = 4) -> tuple[np.ndarray, float]:
    h, w, _ = rgb.shape
    patches = [
        rgb[:size, :size], rgb[:size, -size:],
        rgb[-size:, :size], rgb[-size:, -size:],
    ]
    stacked = np.concatenate([p.reshape(-1, 3) for p in patches], axis=0)
    # Use max per-channel stddev to measure background uniformity;
    # a flat np.std across all channels conflates RGB offset with variance.
    stddev = float(stacked.std(axis=0).max())
    mean_color = stacked.mean(axis=0)
    return mean_color, stddev


def _chroma_key(im: Image.Image, delta_e_max: float = 8.0) -> Image.Image | None:
    arr = np.array(im.convert("RGB"))
    bg, stddev = _sample_corner_bg(arr)
    if stddev >= 5.0:
        return None
    lab = rgb2lab(arr / 255.0)
    bg_lab = rgb2lab(bg.reshape(1, 1, 3) / 255.0)[0, 0]
    de = np.sqrt(np.sum((lab - bg_lab) ** 2, axis=-1))
    alpha = np.where(de < delta_e_max, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr, alpha])
    return Image.fromarray(rgba, "RGBA")


def _rembg_remove(im: Image.Image, model_name: str) -> Image.Image:
    from rembg import new_session, remove
    session = new_session(model_name)
    buf = io.BytesIO()
    im.save(buf, "PNG")
    out = remove(buf.getvalue(), session=session)
    return Image.open(io.BytesIO(out)).convert("RGBA")


def remove_bg(in_path: Path) -> tuple[Image.Image, str]:
    im = Image.open(in_path).convert("RGB")
    # (a) chroma-key
    ck = _chroma_key(im)
    if ck is not None:
        return ck, "chroma-key"
    # (b) isnet-anime
    try:
        return _rembg_remove(im, "isnet-anime"), "isnet-anime"
    except Exception:
        pass
    # (c) u2net
    return _rembg_remove(im, "u2net"), "u2net"


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: bg_remove.py <in> <out.png> <out_meta.json>", file=sys.stderr)
        return 2
    in_path, out_png, out_meta = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    im, method = remove_bg(in_path)
    im.save(out_png)
    out_meta.write_text(json.dumps({"method": method}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
