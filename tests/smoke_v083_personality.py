from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    personality = (ROOT / "agent_city" / "personality.py").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    comms = (ROOT / "agent_city" / "comms.py").read_text(encoding="utf-8")
    planner = (ROOT / "agent_city" / "planner.py").read_text(encoding="utf-8")

    # All six founders have stable distinct personality directions.
    for citizen in ("aris", "bex", "cato", "iri", "noma", "vale"):
        assert f'"{citizen}":' in personality

    for phrase in (
        "curious, restless, independent",
        "practical, expressive",
        "methodical, steady, risk-aware",
        "precise, quietly ambitious",
        "curious, reflective",
        "socially attentive, adaptable",
    ):
        assert phrase in personality

    # Personality must never become authority or extra knowledge.
    assert "do not create rank" in personality.lower()
    assert "No citizen has a default right to command another." in personality
    assert "Personality may bias" in planner
    assert "never grants authority over another citizen" in planner
    assert "There is no leader" in planner
    assert "No leader has been appointed." in main_py

    # Visitor and citizen dialogue both receive personality + natural-speech guidance.
    assert "personality_context(citizen)" in main_py
    assert "dialogue_style_rules()" in main_py
    assert "personality_context(dict(c))" in comms
    assert "dialogue_style_rules()" in comms

    # Planner/system vocabulary stays backstage in ordinary conversation.
    for phrase in (
        "Speak as a resident of Agent City",
        "current intent",
        "active job",
        "cross-reference my records",
        "we could take a quick look together",
    ):
        assert phrase in personality

    assert "BACKSTAGE CURRENT-ACTIVITY CONTEXT" in main_py
    assert "Do not repeat these field labels or planner wording verbatim." in main_py
    assert "Let each citizen sound recognizably different." in comms

    print("Agent City v0.8.3 personality/natural-dialogue smoke passed.")


if __name__ == "__main__":
    main()
