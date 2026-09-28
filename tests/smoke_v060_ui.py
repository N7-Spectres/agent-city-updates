from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    html_ids = re.findall(r'id="([^"]+)"', html)
    js_ids = set(re.findall(r'getElementById\("([^"]+)"\)', js))
    assert len(html_ids) == len(set(html_ids)), "duplicate HTML IDs"
    assert js_ids <= set(html_ids), sorted(js_ids - set(html_ids))

    # v0.6 information architecture.
    for label in ("Home", "Citizens", "Locations", "Records"):
        assert label in html, label
    assert "citizen-sheet" in html
    assert "location-sheet" in html
    assert "visitor-map-status" in html

    # Bounded knowledge comes from safe APIs, not hidden world truth.
    assert "/api/knowledge/citizens/" in js
    assert "/api/knowledge/locations/" in js
    assert "world_properties" not in js
    assert "known_facts" in js
    assert "state.experiment_results" in js
    assert "state.learned_processes" in js

    # Structured visit status is consumed by the UI.
    assert "data.availability" in js
    assert "citizen_talking" in js
    assert "citizen_busy" in js

    # Authoritative cargo capacity is supplied by backend state, not derived in JS.
    assert "cargo_capacity" in main_py
    assert "citizen.cargo_capacity" in js

    # Main runtime exposes both lower-level provenance and bounded Memory read models.
    assert '/api/knowledge/{citizen_id}' in main_py
    assert '/api/knowledge/citizens/{citizen_id}' in main_py
    assert '/api/knowledge/locations/{location_id}' in main_py
    assert "ensure_information_schema()" in main_py

    # Basic bounded layout/visual shell remains present.
    assert "overflow" in css
    assert "location-scene-slot" in css
    assert "identity-slot" in css

    print("Agent City v0.6 assembled UI/integration smoke test passed.")


if __name__ == "__main__":
    main()
