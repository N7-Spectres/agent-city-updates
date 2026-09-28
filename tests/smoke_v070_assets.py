from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    html_ids = re.findall(r'id="([^"]+)"', html)
    js_ids = set(re.findall(r'getElementById\("([^"]+)"\)', js))
    assert len(html_ids) == len(set(html_ids)), "duplicate HTML IDs"
    assert js_ids <= set(html_ids), sorted(js_ids - set(html_ids))

    # Scalable Home rails.
    for required_id in ("citizen-search", "recent-activity", "view-all-history", "chat-log"):
        assert required_id in html, required_id
    assert "--home-panel-height" in css
    assert ".home-shell .compact-citizen-stack" in css
    assert "overflow-y: auto" in css
    assert "citizenSearchQuery" in js

    # Recent Activity is a compact view over real chronology + stored exchanges.
    assert "recentActivityItems" in js
    assert "state?.citizen_conversations" in js
    assert "conversation.summary" in js
    assert 'row.category === "conversation"' in js
    assert "renderRecentActivity" in js
    assert 'openControlRoomView("history"' in js

    # Lightweight avatar framework supports all starting citizens and future art.
    # v0.8 may wrap the same contract in richer citizen visual profiles, so verify
    # the stable citizen IDs plus the backward-compatible flat asset view.
    assert "CITIZEN_AVATAR_ASSETS" in js
    for citizen_id in ("aris", "bex", "cato", "iri", "noma", "vale"):
        assert f"{citizen_id}:" in js
    if "CITIZEN_VISUAL_PROFILES" in js:
        assert "profile.assets.full" in js
        assert "profile.assets.token" in js
    else:
        for citizen_id in ("aris", "bex", "cato", "iri", "noma", "vale"):
            assert f"{citizen_id}: {{ full: null, token: null }}" in js
    for state_name in ("idle", "traveling", "charging", "talking", "working"):
        assert f"state-{state_name}" in css or f'"{state_name}"' in js
    assert "citizenAvatarMarkup" in js
    assert "applyCitizenPortrait" in js
    assert "avatar-full" in css
    assert "avatar-map" in css
    assert "prefers-reduced-motion" in css

    # Identity fallback must remain presentation-only and must not imply equipment/wear.
    assert "interface accent, not physical paint" in js
    assert "neutral mechanical fallback" not in html.lower() or "identity slot" in html.lower()

    # v0.7 maintenance presentation consumes Simulation-owned semantics directly.
    for required_id in ("maintenance-alerts", "maintenance-events"):
        assert required_id in html, required_id
    for field in (
        "battery_health",
        "battery_state",
        "usable_energy_capacity",
        "battery_replacement_due",
        "joint_wear",
        "chassis_service_state",
        "chassis_service_due",
        "condition_state",
        "operational",
        "service_due",
        "effective_cargo_bonus",
        "effective_extraction_speed_multiplier",
        "efficiency_multiplier",
        "maintenance_events",
    ):
        assert field in js, field
    assert "renderMaintenanceAlerts" in js
    assert "renderMaintenanceHistory" in js
    assert 'row.category === "diagnostic"' in js

    # Current equipment capability must use effective fields, not pristine design values.
    assert "Number(item.cargo_bonus" not in js
    assert "Number(item.extraction_speed_multiplier" not in js

    # Maintenance styling keeps system condition separate from citizen speech.
    assert "maintenance-event-card" in css
    assert "maintenance-alert" in css
    assert "history-entry.diagnostic" in css

    print("Agent City v0.7 Assets Home/avatar/maintenance smoke test passed.")


if __name__ == "__main__":
    main()
