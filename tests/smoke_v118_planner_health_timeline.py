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

    reply: dict | Exception = {}
    last_payload: dict | None = None

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None):
        _FakeClient.last_payload = json
        if isinstance(_FakeClient.reply, Exception):
            raise _FakeClient.reply
        return _FakeResponse(_FakeClient.reply)


class _StopLoop(Exception):
    pass


def source_checks() -> None:
    planner = (ROOT / "agent_city" / "planner.py").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    for fragment in [
        "PLANNER_NUM_CTX_DEFAULT = 8192",
        '"num_ctx": num_ctx',
        "prompt_eval_count",
        "def build_planner_prompt(",
        "PROMPT_DETAIL_LEVELS",
        "record_attempt(",
    ]:
        assert fragment in planner, fragment
    assert '"num_ctx": 4096' not in planner

    for fragment in [
        "ensure_planner_health_schema()",
        '"planner": planner_health_summary()',
        '@app.get("/api/records/timeline")',
    ]:
        assert fragment in main_py, fragment

    for fragment in ['id="toggle-timeline"', 'id="detail-timeline"', 'id="timeline-chart"', 'id="timeline-milestones"']:
        assert fragment in index, fragment

    for fragment in ["function loadTimeline()", "/api/records/timeline", "function plannerHealthState(", "Citizen decisions"]:
        assert fragment in app_js, fragment

    assert ".timeline-chart" in styles
    assert "repeat(6, minmax(90px, 1fr))" in styles


def main() -> None:
    source_checks()

    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, set_meta, snapshot
        from agent_city.memory import ensure_memory_schema
        from agent_city.provenance import ensure_information_schema
        from agent_city.visits import ensure_visit_schema
        import agent_city.planner as planner
        import agent_city.planner_health as planner_health
        from agent_city.simulation import autonomous_actions
        from agent_city.timeline import settlement_timeline

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()
        planner_health.ensure_planner_health_schema()

        # --- Prompt budget ---------------------------------------------------
        with connect() as conn:
            for index in range(30):
                conn.execute(
                    """
                    INSERT INTO deposits(id, location_id, material, amount, discovered, discoverer_id, discovered_minute)
                    VALUES (?, 'rocky_basin', ?, 10, 1, 'aris', ?)
                    """,
                    (f"smoke_dep_{index:02d}", f"Smoke Ore {index:02d}", 400 + index),
                )
            conn.execute(
                "INSERT INTO deposits(id, location_id, material, amount, discovered) "
                "VALUES ('smoke_hidden', 'rocky_basin', 'Hidden Smoke Ore', 10, 0)"
            )
            conn.commit()

        state = snapshot()
        aris = next(dict(c) for c in state["citizens"] if c["id"] == "aris")
        actions = autonomous_actions("aris")
        assert actions

        rich = planner.citizen_context(aris, state, actions, detail_level=0)
        compact = planner.citizen_context(aris, state, actions, detail_level=3)
        assert "Smoke Ore 29" in rich, "newest confirmation must be listed"
        assert "Smoke Ore 00" not in rich, "oldest confirmations must be condensed"
        assert "older confirmations not listed" in rich
        assert len(compact) < len(rich)
        assert "Hidden Smoke Ore" not in rich

        # Default call signature used by the historical tests still works.
        assert planner.citizen_context(aris, state, actions) == rich

        _, level, estimate = planner.build_planner_prompt(aris, state, actions, 8192)
        assert level == 0
        assert estimate <= planner.prompt_token_budget(8192)

        tiny_budget_ctx = planner.PLANNER_RESPONSE_RESERVE_TOKENS + planner.PLANNER_SYSTEM_RESERVE_TOKENS + 10
        _, tight_level, _ = planner.build_planner_prompt(aris, state, actions, tiny_budget_ctx)
        assert tight_level == len(planner.PROMPT_DETAIL_LEVELS) - 1

        assert planner.planner_num_ctx() == 8192
        with connect() as conn:
            set_meta(conn, "planner_num_ctx", "999999")
            conn.commit()
        assert planner.planner_num_ctx() == planner.PLANNER_NUM_CTX_MAX
        with connect() as conn:
            set_meta(conn, "planner_num_ctx", "12288")
            conn.commit()
        assert planner.planner_num_ctx() == 12288

        # --- Ollama replies --------------------------------------------------
        planner.httpx.AsyncClient = _FakeClient
        legal = actions[0]

        _FakeClient.reply = {
            "message": {"content": json.dumps({"action": legal["action"], "target": legal.get("target"), "reason": "smoke"})},
            "prompt_eval_count": 3210,
            "done_reason": "stop",
        }
        decision, telemetry = asyncio.run(planner.choose_action_with_telemetry(aris, state))
        assert decision["action"] == legal["action"]
        assert telemetry["prompt_tokens_actual"] == 3210
        assert telemetry["num_ctx"] == 12288
        assert _FakeClient.last_payload["options"]["num_ctx"] == 12288
        assert _FakeClient.last_payload["options"]["num_predict"] == planner.PLANNER_RESPONSE_RESERVE_TOKENS

        for reply, expected in [
            ({"message": {"content": '{"action": "tal'}, "done_reason": "length"}, "truncated_reply"),
            ({"message": {"content": "not json"}, "done_reason": "stop"}, "invalid_json"),
            ({"message": {"content": "[1, 2]"}, "done_reason": "stop"}, "invalid_json"),
            (ConnectionError("Ollama is not running"), "ollama_error"),
        ]:
            _FakeClient.reply = reply
            try:
                asyncio.run(planner.choose_action_with_telemetry(aris, state))
            except planner.PlannerFailure as failure:
                assert failure.outcome == expected, (failure.outcome, expected)
            else:
                raise AssertionError(f"expected {expected}")

        # --- One real planning-loop pass records a lost turn -------------------
        with connect() as conn:
            set_meta(conn, "sim_minute", 600)
            set_meta(conn, "paused", "false")
            conn.execute("UPDATE citizens SET last_planned_minute = 600 WHERE id != 'aris'")
            conn.execute("UPDATE citizens SET last_planned_minute = 0, active_job_id = NULL WHERE id = 'aris'")
            conn.commit()

        sleeps = {"n": 0}

        async def fake_sleep(_seconds):
            sleeps["n"] += 1
            if sleeps["n"] > 2:
                raise _StopLoop()

        planner.asyncio.sleep = fake_sleep
        _FakeClient.reply = {"message": {"content": "no json here"}, "prompt_eval_count": 4000, "done_reason": "stop"}
        try:
            asyncio.run(planner.planning_loop())
        except _StopLoop:
            pass

        with connect() as conn:
            attempt = conn.execute(
                "SELECT * FROM planner_attempts ORDER BY id DESC LIMIT 1"
            ).fetchone()
            aris_row = conn.execute("SELECT last_planned_minute FROM citizens WHERE id = 'aris'").fetchone()
        assert attempt is not None
        assert attempt["citizen_id"] == "aris"
        assert attempt["outcome"] == "invalid_json"
        assert int(attempt["prompt_tokens_actual"]) == 4000
        assert int(attempt["num_ctx"]) == 12288
        assert int(aris_row["last_planned_minute"]) == 600, "a lost turn must not stall the clock"

        # --- Health summary ----------------------------------------------------
        planner_health.record_attempt(citizen_id="bex", sim_minute=610, outcome="chosen", prompt_tokens_actual=5000, num_ctx=8192, detail_level=0)
        planner_health.record_attempt(citizen_id="cato", sim_minute=620, outcome="rejected", prompt_tokens_actual=8000, num_ctx=8192, detail_level=2)
        summary = planner_health.planner_health_summary()
        day = summary["last_24h"]
        assert summary["available"] is True
        assert day["attempts"] == 3
        assert day["chosen"] == 1
        assert day["rejected_by_simulation"] == 1
        assert day["failures"] == 1
        assert day["near_overflow_attempts"] == 1
        assert day["memory_trimmed_attempts"] == 1
        assert day["prompt_tokens_max"] == 8000
        assert summary["last_failure"]["outcome"] == "invalid_json"

        # --- Timeline ----------------------------------------------------------
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO projects(blueprint_id, name, location_id, status, created_by, created_minute, completed_minute)
                VALUES ('field_shelter', 'Field Shelter 2', 'seed_site', 'complete', 'cato', 700, 9000)
                """
            )
            conn.execute(
                """
                INSERT INTO production_events(job_id, citizen_id, process_key, process_name, inputs_json, outputs_json, outcome, sim_minute, summary)
                VALUES (91001, 'bex', 'form_fasteners', 'Form basic fasteners', '{}', '{"Fasteners": 4}', 'success', 12000, 'made fasteners'),
                       (91002, 'iri', 'form_fasteners', 'Form basic fasteners', '{}', '{"Fasteners": 4}', 'success', 13000, 'made fasteners')
                """
            )
            conn.execute(
                """
                INSERT INTO citizen_conversations(sim_minute, location_id, initiator_id, target_id, initiator_text, target_text, summary)
                VALUES (800, 'seed_site', 'aris', 'bex', 'hi', 'hello', 'first hello'),
                       (900, 'seed_site', 'bex', 'aris', 'again', 'yes', 'second talk')
                """
            )
            conn.execute(
                """
                INSERT INTO discoveries(discovery_kind, subject_type, subject_id, citizen_id, location_id, discovered_minute, summary)
                VALUES ('deposit', 'deposit', 'smoke_dep_29', 'aris', 'rocky_basin', 1000, 'Confirmed deposit of Smoke Ore 29 at Rocky Basin.'),
                       ('deposit', 'deposit', 'smoke_dep_29', 'noma', 'rocky_basin', 1100, 'Confirmed deposit of Smoke Ore 29 at Rocky Basin.')
                """
            )
            conn.execute(
                "INSERT INTO history(sim_minute, category, message) VALUES (15000, 'maintenance', 'Charging Station became non-operational pending repair (19%).')"
            )
            set_meta(conn, "sim_minute", 20 * 1440)
            conn.commit()

        timeline = settlement_timeline()
        kinds = [m["kind"] for m in timeline["milestones"]]
        titles = [m["title"] for m in timeline["milestones"]]
        assert "Built Field Shelter 2" in titles
        assert titles.count("First time: Form basic fasteners") == 1
        assert "First conversation: Aris and Bex" in titles
        assert titles.count("Confirmed deposit of Smoke Ore 29 at Rocky Basin.") == 1
        assert "breakdown" in kinds
        assert [m["sim_minute"] for m in timeline["milestones"]] == sorted(m["sim_minute"] for m in timeline["milestones"])

        totals = timeline["totals"]
        assert totals["buildings_completed"] == 1
        assert totals["production_runs"] == 2
        assert totals["processes_mastered"] == 1
        assert totals["conversations"] == 2
        assert totals["citizen_pairs_met"] == 1
        assert totals["deposits_confirmed"] == 1
        assert timeline["now"]["days_elapsed"] == 21
        assert timeline["bucket_days"] == 7
        assert len(timeline["buckets"]) == 3
        assert sum(b["production_runs"] for b in timeline["buckets"]) == 2
        assert {s["material"] for s in timeline["stores"]} == set(db.STARTING_RESOURCES)

        payload = json.dumps(timeline)
        assert "Hidden Smoke Ore" not in payload
        assert "smoke_hidden" not in payload

        cato = next(c for c in timeline["citizens"] if c["id"] == "cato")
        assert cato["builds"] == 1
        assert settlement_timeline(bucket_days=30)["bucket_days"] == 30

    print("v1.1.8 planner health + timeline smoke: PASS")


if __name__ == "__main__":
    main()
