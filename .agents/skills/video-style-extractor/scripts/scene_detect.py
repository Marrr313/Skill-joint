"""Wrap PySceneDetect ContentDetector and emit scenes.json."""
import json
import sys
from pathlib import Path

from scenedetect import detect, ContentDetector


def detect_scenes(video_path: Path, threshold: float = 27.0) -> list[dict]:
    scene_list = detect(str(video_path), ContentDetector(threshold=threshold))
    scenes = []
    for start, end in scene_list:
        scenes.append({
            "start_ms": int(start.get_seconds() * 1000),
            "end_ms": int(end.get_seconds() * 1000),
        })
    # If no cuts detected, treat whole video as a single scene.
    if not scenes:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        cap.release()
        duration_ms = int((frames / fps) * 1000) if fps else 0
        scenes = [{"start_ms": 0, "end_ms": duration_ms}]
    return scenes


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: scene_detect.py <video> <out.json>", file=sys.stderr)
        return 2
    video = Path(sys.argv[1])
    out = Path(sys.argv[2])
    scenes = detect_scenes(video)
    out.write_text(json.dumps({"scenes": scenes, "count": len(scenes)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
