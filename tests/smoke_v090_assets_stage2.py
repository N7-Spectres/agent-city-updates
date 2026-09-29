from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    # Stage 1 continuity stays intact.
    assert "Evidence / Record" in app
    assert "Remembered Perspective" in app
    assert "Citizen Interpretation" in app
    assert "Ongoing plans" in app
    assert "Recorded practice" in app
    assert "Relevant memories" in app
    assert "/api/continuity/" in app
    assert "/api/memory/continuity/" in app

    # Stage 2 consumes the assembled Simulation read model directly.
    assert "/api/competence/" in app
    assert '@app.get("/api/competence/{citizen_id}")' in main_py
    assert "duration_reduction_percent" in app
    assert "guided_practice_sessions" in app
    assert "source_practice_event_ids" in main_py

    # The measured effect is factual text, not a proficiency visualization.
    assert "Measured work effect:" in app
    assert "shorter from prior practice" in app
    assert ".continuity-measured-effect" in css

    continuity = app[
        app.index("function citizenContinuityMarkup"):
        app.index("function knowledgeFactMarkup")
    ]
    for forbidden in (
        "weighted_evidence",
        "teacher_weighted_evidence",
        "learner_weighted_evidence",
        "evidence_gap",
        "guidance_duration_multiplier",
        "combined_duration_multiplier",
        "competence score",
        "proficiency bar",
        "mastery",
        "skill level",
    ):
        assert forbidden not in continuity.lower(), forbidden

    # Assets must not derive competence from counts or from the physical cap.
    assert "0.08" not in continuity
    assert "duration_multiplier" not in continuity
    assert "practice_count /" not in continuity
    assert "practice_count *" not in continuity

    # Guided-practice sessions stay event history with local roles.
    assert "Guided practice history" in app
    assert "Guided ${counterpart}" in app
    assert "Practiced with ${counterpart}" in app
    assert "mentor" not in continuity.lower()
    assert "trainer" not in continuity.lower()
    assert "expert badge" not in continuity.lower()

    # Internal session evidence counts are not surfaced.
    assert "teacher_practice_count" not in app
    assert "learner_practice_count" not in app
    assert "consumed_by_job_id" not in app

    # Memory remains the remembered-perspective source and ranking internals stay hidden.
    assert "continuity-memory-context" in app
    assert "source_role" in app
    assert '"counterparty"' in app
    assert '"competence_family"' in app
    assert "recall_score" not in app
    assert "reinforcement_count" not in app

    # Interpretation remains attributed/Communication-owned instead of being generated from counts.
    assert "Source-backed self-reflection remains Communication-owned and attributed." in app
    assert "Measured work effects and event counts are evidence" in app

    # No new top-level skill or ranking system.
    assert "leaderboard" not in app.lower()
    assert "heatmap" not in app.lower()
    assert "guidance buff" not in app.lower()

    # Styling stays quiet and card-like, with no competence meter selectors.
    assert ".continuity-practice-family" in css
    assert ".continuity-guided-row" in css
    assert ".continuity-memory-context" in css
    assert "competence-meter" not in css
    assert "skill-meter" not in css
    assert "mastery" not in css.lower()

    print("Agent City v0.9 Stage 2 continuity Assets/UI smoke passed.")


if __name__ == "__main__":
    main()
