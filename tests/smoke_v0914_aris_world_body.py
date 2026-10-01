from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    sprite = ROOT / "static" / "assets" / "citizens" / "aris" / "world" / "front.png"
    reference = ROOT / "static" / "assets" / "citizens" / "aris" / "reference" / "concept" / "approved_dark_sheet_v1.webp"
    contract = (ROOT / "docs" / "departments" / "assets" / "ARIS_PREBLENDER_WORLD_BODY.md").read_text(encoding="utf-8")

    # Canon reference and runtime body both exist.
    assert reference.exists()
    reference_bytes = reference.read_bytes()
    assert len(reference_bytes) > 10000
    assert reference_bytes[:4] == b"RIFF"
    assert b"WEBP" in reference_bytes[:16]
    declared_size = int.from_bytes(reference_bytes[4:8], "little") + 8
    assert declared_size == len(reference_bytes)

    assert sprite.exists()
    sprite_bytes = sprite.read_bytes()
    assert sprite.stat().st_size == 14262
    assert sprite_bytes[:8] == b"\x89PNG\r\n\x1a\n"
    # PNG color type 6 = RGBA, required so the Local body has real transparency.
    assert sprite_bytes[25] == 6

    # Aris remains correctly configured even as later citizens are separately promoted.
    assert 'aris: Object.freeze({' in js
    assert 'cato: Object.freeze({' in js
    assert 'baseBody: "/static/assets/citizens/aris/world/front.png"' in js
    assert 'futureModelSlot: "/static/assets/citizens/aris/world/model.glb"' in js
    for citizen in ("bex", "noma", "vale"):
        assert f'{citizen}: Object.freeze({{' not in js

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
