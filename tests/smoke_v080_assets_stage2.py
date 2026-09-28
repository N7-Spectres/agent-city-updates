from __future__ import annotations

import re
import tempfile
from pathlib import Path

from agent_city.asset_worker import AssetQueue, AssetSpec

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    html_ids = re.findall(r'id="([^"]+)"', html)
    js_ids = set(re.findall(r'getElementById\("([^"]+)"\)', js))
    assert len(html_ids) == len(set(html_ids)), "duplicate HTML IDs"
    assert js_ids <= set(html_ids), sorted(js_ids - set(html_ids))

    # Stage 1 interaction/identity guarantees remain intact.
    assert "citizen-job-progress" in js
    assert 'els.chatInput.addEventListener("keydown"' in js
    assert 'event.key !== "Enter" || event.shiftKey' in js
    assert "event.isComposing" in js
    assert "CITIZEN_VISUAL_PROFILES" in js

    # Stage 2 consumes only safe authoritative meter-space fields.
    for token in (
        "state?.spatial_frame",
        "position_x_m",
        "position_y_m",
        "local_movement",
        "state.spatial_observations",
        "radius_m",
        "visitorPresence.x_m",
        "visitorPresence.y_m",
    ):
        assert token in js, token
    assert "computeSpatialViewport" in js
    assert "metersToMap" in js
    assert "Local meter view" in js
    assert "scalePxPerMeter" in js

    # Continuous local movement is smoothed only from the authoritative segment.
    for token in (
        "start_x_m",
        "start_y_m",
        "target_x_m",
        "target_y_m",
        "path_distance_m",
        "movement.progress",
    ):
        assert token in js, token
    assert "local-movement-route" in css
    assert "transition: left 3.6s linear, top 3.6s linear" in css
    assert "prefers-reduced-motion" in css

    # Validated observations show uncertainty instead of false precision.
    assert "renderSpatialObservations" in js
    assert "observation-radius" in js
    assert "uncertainty radius" in js
    assert "baseline" in js
    assert "unclassified" in js
    assert "map-observation" in css

    # Shared proposal intent stays separate from real Simulation movement.
    assert "shared_action_proposals" in js
    assert "simulation_activity_id" in js
    assert "simulation_action_id" in js
    assert "A proposal is not movement" in js
    assert "Active physical activity" in js
    assert "/api/shared-actions/" in js
    assert "/accept" in js
    assert "/reject" in js
    assert "acceptance_available" in js
    assert "shared-action-card" in css

    # Hidden seeded truth is never referenced by Assets.
    assert "planet_seed" not in js
    assert "generated_deposits" not in js
    assert "richness" not in js
    assert "center_x_m" not in js
    assert "long_axis_m" not in js
    assert "short_axis_m" not in js

    # The local Asset Worker queue is a separate presentation cache.
    with tempfile.TemporaryDirectory() as tmp:
        queue = AssetQueue(Path(tmp) / "asset_worker.db")
        spec = AssetSpec(
            source_type="equipment",
            source_id="17",
            source_revision="condition-100",
            render_tier="individual",
            visual_kind="equipment",
            generator_key="procedural_v1",
            spec_json={"family": "cargo_pack", "fallback": "generic_equipment"},
        )
        queued = queue.enqueue(spec, priority=200)
        assert queued["status"] == "queued"
        claimed = queue.claim_next("smoke-worker")
        assert claimed and claimed["status"] == "working"
        assert claimed["spec"]["source_id"] == "17"
        ready = queue.mark_ready(
            claimed["id"],
            output_path="generated_assets/equipment/17/object.glb",
            output_format="glb",
            content_hash="abc123",
            generator_version="smoke-v1",
        )
        assert ready["status"] == "ready"
        # Re-enqueueing the same physical revision returns the ready job.
        again = queue.enqueue(spec)
        assert again["id"] == ready["id"]

    print("Agent City v0.8 Assets Stage 2 smoke test passed.")


if __name__ == "__main__":
    main()
