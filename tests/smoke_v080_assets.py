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

    # v0.7 visual/maintenance baseline remains intact.
    for required_id in (
        "citizen-search",
        "recent-activity",
        "maintenance-alerts",
        "maintenance-events",
        "chat-log",
        "chat-input",
        "send-button",
    ):
        assert required_id in html, required_id
    assert "CITIZEN_AVATAR_ASSETS" in js
    assert "renderMaintenanceAlerts" in js
    assert "renderMaintenanceHistory" in js
    assert 'row.category === "diagnostic"' in js
    assert "prefers-reduced-motion" in css

    # v0.8 Stage 1 restores glanceable active-job progress to Home citizen rows.
    assert "const progress = job ? jobProgress(job) : null" in js
    assert "citizen-job-progress" in js
    assert "citizen-job-progress-meta" in js
    assert "progress.elapsed" in js
    assert "progress.total" in js
    assert "progress.remaining" in js
    assert "formatMinute(job.end_minute)" in js
    assert "citizen-job-progress-track" in css

    # Progress remains driven by authoritative job timing + current sim minute.
    assert "Number(job.end_minute) - Number(job.start_minute)" in js
    assert "Number(state.sim_minute) - Number(job.start_minute)" in js

    # Enter sends, Shift+Enter keeps a newline, and IME composition never submits.
    assert 'els.chatInput.addEventListener("keydown"' in js
    assert 'event.key !== "Enter" || event.shiftKey' in js
    assert "event.isComposing" in js
    assert "event.keyCode === 229" in js
    assert "event.preventDefault()" in js
    assert "els.chatForm.requestSubmit(els.sendButton)" in js

    # One shared submit path and explicit in-flight guard prevent duplicate sends.
    assert "let chatSubmitting = false" in js
    assert "if (!selectedCitizen || chatSubmitting) return" in js
    assert "chatSubmitting = true" in js
    assert "chatSubmitting = false" in js
    assert 'els.chatForm.addEventListener("submit"' in js

    # Stage 1 visual profiles encode approved presentation canon without equipment truth.
    assert "CITIZEN_VISUAL_PROFILES" in js
    expected_aptitudes = {
        "aris": "extraction / prospecting",
        "bex": "fabrication",
        "cato": "logistics / resource planning",
        "iri": "construction",
        "noma": "research / experimentation",
        "vale": "generalist / cooperation",
    }
    for citizen_id, aptitude in expected_aptitudes.items():
        assert f"{citizen_id}:" in js
        assert f'canonical_aptitude: "{aptitude}"' in js
    for expression in ("neutral", "blink", "happy", "focused", "curious"):
        assert f"{expression}: null" in js
    assert 'silhouette: "heavy"' in js
    assert 'silhouette: "slim"' in js
    assert "equipment_layers: { rear: [], body: [], waist: [], held: [], foreground: [] }" in js
    assert "silhouette-heavy" in css
    assert "silhouette-slim" in css

    # Stage 1 still keeps visual identity presentation-only.
    assert "interface accent, not physical paint" in js
    assert "world_properties" not in js

    print("Agent City v0.8 Assets Stage 1 smoke test passed.")


if __name__ == "__main__":
    main()
