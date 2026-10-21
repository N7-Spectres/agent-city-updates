from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Presentation-height cues from docs/departments/assets/model_notes/README.md.
EXPECTED_HEIGHTS = {
    "cato": 2.10,
    "vale": 2.00,
    "aris": 1.85,
    "iri": 1.78,
    "bex": 1.60,
    "noma": 1.60,
}


def main() -> None:
    world3d = ROOT / "static" / "world3d"
    js = (world3d / "planet_lab.js").read_text(encoding="utf-8")
    models_js = (world3d / "citizen_models.js").read_text(encoding="utf-8")
    css = (world3d / "planet_lab.css").read_text(encoding="utf-8")

    # One height table for all six citizens, matching the model notes.
    table = js.split("const CITIZEN_HEIGHT_METERS = Object.freeze({", 1)[1].split("});", 1)[0]
    heights = {name: float(value) for name, value in re.findall(r"(\w+): ([0-9.]+),", table)}
    assert heights == EXPECTED_HEIGHTS, heights
    assert max(heights, key=heights.get) == "cato"

    # Sprites and models share one pixels-per-meter and one readability clamp.
    assert "const PRESENTATION_PX_PER_METER = " in js
    assert "function spritePresentationScale(citizenId, spriteArtHeightPx)" in js
    for citizen in ("aris", "cato", "iri"):
        assert f'presentationScale: spritePresentationScale("{citizen}", ' in js
    assert "minReadableScale" not in js
    assert "spritePixelHeight" not in js
    assert "bodyPerspective * Number(visual.presentationScale || 1)" in js
    assert "pixelsPerMeter: PRESENTATION_PX_PER_METER * bodyPerspective" in js

    # Models keep their authored meters, are centered on their marker, and
    # correct for the raised camera so they match sprite heights on screen.
    assert "citizen.pixelsPerMeter * worldPerPixel * foreshortening" in models_js
    assert "-(box.min.x + box.max.x) / 2" in models_js
    assert "-(box.min.z + box.max.z) / 2" in models_js
    assert "body.height" not in models_js

    # Full-body markers never draw the token frame (night glow / hover ring).
    rule = css.split("/* v1.1.11", 1)[1]
    assert "body[data-day-phase] .citizen-marker.citizen-world-body" in rule
    assert ".citizen-marker.citizen-world-body:hover" in rule
    assert "box-shadow: none;" in rule
    assert "border: 0;" in rule

    # Presentation only.
    assert ".position_x_m =" not in js + models_js
    assert ".position_y_m =" not in js + models_js

    print("v1.1.11 body scale consistency smoke passed")


if __name__ == "__main__":
    main()
