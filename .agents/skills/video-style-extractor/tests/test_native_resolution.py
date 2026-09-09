import json, subprocess, sys
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

def test_detects_8x_scale_and_32x32_native(tmp_path):
    out = tmp_path / "res.json"
    result = subprocess.run(
        [sys.executable, "-m", "scripts.native_resolution",
         str(FIXTURES / "mascot_scaled_8x.png"), str(out)],
        capture_output=True, text=True, cwd=Path(__file__).parents[1],
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(out.read_text())
    assert data["scale"] == 8
    assert data["native_resolution_px"] == {"w": 32, "h": 32}
    assert data["confidence"] == "high"
