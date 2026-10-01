from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    source = ROOT / "static" / "assets" / "citizens" / "iri" / "full.webp"
    contract = (ROOT / "docs" / "departments" / "assets" / "IRI_PREBLENDER_WORLD_BODY.md").read_text(encoding="utf-8")

    # Iri uses the existing repository body source, not an unverified new binary.
    assert source.exists()
    data = source.read_bytes()
    assert len(data) > 2000
    assert data[:4] == b"RIFF"
    assert b"WEBP" in data[:16]

    # Iri is the third promoted Local body.
    assert 'iri: Object.freeze({' in js
    assert 'baseBody: "/static/assets/citizens/iri/full.webp"' in js
    assert 'futureModelSlot: "/static/assets/citizens/iri/world/model.glb"' in js
    assert "presentationScale: 0.848" in js
    assert "minReadableScale: 0.50" in js

    # Background removal is presentation-only and connected to the image border,
    # so dark internal robot parts are not globally keyed away.
    assert "removeConnectedBackdrop: true" in js
    assert "backdropTolerance: 54" in js
    assert "function prepareWorldBodyImage(img, visual)" in js
    assert 'canvas.getContext("2d"' in js
    assert "const connected = new Uint8Array(count);" in js
    assert "const queue = new Int32Array(count);" in js
    assert 'img.src = canvas.toDataURL("image/png");' in js
    assert 'img.dataset.worldBodyCleaned = "1";' in js

    # Physical authority stays in the existing Simulation-driven route pipeline.
    assert "citizenRenderMeters(item.data, now)" in js
    assert "localWorld(x, y, bodyLift)" in js
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    # Bodies remain Local-only.
    local_block = js.index('if (mode === "local") {')
    citizen_loop = js.index('for (const citizen of state && state.citizens || [])', local_block)
    assert citizen_loop > local_block
    assert 'if (item.type === "location") {\n      return globeWorld' in js

    # The other unreviewed citizens remain token-based.
    for citizen in ("bex", "noma", "vale"):
        assert f'{citizen}: Object.freeze({{' not in js

    # Iri has a distinct research/analysis presentation.
    assert ".citizen-marker.iri-world-body" in css
    assert ".iri-world-body::before" in css
    assert ".iri-world-body.selected::before" in css
    assert "@keyframes iri-world-travel-bob" in css
    assert "@keyframes iri-world-travel-shadow" in css
    assert ".world-body-image.world-body-cleaning" in css
    assert "prefers-reduced-motion" in css

    # Shared body stacking remains active.
    assert ".citizen-marker.citizen-world-body {" in css
    assert "z-index: 23;" in css

    # Durable canon / truth boundary.
    assert "1.78 m" in contract
    assert "sensor-halo" in contract
    assert "visual identity cue only" in contract
    assert "renderer values only" in contract
    assert "merely because it is depicted" in contract

    print("Agent City v0.9.18 Iri Local world-body smoke passed.")


if __name__ == "__main__":
    main()
