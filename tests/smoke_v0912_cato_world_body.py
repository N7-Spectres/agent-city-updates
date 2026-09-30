from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "world3d" / "planet_lab.css").read_text(encoding="utf-8")
    sprite = ROOT / "static" / "assets" / "citizens" / "cato" / "world" / "front.webp"
    contract = (ROOT / "docs" / "departments" / "assets" / "CATO_PREBLENDER_WORLD_BODY.md").read_text(encoding="utf-8")

    # A real runtime body asset exists rather than Cato remaining token-only.
    assert sprite.exists()
    assert sprite.stat().st_size > 1000
    assert sprite.read_bytes()[:4] == b"RIFF"
    assert b"WEBP" in sprite.read_bytes()[:16]

    assert "const CITIZEN_WORLD_VISUALS" in js
    assert 'cato: Object.freeze({' in js
    assert 'kind: "sprite_body"' in js
    assert 'baseBody: "/static/assets/citizens/cato/world/front.webp"' in js
    assert '"world-body-marker", "cato-world-body"' in js

    # Body is grounded on the same authoritative Local movement/travel pipeline.
    assert "citizenRenderMeters(item.data, now)" in js
    assert "const bodyLift = worldVisualFor(item.id)?.kind" in js
    assert "localWorld(x, y, bodyLift)" in js
    assert 'item.element.classList.toggle("route-traveling", routeTraveling)' in js

    # Presentation spread can widen around the larger body without changing truth.
    assert "const hasBodyPilot = colocated.some" in js
    assert "worldVisualFor(other.id)?.kind" in js
    assert ".position_x_m =" not in js
    assert ".position_y_m =" not in js

    # Equipment is a separate empty runtime layer, never baked into body state.
    assert 'className = "world-equipment-layer"' in js
    assert ".cato-world-body .world-equipment-layer" in css
    assert "equipment-free" in contract
    assert "No concept-art prop becomes inventory" in contract

    # Body feels grounded and selected without pretending to be a true mesh.
    assert ".citizen-marker.cato-world-body" in css
    # Grounding percentage may be tuned by later presentation-only patches;
    # keep the invariant that the body is horizontally centered and foot-anchored.
    assert "transform: translate(-50%, -" in css
    assert "transform-origin: 50%" in css
    assert ".cato-world-body::after" in css
    assert ".cato-world-body.selected .world-body-image" in css
    assert "@keyframes cato-world-travel-bob" in css
    assert "prefers-reduced-motion" in css

    # Blender handoff is planned but not loaded as if it already existed.
    assert 'futureModelSlot: "/static/assets/citizens/cato/world/model.glb"' in js
    assert not (ROOT / "static" / "assets" / "citizens" / "cato" / "world" / "model.glb").exists()
    assert "2.5D pre-Blender body pilot" in contract

    print("Agent City v0.9.12 Cato pre-Blender world-body smoke passed.")


if __name__ == "__main__":
    main()
