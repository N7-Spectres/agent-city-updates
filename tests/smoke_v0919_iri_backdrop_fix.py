from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    assert "backdropTolerance: 72" in js
    assert "backdropFringe: 126" in js
    assert "backdropDarkLuma: 108" in js
    assert "backdropCropPadding: 3" in js

    # Cleanup must remain border-connected rather than globally deleting dark
    # pixels, protecting Iri's enclosed visor/joints while removing the matte.
    assert "const connected = new Uint8Array(count);" in js
    assert "const queued = new Uint8Array(count);" in js
    assert "const queue = new Int32Array(count);" in js
    assert "const isBackdropCandidate = index =>" in js
    assert "luma <= darkLuma" in js
    assert "for (let dy = -1; dy <= 1; dy += 1)" in js
    assert "pixels[(index * 4) + 3] = 0;" in js

    # After cleanup the renderer crops to remaining alpha content so the
    # rectangular source canvas cannot remain visible around Iri.
    assert "let minX = width;" in js
    assert "let maxX = -1;" in js
    assert "const outputCanvas = document.createElement" in js
    assert 'img.src = outputCanvas.toDataURL("image/png");' in js

    # Presentation-only: no physical authority mutations.
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    print("Agent City v0.9.19 Iri backdrop cleanup smoke passed.")


if __name__ == "__main__":
    main()
