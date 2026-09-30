from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    sprite = ROOT / "static" / "assets" / "citizens" / "aris" / "world" / "front.webp"
    reference = ROOT / "static" / "assets" / "citizens" / "aris" / "reference" / "concept" / "approved_dark_sheet_v1.webp"
    contract = (ROOT / "docs" / "departments" / "assets" / "ARIS_PREBLENDER_WORLD_BODY.md").read_text(encoding="utf-8")

    # Canon reference and runtime body both exist.
    assert reference.exists()
    assert reference.stat().st_size > 50000
    assert reference.read_bytes()[:4] == b"RIFF"
    assert b"WEBP" in reference.read_bytes()[:16]

    assert sprite.exists()
    assert sprite.stat().st_size > 1000
    assert sprite.read_bytes()[:4] == b"RIFF"
    assert b"WEBP" in sprite.read_bytes()[:16]

    # Aris joins Cato, and only Aris joins Cato in this rollout.
    assert 'aris: Object.freeze({' in js
    assert 'cato: Object.freeze({' in js
    assert 'baseBody: "/static/assets/citizens/aris/world/front.webp"' in js
    assert 'futureModelSlot: "/static/assets/citizens/aris/world/model.glb"' in js
    for citizen in ("bex", "iri", "noma", "vale"):
        assert f'/static/assets/citizens/{citizen}/world/front.webp' not in js

    # Relative character scale is presentation-only and keeps Aris readable
    # at full Local zoom-out.
    assert "presentationScale: 0.881" in js
    assert "minReadableScale: 0.52" in js
    assert "perspectiveScale * Number(visual.presentationScale || 1)" in js
    assert "Number(visual.minReadableScale || 0.5)" in js
    assert "1.85 m" in contract
    assert "renderer values only" in contract

    # Both body citizens share authoritative movement logic.
    assert "citizenRenderMeters(item.data, now)" in js
    assert "localWorld(x, y, bodyLift)" in js
    assert 'item.element.classList.toggle("route-traveling", routeTraveling)' in js
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    # Bodies remain Local-only because citizen markers are rebuilt only
    # inside the Local mode block; globe modes expose location markers only.
    local_block = js.index('if (mode === "local") {')
    citizen_loop = js.index('for (const citizen of state && state.citizens || [])', local_block)
    assert citizen_loop > local_block
    assert 'if (item.type === "location") {\n      return globeWorld' in js

    # Aris has his own grounded, cyan-accented treatment and reduced motion.
    assert ".citizen-marker.aris-world-body" in css
    assert ".aris-world-body::before" in css
    assert ".aris-world-body.selected::before" in css
    assert "@keyframes aris-world-travel-bob" in css
    assert "@keyframes aris-world-travel-shadow" in css
    assert "prefers-reduced-motion" in css

    # Concept-art equipment remains non-authoritative.
    assert "No:" in contract
    assert "becomes authoritative merely because the concept art depicts it" in contract

    print("Agent City v0.9.14 Aris Local world-body smoke passed.")


if __name__ == "__main__":
    main()
