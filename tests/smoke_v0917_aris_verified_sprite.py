from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sprite = ROOT / "static" / "assets" / "citizens" / "aris" / "world" / "front.png"
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    data = sprite.read_bytes()
    assert len(data) == 14262
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[25] == 6  # RGBA

    git_blob = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    assert git_blob == "f8811d359b1a232b0f27ce41d87163d5ac4cc57f"

    assert 'baseBody: "/static/assets/citizens/aris/world/front.png"' in js
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    print("Agent City v0.9.17 verified Aris sprite smoke passed.")


if __name__ == "__main__":
    main()
