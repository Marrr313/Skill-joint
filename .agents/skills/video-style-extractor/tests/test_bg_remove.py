import json
import subprocess
import sys
from pathlib import Path

from PIL import Image
import numpy as np

FIXTURES = Path(__file__).parent / "fixtures"

def test_chroma_key_removes_solid_cream(tmp_path):
    out_png = tmp_path / "out.png"
    out_meta = tmp_path / "meta.json"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.bg_remove",
         str(FIXTURES / "mascot_on_cream.png"), str(out_png), str(out_meta)],
        capture_output=True, text=True, cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    meta = json.loads(out_meta.read_text())
    assert meta["method"] == "chroma-key"
    arr = np.array(Image.open(out_png).convert("RGBA"))
    # The cream-colored pixels (corners) should be transparent.
    assert arr[0, 0, 3] == 0
    # Center mascot pixel should be opaque.
    assert arr[64, 64, 3] > 200
