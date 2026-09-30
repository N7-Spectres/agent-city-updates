from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    memory = (ROOT / "agent_city" / "causal_memory.py").read_text(encoding="utf-8")

    # Citizen continuity stays attached to the citizen sheet, now through
    # explicit on-demand detail views rather than one long stacked section.
    assert 'citizenContinuityMarkup(citizen.id, "continuity")' in app
    assert 'citizenContinuityMarkup(citizen.id, "memories")' in app
    assert 'citizenContinuityMarkup(citizen.id, "experience")' in app
    assert "Ongoing plans" in app
    assert "Recorded practice" in app
    assert "Relevant memories" in app

    # The visual grammar preserves the three truth layers instead of collapsing
    # history into a skill/reputation badge.
    assert "Evidence / Record" in app
    assert "Remembered Perspective" in app
    assert "Citizen Interpretation" in app
    assert "Not an objective stat" in app
    assert "does not infer expertise, rank, friendship" in app
    interpretation = app[
        app.index("Citizen Interpretation"):
        app.index("function knowledgeFactMarkup")
    ]
    assert "preference" in interpretation
    assert "favorite places" in interpretation
    assert "traditions" in interpretation

    # Objective continuity and active remembered perspective use separate sources.
    assert "/api/continuity/" in app
    assert "/api/memory/continuity/" in app
    assert '@app.get("/api/memory/continuity/{citizen_id}")' in main_py
    assert "def display_recall_snapshot(" in memory

    # Ordinary UI-safe projection must not return private ranking machinery.
    display_block = memory[memory.index("def display_recall_snapshot("):]
    assert '"recall_score"' not in display_block
    assert '"reinforcement_count"' not in display_block
    assert '"importance"' not in display_block
    assert '"pinned_by_plan"' in display_block
    assert '"verification"' in display_block
    assert '"source_type"' in display_block

    # No proficiency/XP visual is introduced by the continuity surface.
    continuity_block = app[app.index("function citizenContinuityMarkup"):app.index("function knowledgeFactMarkup")]
    assert "progress bar" not in continuity_block.lower()
    assert "level " not in continuity_block.lower()
    assert "xp " not in continuity_block.lower()
    assert "expert badge" not in continuity_block.lower()

    assert ".continuity-grid {" in css
    assert ".continuity-layer.remembered" in css
    assert ".continuity-layer.interpretation" in css

    print("Agent City v0.9 Stage 1 continuity Assets/UI smoke passed.")


if __name__ == "__main__":
    main()
