from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    # DOM wiring should remain internally consistent.
    html_ids = set(re.findall(r'id="([^"]+)"', html))
    js_ids = set(re.findall(r'getElementById\("([^"]+)"\)', js))
    assert js_ids <= html_ids, sorted(js_ids - html_ids)
    assert len(html_ids) == len(re.findall(r'id="([^"]+)"', html)), "duplicate HTML IDs"

    # v0.5 Visit/History UX.
    assert "chat-log" in html
    assert "visit-history-panel" in html
    assert "toggle-history" in html
    assert "History" in html
    assert "overflow-y" in css
    assert "max-height" in css or "height:" in css

    # v0.5 Making view must consume authoritative Simulation collections.
    assert "Making" in html
    for token in ("state.projects", "state.project_materials", "state.equipment", "state.structures"):
        assert token in js, token

    # Conversation History must use real stored conversation identity/source anchors.
    assert "source_job_id" in js
    assert "conversation #" in js.lower() or "conversation #" in html.lower() or "conversation #" in css.lower()

    print("Agent City v0.5 UI integration smoke test passed.")


if __name__ == "__main__":
    main()
