from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

UNSAFE = ("validated", "confirmed", "verified", "proved", "proven", "demonstrated", "established")


def is_claim_safe(summary: str) -> bool:
    text = str(summary or "").lower()
    return not any(re.search(rf"\\b{re.escape(term)}\\b", text) for term in UNSAFE)


def main() -> None:
    comms = (ROOT / "agent_city" / "comms.py").read_text(encoding="utf-8")

    # Ordinary social-summary language remains allowed.
    for text in (
        "Iri reported carrying twenty units of Native Resin.",
        "Noma and Cato compared their observations and agreed to recharge.",
        "Vale said she had seen plant fiber near the resin plants.",
        "They planned to inspect the area together.",
    ):
        assert is_claim_safe(text), text

    # A conversation source may not upgrade claims into physical verification.
    for text in (
        "They validated the deposit.",
        "Cato confirmed Vale's report.",
        "Noma verified the material.",
        "They proved the claim.",
        "The result was demonstrated.",
        "The fact was established.",
    ):
        assert not _summary_is_claim_safe(text), text

    fallback = "The citizens exchanged reports and discussed possible next steps; the conversation itself does not verify any physical claim."
    assert is_claim_safe(fallback)
    assert "does not verify any physical claim" in fallback

    # Prompt contract must explicitly protect intent vs physical completion.
    assert "SUMMARY TRUTH RULES:" in comms
    assert "The summary describes communication, not physical verification." in comms
    assert "An agreement to inspect, travel, recharge, build, or test remains an intention" in comms
    assert "summary_claim_upgrade" in comms

    print("Agent City v0.8.4 claim-safe conversation summary smoke passed.")


if __name__ == "__main__":
    main()
