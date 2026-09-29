from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    # Stage 3 UI consumes the owner-scoped Memory read model directly.
    assert "/api/memory/patterns/" in app
    assert app.count("/api/memory/patterns/") == 1
    assert '@app.get("/api/memory/patterns/{citizen_id}")' in main_py
    assert "const patterns = await patternsResponse.json();" in app
    assert "patterns, planMemories" in app

    continuity = app[
        app.index("function citizenContinuityMarkup"):
        app.index("function knowledgeFactMarkup")
    ]

    # Keep the existing three-layer continuity grammar.
    assert "Evidence / Record" in continuity
    assert "Remembered Perspective" in continuity
    assert "Citizen Interpretation" in continuity

    # Stage 3 uses evidence wording, not identity labels.
    assert "Recurring choice evidence" in continuity
    assert "Place continuity" in continuity
    assert "Social pattern evidence" in continuity
    assert "source-backed evidence states, not traits or preferences" in continuity
    assert "Personal continuity evidence only." in continuity
    assert "Owner-perspective social evidence only." in continuity
    assert "not an authoritative tradition or culture fact" in continuity

    # Current/mixed/fading are rendered as neutral evidence state text only.
    assert "continuity-evidence-state" in continuity
    assert '${escapeHtml(evidenceState)} evidence' in continuity
    assert "support_count" in continuity
    assert "distinct_days" in continuity
    assert "support_sources" in continuity
    assert "recent_contrary_sources" in continuity

    # Place continuity renders retained source history and never computes affinity.
    assert "evidence_count" in continuity
    assert "Place evidence trail" in continuity
    assert "favorite, home, safe, or sacred place" in continuity
    for forbidden in (
        "affinity",
        "favorite_place",
        "place_score",
        "attachment_score",
    ):
        assert forbidden not in continuity.lower(), forbidden

    # Social-pattern candidates show provenance/verification rather than culture truth.
    assert "distinct_actors" in continuity
    assert "transmission_modes" in continuity
    assert "verification_states" in continuity
    assert "Social source trail" in continuity
    assert "Verification represented:" in continuity

    # No Stage 3 threshold or scoring logic is recreated in JavaScript.
    for forbidden in (
        "habit_min_support",
        "custom_min_evidence",
        "habit_strength",
        "preference_score",
        "culture_score",
        "tradition_score",
        "support_count >=",
        "distinct_actors.length >=",
        "distinct_days >=",
    ):
        assert forbidden not in continuity.lower(), forbidden

    # No identity/ranking presentation is introduced.
    for forbidden in (
        "habit badge",
        "favorite-place badge",
        "tradition badge",
        "culture badge",
        "leaderboard",
        "ranking",
        "personality score",
    ):
        assert forbidden not in continuity.lower(), forbidden

    # Stage 3 presentation remains quiet, card-like, and source-traceable.
    assert ".continuity-pattern-list" in css
    assert ".continuity-pattern-row" in css
    assert ".continuity-source-chip" in css
    assert ".continuity-place-event" in css
    assert ".continuity-social-source" in css
    assert ".continuity-evidence-state" in css
    assert ".habit-meter" not in css
    assert ".culture-meter" not in css
    assert ".preference-meter" not in css

    # Home stays untouched by the Stage 3 pattern endpoint.
    load_section = app[
        app.index("async function loadCitizenContinuity"):
        app.index("function continuityMemoryRow")
    ]
    assert "/api/memory/patterns/" in load_section

    print("Agent City v0.9 Stage 3 continuity Assets/UI smoke passed.")


if __name__ == "__main__":
    main()
