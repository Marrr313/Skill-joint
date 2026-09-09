"""Detect native animation fps by finding modal frame-hold count."""
import json
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


def detect(video: Path, bbox: tuple[int, int, int, int] | None = None,
           delta_threshold: float = 5.0) -> dict:
    cap = cv2.VideoCapture(str(video))
    source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    deltas: list[bool] = []  # True = distinct, False = near-duplicate
    prev = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if bbox:
            x, y, w, h = bbox
            frame = frame[y:y + h, x:x + w]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            mad = float(np.mean(np.abs(gray.astype(np.int16) - prev.astype(np.int16))))
            deltas.append(mad > delta_threshold)
        prev = gray
    cap.release()
    if not deltas:
        return {"native_animation_fps": None, "confidence": "low",
                "reason": "insufficient frames"}
    # Count run-lengths of near-duplicates between distinct transitions.
    gaps: list[int] = []
    run = 1
    for d in deltas:
        if d:
            gaps.append(run)
            run = 1
        else:
            run += 1
    if not gaps:
        gaps = [1]
    modal_gap = Counter(gaps).most_common(1)[0][0]
    fps = source_fps / modal_gap
    confidence = "high" if fps <= 20 else "low"
    return {
        "native_animation_fps": round(fps, 2),
        "source_fps": round(source_fps, 2),
        "modal_gap_frames": modal_gap,
        "confidence": confidence,
    }


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: native_fps_detect.py <video> <out.json> [<x> <y> <w> <h>]",
              file=sys.stderr)
        return 2
    video = Path(sys.argv[1])
    out = Path(sys.argv[2])
    bbox = None
    if len(sys.argv) == 7:
        bbox = tuple(int(v) for v in sys.argv[3:7])
    out.write_text(json.dumps(detect(video, bbox), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
