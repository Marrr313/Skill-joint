"""Assemble labeled pose frames into a sprite sheet.

Input: JSON mapping pose_label → list of frame paths.
Output: single PNG with one column per pose, frames as rows.
"""
import json
import sys
from pathlib import Path

from PIL import Image


def build(pose_map: dict[str, list[Path]], out: Path, cell: int = 128) -> None:
    poses = list(pose_map.items())
    cols = len(poses)
    rows = max(len(frames) for _, frames in poses)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (0, 0, 0, 0))
    for c, (_, frames) in enumerate(poses):
        for r, fp in enumerate(frames):
            im = Image.open(fp).convert("RGBA")
            im.thumbnail((cell, cell), Image.NEAREST)
            x = c * cell + (cell - im.width) // 2
            y = r * cell + (cell - im.height) // 2
            sheet.paste(im, (x, y), im)
    sheet.save(out)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: sprite_sheet.py <pose_map.json> <out.png>", file=sys.stderr)
        return 2
    mapping = json.loads(Path(sys.argv[1]).read_text())
    pose_map = {k: [Path(p) for p in v] for k, v in mapping.items()}
    build(pose_map, Path(sys.argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
