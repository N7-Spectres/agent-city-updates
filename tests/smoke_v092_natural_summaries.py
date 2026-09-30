from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_city.comms import _naturalize_conversation_summary, _summary_is_claim_safe


def main() -> None:
    cases = (
        (
            "The initiator mentioned coordinating recharge logistics with Noma, who is currently present.",
            "Cato mentioned coordinating recharge logistics with Noma, who is currently present.",
        ),
        (
            "The target citizen agreed to wait for more information.",
            "Noma agreed to wait for more information.",
        ),
        (
            "The initiator, Cato, brought up checking the resin inventory.",
            "Cato brought up checking the resin inventory.",
        ),
        (
            "The initiator discussed source job #255 and the proposal state with the target.",
            "Cato discussed the conversation and the discussion with Noma.",
        ),
    )

    for raw, expected in cases:
        cleaned = _naturalize_conversation_summary(raw, "Cato", "Noma")
        assert cleaned == expected, (raw, cleaned)
        lowered = cleaned.lower()
        for forbidden in (
            "initiator",
            "target citizen",
            "conversation target",
            "source job",
            "action target",
            "proposal state",
        ):
            assert forbidden not in lowered, (forbidden, cleaned)
        assert _summary_is_claim_safe(cleaned)

    comms = (ROOT / "agent_city" / "comms.py").read_text(encoding="utf-8")
    assert "Write the summary for a human reader using {initiator_name} and {target_name} by name." in comms
    assert 'Never refer to either citizen as "the initiator"' in comms
    assert 'Never expose backend terms such as "source job"' in comms
    assert "{initiator_name.upper()} PRIVATE KNOWLEDGE:" in comms
    assert "{target_name.upper()} PRIVATE KNOWLEDGE:" in comms
    assert 'purpose = (reason or f"{initiator_name} wants to speak briefly.")' in comms

    print("Agent City v0.9.2 natural conversation-summary smoke passed.")


if __name__ == "__main__":
    main()
