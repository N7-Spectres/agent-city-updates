from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    assert 'let citizenDetailView = localStorage.getItem("agentCityCitizenDetailView") || "continuity";' in app
    assert 'localStorage.setItem("agentCityCitizenDetailView", citizenDetailView);' in app
    assert 'window.openCitizenDetail = function(view)' in app

    assert 'function citizenContinuityMarkup(citizenId, section = "continuity")' in app
    for section in ("memories", "experience", "patterns"):
        assert f'if (section === "{section}")' in app

    assert 'class="citizen-sheet-dashboard"' in app
    assert 'class="citizen-overview-column"' in app
    assert '<span class="sheet-label">Physical state</span>' in app
    assert '<span class="sheet-label">Long-term maintenance</span>' in app
    assert '<span class="sheet-label">Cargo</span>' in app
    assert '<span class="sheet-label">Equipped gear</span>' in app
    assert '<span class="sheet-label">Projects</span>' in app
    assert '<span class="sheet-label">Active plan</span>' in app

    assert 'class="citizen-detail-nav"' in app
    for key, label in (
        ("continuity", "Continuity"),
        ("memories", "Memories"),
        ("experience", "Experience"),
        ("patterns", "Patterns & Places"),
        ("social", "Social"),
        ("knowledge", "Knowledge"),
    ):
        assert f'["{key}", "{label}"' in app

    assert 'class="citizen-detail-tab ${citizenDetailView === key ? "active" : ""}"' in app
    assert 'aria-pressed="${citizenDetailView === key ? "true" : "false"}"' in app
    assert 'class="citizen-detail-panel"' in app
    assert 'class="citizen-detail-content">${detail.markup}</div>' in app

    assert 'grid-template-columns: minmax(0, 1.45fr) minmax(340px, .85fr);' in css
    assert '.citizen-info-column {' in css
    assert 'position: sticky;' in css
    assert 'max-height: min(67vh, 760px);' in css
    assert '@media (max-width: 1100px)' in css
    assert '@media (max-width: 760px)' in css
    assert 'overflow-x: auto;' in css

    print("Agent City v0.9.3 citizen-sheet navigation smoke passed.")


if __name__ == "__main__":
    main()
