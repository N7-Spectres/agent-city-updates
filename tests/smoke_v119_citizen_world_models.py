from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, total_length = struct.unpack("<4sII", data[:12])
    assert magic == b"glTF", "model is not a binary glTF"
    assert version == 2
    assert total_length == len(data)
    chunk_length, chunk_type = struct.unpack("<II", data[12:20])
    assert chunk_type == 0x4E4F534A, "first GLB chunk must be JSON"
    return json.loads(data[20:20 + chunk_length])


def main() -> None:
    world3d = ROOT / "static" / "world3d"
    js = (world3d / "planet_lab.js").read_text(encoding="utf-8")
    models_js = (world3d / "citizen_models.js").read_text(encoding="utf-8")
    html = (world3d / "planet_lab.html").read_text(encoding="utf-8")
    css = (world3d / "planet_lab.css").read_text(encoding="utf-8")

    # three.js is vendored so the 3D world keeps working offline.
    vendor = ROOT / "static" / "vendor" / "three"
    for rel in (
        "three.module.min.js",
        "LICENSE",
        "addons/loaders/GLTFLoader.js",
        "addons/utils/BufferGeometryUtils.js",
    ):
        assert (vendor / rel).exists(), rel
    assert '"three": "/static/vendor/three/three.module.min.js"' in html
    assert '"three/addons/": "/static/vendor/three/addons/"' in html
    assert "cdn" not in html.lower()
    assert 'type="module" src="/static/world3d/citizen_models.js' in html
    # Model canvas sits above the terrain canvas and below the DOM markers.
    assert html.index('id="world-canvas"') < html.index('id="citizen-model-canvas"') < html.index('id="marker-layer"')
    # Classic script still loads, so the world works if the module never does.
    assert '<script src="/static/world3d/planet_lab.js' in html

    # Cato's rigged model is in his reserved slot with Idle and Walk loops.
    model = ROOT / "static" / "assets" / "citizens" / "cato" / "world" / "model.glb"
    assert model.exists()
    gltf = read_glb_json(model)
    clip_names = {anim.get("name") for anim in gltf.get("animations", [])}
    assert {"Idle", "Walk"} <= clip_names
    assert gltf.get("skins"), "Cato model must be rigged"
    assert len(gltf["skins"][0]["joints"]) >= 10

    # Generic per-citizen model contract, so all six can gain bodies later.
    assert "model: Object.freeze({" in js
    assert 'src: "/static/assets/citizens/cato/world/model.glb"' in js
    assert 'clips: Object.freeze({ idle: "Idle", walk: "Walk" })' in js
    assert "visual?.model" in js
    assert "window.AgentCityModels.status(item.id, visual.model)" in js
    assert "window.AgentCityModels.render(" in js
    assert "pixelsPerMeter: PRESENTATION_PX_PER_METER * bodyPerspective" in js
    # Citizens without a model (or whose model fails) keep their sprite.
    assert 'kind: "sprite_body"' in js
    assert 'item.element.classList.toggle("model-active", modelActive)' in js
    assert '.citizen-world-body.model-active .world-body-image' in css
    assert 'status = "failed"' in models_js
    assert "Object.entries(clips)" in models_js

    # Animation follows authoritative travel; presentation never writes positions.
    assert "function citizenIsWalking" in js
    assert "state.paused" in js
    assert 'playRole(body, citizen.walking ? "walk" : "idle")' in models_js
    assert "function citizenHeading" in js
    assert ".position_x_m =" not in js + models_js
    assert ".position_y_m =" not in js + models_js

    # Models are only drawn in Local mode, and clicks still reach markers.
    assert 'active: mode === "local"' in js
    assert "pointer-events: none" in css.split("#citizen-model-canvas", 1)[1][:300]

    print("v1.1.9 citizen world models smoke passed")


if __name__ == "__main__":
    main()
