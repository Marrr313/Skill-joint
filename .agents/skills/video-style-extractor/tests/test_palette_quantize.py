import json
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

def test_palette_quantize_finds_exactly_4_colors(tmp_path):
    out = tmp_path / "palette.json"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.palette_quantize",
         str(FIXTURES / "mascot_4color.png"), str(out)],
        capture_output=True, text=True, cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert data["k"] == 4
    assert len(data["hex"]) == 4
    assert data["space"] == "LAB"
    assert data["reconstruction_delta_e_mean"] < 3.0
