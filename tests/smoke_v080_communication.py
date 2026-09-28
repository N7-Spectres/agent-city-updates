from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


class FakeResponse:
    def __init__(self, text: str):
        self._text = text

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {"message": {"content": self._text}}


class CaptureAsyncClient:
    payloads: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json=None, **kwargs):
        self.payloads.append(json or {})
        return FakeResponse(
            "That sounds worth examining. I can discuss what you're seeing, "
            "but I haven't validated the feature or started a physical action."
        )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.comms import _citizen_private_context
        from agent_city.db import connect, init_db, snapshot
        from agent_city.grounding import (
            citizen_capability_context,
            citizen_capability_payload,
            grounding_policy_text,
            settlement_store_context,
        )
        from agent_city.memory import ensure_memory_schema
        from agent_city.planner import citizen_context
        from agent_city.provenance import ensure_information_schema
        from agent_city.simulation import possible_actions
        from agent_city.talk_diagnostics import ensure_talk_diagnostic_schema
        from agent_city.visitors import ensure_visitor
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()
        ensure_talk_diagnostic_schema()

        # Physical capability comes only from runtime state.
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO equipment
                (template_id, name, kind, owner_citizen_id, location_id, condition,
                 extraction_speed_multiplier, cargo_bonus, created_job_id, created_minute)
                VALUES ('field_probe', 'Field Probe', 'analysis', 'aris', 'seed_site',
                        100, 1.0, 0, 9001, 500)
                """
            )
            conn.execute(
                """
                INSERT INTO equipment
                (template_id, name, kind, owner_citizen_id, location_id, condition,
                 extraction_speed_multiplier, cargo_bonus, created_job_id, created_minute)
                VALUES ('broken_probe', 'Broken Probe', 'analysis', 'aris', 'seed_site',
                        10, 1.0, 0, 9002, 500)
                """
            )
            conn.commit()

        payload = citizen_capability_payload("aris")
        equipment_names = {item["name"] for item in payload["equipment"]}
        assert "Field Probe" in equipment_names
        assert "Broken Probe" not in equipment_names
        assert "Jetpack" not in equipment_names

        capability_text = citizen_capability_context("aris")
        assert "AUTHORITATIVE CAPABILITY SURFACE" in capability_text
        assert "Field Probe" in capability_text
        # Broken Probe may appear in the legal service-action list, but must not
        # appear in the operational equipment subsection.
        operational_section = capability_text.split(
            "Operational structures at your current location:", 1
        )[0]
        assert "Broken Probe" not in operational_section
        assert "Concept art" in capability_text

        # Current Seed Site inventory may be observed locally, but is not a live
        # remote feed after the citizen leaves.
        local_store = settlement_store_context("aris")
        assert "Seed Site current storage:" in local_store
        assert "Processed structural material" in local_store

        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'resin_grove', location = 'Resin Grove',
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'aris'
                """
            )
            conn.commit()

        remote_store = settlement_store_context("aris")
        assert "away from Seed Site" in remote_store
        assert "Processed structural material" not in remote_store
        assert "120" not in remote_store

        # Grounding vocabulary explicitly separates claims/hypotheses/actions.
        visitor_rules = grounding_policy_text(visitor_facing=True)
        assert "KNOWN FACT" in visitor_rules
        assert "CURRENT OBSERVATION" in visitor_rules
        assert "REPORTED CLAIM" in visitor_rules
        assert "HYPOTHESIS / PROPOSAL" in visitor_rules
        assert "VALIDATED CAPABILITY / ACTION" in visitor_rules
        assert "economic/market value" in visitor_rules
        assert "visitor-reported" in visitor_rules
        assert "do NOT say walking" in visitor_rules
        assert "concept art" in visitor_rules

        # Autonomous citizen context also receives authoritative capability
        # grounding rather than visual/concept-art assumptions.
        private_context = _citizen_private_context("aris")
        assert "AUTHORITATIVE CAPABILITY SURFACE" in private_context
        assert "Field Probe" in private_context
        assert "Broken Probe" not in private_context

        # Planner reasons are prohibited from inventing properties/value/weather.
        state = snapshot()
        aris = next(c for c in state["citizens"] if c["id"] == "aris")
        actions = possible_actions("aris")
        planner_prompt = citizen_context(aris, state, actions)
        assert "market/economic value" in planner_prompt
        assert "weather/environment effects" in planner_prompt
        assert "A plausible explanation is still a hypothesis" in planner_prompt

        # Visitor chat receives the Stage 1 grounding contract. Visitor prose
        # remains the user's message, never converted into system-confirmed fact.
        ensure_visitor("N7")
        with connect() as conn:
            conn.execute(
                """
                UPDATE visitor_presence
                SET location_id = 'resin_grove',
                    from_location_id = NULL,
                    to_location_id = NULL,
                    travel_start_minute = NULL,
                    travel_end_minute = NULL
                WHERE visitor = 'N7'
                """
            )
            conn.commit()

        import main as app_module

        original_client = app_module.httpx.AsyncClient
        CaptureAsyncClient.payloads = []
        app_module.httpx.AsyncClient = CaptureAsyncClient
        try:
            req = app_module.TalkRequest(
                visitor="N7",
                citizen_id="aris",
                message=(
                    "I see a crystal spire here, this ore looks extremely valuable, "
                    "and I want us to walk one meter north and scan it with the jetpack."
                ),
            )
            result = asyncio.run(app_module.talk(req))
            assert result["message"]

            assert CaptureAsyncClient.payloads
            messages = CaptureAsyncClient.payloads[0]["messages"]
            system_text = messages[0]["content"]
            assert "VISITOR ROLEPLAY GROUNDING" in system_text
            assert "AUTHORITATIVE CAPABILITY SURFACE" in system_text
            assert "visitor-reported" in system_text
            assert "concept art" in system_text
            assert "shared visitor activity" in system_text
            assert "Seed Site current storage:" not in system_text
            assert "Processed structural material: 120" not in system_text
            assert messages[-1]["role"] == "user"
            assert "crystal spire" in messages[-1]["content"]
            assert "jetpack" in messages[-1]["content"]
        finally:
            app_module.httpx.AsyncClient = original_client

        print("Agent City v0.8 Stage 1 communication grounding smoke test passed.")


if __name__ == "__main__":
    main()
