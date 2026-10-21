from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.db as db


class _FakeResponse:
    def __init__(self, body: dict):
        self._body = body

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._body


class _FakeClient:
    """Stands in for httpx.AsyncClient so no real Ollama is needed."""

    queue: list[dict] = []
    payloads: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None):
        _FakeClient.payloads.append(json)
        if not _FakeClient.queue:
            raise AssertionError("fake Ollama queue exhausted")
        return _FakeResponse(_FakeClient.queue.pop(0))


def _section(prompt: str, start: str, end: str) -> str:
    return prompt[prompt.index(start):prompt.index(end)]


def source_checks() -> None:
    comms = (ROOT / "agent_city" / "comms.py").read_text(encoding="utf-8")
    for fragment in [
        "DIALOGUE_NUM_CTX_DEFAULT = 8192",
        "def dialogue_num_ctx(",
        "def build_dialogue_prompt(",
        "DIALOGUE_DETAIL_LEVELS",
        "def _share_repeated_lines(",
        '"num_ctx": num_ctx',
        "prompt_eval_count",
        "prompt_window_overflow",
        "claim_prompt_over_budget",
    ]:
        assert fragment in comms, fragment
    assert '"num_ctx": 4096' not in comms
    assert '"num_ctx": 2048' not in comms


def main() -> None:
    source_checks()

    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        import agent_city.comms as comms
        from agent_city.db import connect, init_db, set_meta
        from agent_city.memory import ensure_memory_schema
        from agent_city.provenance import ensure_information_schema
        from agent_city.talk_diagnostics import ensure_talk_diagnostic_schema, talk_diagnostics_for
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()
        ensure_talk_diagnostic_schema()

        def build(num_ctx: int):
            return comms.build_dialogue_prompt(
                initiator_id="aris",
                target_id="bex",
                initiator_name="Aris",
                target_name="Bex",
                purpose="Compare what we have each seen.",
                location_name="Seed Site",
                now=600,
                num_ctx=num_ctx,
            )

        # --- A new city already needed more than the old 4,096 window ---------
        prompt, level, estimate = build(8192)
        assert level == 0
        assert estimate <= comms.dialogue_prompt_token_budget(8192)
        assert estimate > 4096, "the old 4,096 window really was too small"

        # Rules are never cut: every rule line is still present word for word.
        for rule_header in ["INFORMATION RULES:", "SUMMARY TRUTH RULES:"]:
            assert rule_header in prompt
        rich_unshared = comms._dialogue_prompt_text(
            initiator_name="Aris",
            target_name="Bex",
            initiator_context=comms._citizen_private_context("aris", "bex"),
            target_context=comms._citizen_private_context("bex", "aris"),
            purpose="Compare what we have each seen.",
            location_name="Seed Site",
            now=600,
        )
        tail_start = rich_unshared.index("Why Aris chose to speak:")
        assert prompt.endswith(rich_unshared[tail_start:]), "shared rules must be identical"
        assert len(prompt) < len(rich_unshared), "repeated rule lines should be stated once"

        # Shared-line pointers only point at lines Aris's packet really contains,
        # under the same heading, and Bex's own lines are kept.
        aris_ctx = comms._citizen_private_context("aris", "bex")
        bex_ctx = comms._citizen_private_context("bex", "aris")
        bex_shared = comms._share_repeated_lines("ARIS", aris_ctx, bex_ctx)
        assert "word for word, as in ARIS's" in bex_shared
        assert "Name: Bex" in bex_shared
        assert "talk target=aris" in bex_shared, "Bex's own differing actions stay listed"
        kept = set(bex_shared.splitlines())
        aris_lines = set(aris_ctx.splitlines())
        for line in bex_ctx.splitlines():
            assert line in kept or (line in aris_lines and len(line) >= comms.SHARED_LINE_MIN_CHARS), line

        # --- A busy city condenses older memories, never other citizens' -----
        with connect() as conn:
            for owner in ("aris", "bex"):
                for index in range(30):
                    conn.execute(
                        """
                        INSERT INTO deposits(id, location_id, material, amount, discovered, discoverer_id, discovered_minute)
                        VALUES (?, 'rocky_basin', ?, 10, 1, ?, ?)
                        """,
                        (f"{owner}_dep_{index:02d}", f"{owner.title()} Ore {index:02d}", owner, 400 + index),
                    )
            conn.execute(
                "INSERT INTO deposits(id, location_id, material, amount, discovered) "
                "VALUES ('smoke_hidden', 'rocky_basin', 'Hidden Smoke Ore', 10, 0)"
            )
            long_summary = "Aris and Bex discussed the basin route at length. " * 12
            for index in range(12):
                conn.execute(
                    """
                    INSERT INTO citizen_conversations(sim_minute, location_id, initiator_id, target_id, initiator_text, target_text, summary)
                    VALUES (?, 'seed_site', 'aris', 'bex', 'hi', 'hello', ?)
                    """,
                    (500 + index, f"Talk {index:02d}: {long_summary}"),
                )
            conn.commit()

        rich_aris = comms._citizen_private_context("aris", "bex", detail_level=0)
        compact_aris = comms._citizen_private_context("aris", "bex", detail_level=3)
        assert "Aris Ore 29" in rich_aris, "newest confirmation must be listed"
        assert "Aris Ore 00" not in rich_aris, "oldest confirmations are condensed"
        assert "older confirmations not listed" in rich_aris
        assert len(compact_aris) < len(rich_aris)
        assert "…" in rich_aris, "very long memory lines are clamped"
        assert comms._citizen_private_context("aris", "bex") == rich_aris

        prompt, level, estimate = build(8192)
        aris_part = _section(prompt, "ARIS PRIVATE KNOWLEDGE:", "BEX PRIVATE KNOWLEDGE:")
        bex_part = _section(prompt, "BEX PRIVATE KNOWLEDGE:", "Why Aris chose to speak:")
        assert "Hidden Smoke Ore" not in prompt
        assert "Bex Ore" not in aris_part, "Aris must not see Bex's discoveries"
        assert "Aris Ore" not in bex_part, "Bex must not see Aris's discoveries"
        assert "Talk 11" in aris_part, "Aris took part in that talk"
        # Bex took part in the same talks, so Bex's identical memory lines
        # point back to Aris's packet instead of repeating them.
        assert "Talk 11" in bex_part or "word for word, as in ARIS's Recent face-to-face" in bex_part

        # A tight window drops to a more compact level instead of overflowing.
        tight_ctx = estimate + comms.DIALOGUE_RESPONSE_RESERVE_TOKENS - 200
        _, tight_level, tight_estimate = build(tight_ctx)
        assert tight_level > level
        assert tight_estimate < estimate
        _, floor_level, _ = build(comms.DIALOGUE_RESPONSE_RESERVE_TOKENS + 10)
        assert floor_level == len(comms.DIALOGUE_DETAIL_LEVELS) - 1

        # --- Window setting --------------------------------------------------
        assert comms.dialogue_num_ctx() == 8192
        with connect() as conn:
            set_meta(conn, "planner_num_ctx", "12288")
            conn.commit()
        assert comms.dialogue_num_ctx() == 12288, "talk follows the planner window by default"
        with connect() as conn:
            set_meta(conn, "dialogue_num_ctx", "999999")
            conn.commit()
        assert comms.dialogue_num_ctx() == comms.DIALOGUE_NUM_CTX_MAX
        with connect() as conn:
            set_meta(conn, "dialogue_num_ctx", "1024")
            conn.commit()
        assert comms.dialogue_num_ctx() == comms.DIALOGUE_NUM_CTX_MIN
        with connect() as conn:
            set_meta(conn, "dialogue_num_ctx", "")
            conn.commit()

        # --- Ollama requests use the budgeted window ----------------------------
        comms.httpx.AsyncClient = _FakeClient
        exchange = {
            "initiator_text": "I logged the basin route earlier.",
            "target_text": "Then let's compare notes when we're both back.",
            "summary": "Aris and Bex talked about the basin route.",
        }
        telemetry = {"num_ctx": 12288, "detail_level": 0, "prompt_tokens_estimate": 5000, "prompt_tokens_actual": None}
        _FakeClient.queue = [{"message": {"content": json.dumps(exchange)}, "prompt_eval_count": 4321}]
        _FakeClient.payloads = []
        result = asyncio.run(
            comms._generate_raw_exchange(model="test", prompt="hi", source_job_id=9101, telemetry=telemetry)
        )
        assert result["summary"] == exchange["summary"]
        assert _FakeClient.payloads[0]["options"]["num_ctx"] == 12288
        assert _FakeClient.payloads[0]["messages"][0]["content"] == comms.DIALOGUE_SYSTEM_MESSAGE
        assert telemetry["prompt_tokens_actual"] == 4321
        codes = [(d["outcome"], d["code"]) for d in talk_diagnostics_for(9101)]
        assert ("success", "dialogue_generated") in codes
        assert ("degraded", "prompt_window_overflow") not in codes
        success = next(d for d in talk_diagnostics_for(9101) if d["code"] == "dialogue_generated")
        assert "12288-token window" in success["detail"] and "4321" in success["detail"]

        # If Ollama still reports a full window, the overflow is recorded, not silent.
        telemetry = {"num_ctx": 8192, "detail_level": 3, "prompt_tokens_estimate": 8000, "prompt_tokens_actual": None}
        _FakeClient.queue = [{"message": {"content": json.dumps(exchange)}, "prompt_eval_count": 8192}]
        asyncio.run(comms._generate_raw_exchange(model="test", prompt="hi", source_job_id=9102, telemetry=telemetry))
        codes = [(d["outcome"], d["code"]) for d in talk_diagnostics_for(9102)]
        assert ("degraded", "prompt_window_overflow") in codes

        # Claim extraction uses the same window (no model reload between steps).
        _FakeClient.queue = [{"message": {"content": json.dumps({"claims": []})}}]
        _FakeClient.payloads = []
        asyncio.run(
            comms._extract_claims_best_effort(
                model="test", source_job_id=9103, conversation_id=1,
                initiator_text="hi", target_text="hello",
            )
        )
        assert _FakeClient.payloads[0]["options"]["num_ctx"] == comms.dialogue_num_ctx()
        assert _FakeClient.payloads[0]["options"]["num_predict"] == comms.CLAIM_RESPONSE_RESERVE_TOKENS

        # An oversized claim prompt is skipped instead of being cut by Ollama.
        _FakeClient.queue = []
        _FakeClient.payloads = []
        asyncio.run(
            comms._extract_claims_best_effort(
                model="test", source_job_id=9104, conversation_id=1,
                initiator_text="word " * 20000, target_text="hello",
            )
        )
        assert _FakeClient.payloads == []
        codes = [(d["outcome"], d["code"]) for d in talk_diagnostics_for(9104)]
        assert ("degraded", "claim_prompt_over_budget") in codes

    print("v1.1.10 dialogue prompt budget smoke: PASS")


if __name__ == "__main__":
    main()
