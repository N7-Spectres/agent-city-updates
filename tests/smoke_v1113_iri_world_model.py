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


def joint_names(gltf: dict) -> set[str]:
    return {gltf["nodes"][index]["name"] for index in gltf["skins"][0]["joints"]}


def mesh_height(gltf: dict) -> float:
    top = 0.0
    bottom = 0.0
    for mesh in gltf["meshes"]:
        for primitive in mesh["primitives"]:
            accessor = gltf["accessors"][primitive["attributes"]["POSITION"]]
            top = max(top, accessor["max"][1])
            bottom = min(bottom, accessor["min"][1])
    return top - bottom


def main() -> None:
    js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")
    citizens = ROOT / "static" / "assets" / "citizens"

    iri = read_glb_json(citizens / "iri" / "world" / "model.glb")
    cato = read_glb_json(citizens / "cato" / "world" / "model.glb")

    # Same rig and clips as Cato, so one loader and animation path serves both.
    assert {anim.get("name") for anim in iri.get("animations", [])} >= {"Idle", "Walk"}
    assert iri.get("skins"), "Iri model must be rigged"
    assert joint_names(iri) == joint_names(cato)

    # Authored in meters at Iri's presentation-height cue (halo included).
    assert 1.70 <= mesh_height(iri) <= 1.90, mesh_height(iri)
    assert mesh_height(iri) < mesh_height(cato)

    # Iri's visual entry declares the model; the cleaned sprite stays as fallback.
    iri_block = js.split("iri: Object.freeze({", 1)[1].split("\n  });", 1)[0]
    assert 'src: "/static/assets/citizens/iri/world/model.glb"' in iri_block
    assert 'clips: Object.freeze({ idle: "Idle", walk: "Walk" })' in iri_block
    assert 'baseBody: "/static/assets/citizens/iri/full.webp"' in iri_block
    assert "removeConnectedBackdrop: true" in iri_block
    assert "iri: 1.78," in js

    print("v1.1.13 Iri world model smoke passed")


if __name__ == "__main__":
    main()
