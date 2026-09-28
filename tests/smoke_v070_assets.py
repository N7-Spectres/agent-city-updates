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
    assert "CITIZEN_AVATAR_ASSETS" in js
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

    print("Agent City v0.7 Assets Home/avatar smoke test passed.")


if __name__ == "__main__":
    main()
