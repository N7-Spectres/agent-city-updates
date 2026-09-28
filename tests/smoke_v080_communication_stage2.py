from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {
            "message": {
                "content": json.dumps(self._payload),
            }
        }


class FakeAsyncClient:
    queue: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        if not self.queue:
            raise AssertionError("FakeAsyncClient queue exhausted")
        return FakeResponse(self.queue.pop(0))


def make_exchange(visitor: str, citizen_id: str, visit_id: int, visitor_text: str, citizen_text: str) -> int:
    from agent_city.db import connect, get_meta

    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        cur = conn.execute(
            """
            INSERT INTO conversations
            (sim_minute, visitor, citizen_id, visitor_text, citizen_text, visit_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (now, visitor, citizen_id, visitor_text, citizen_text, visit_id),
        )
        conn.commit()
        return int(cur.lastrowid)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        import agent_city.shared_actions as shared
        from agent_city.db import connect, init_db, set_meta
        from agent_city.memory import ensure_memory_schema
        from agent_city.provenance import ensure_information_schema
        from agent_city.shared_actions import (
            accept_proposal,
            ensure_shared_action_schema,
            expire_pending_proposals_for_visitor,
            maybe_create_proposal_from_exchange,
            proposal_payload,
            proposals_for_visit,
            reject_proposal,
            shared_action_context,
            shared_action_option_context,
        )
        from agent_city.talk_diagnostics import ensure_talk_diagnostic_schema
        from agent_city.visitors import ensure_visitor
        from agent_city.visits import ensure_visit_schema, get_or_create_active_visit

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()
        ensure_talk_diagnostic_schema()
        ensure_shared_action_schema()

        visitor = "N7"
        citizen_id = "aris"
        ensure_visitor(visitor)

        with connect() as conn:
            set_meta(conn, "sim_minute", 1000)
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site',
                    location = 'Seed Site',
                    position_x_m = 0,
                    position_y_m = 0,
                    active_job_id = NULL,
                    current_activity = 'Available',
                    energy = 100
                WHERE id = ?
                """,
                (citizen_id,),
            )
            conn.execute(
                """
                UPDATE visitor_presence
                SET location_id = 'seed_site',
                    x_m = 0,
                    y_m = 0,
                    from_location_id = NULL,
                    to_location_id = NULL,
                    travel_start_minute = NULL,
                    travel_end_minute = NULL
                WHERE visitor = ?
                """,
                (visitor,),
            )
            visit = get_or_create_active_visit(conn, visitor, citizen_id, 1000)
            visit_id = int(visit["id"])
            conn.commit()

        visitor_text = "Let's walk five meters east together and inspect the ground there."
        citizen_text = "Yes, we could walk over together and inspect that point."
        exchange_id = make_exchange(
            visitor,
            citizen_id,
            visit_id,
            visitor_text,
            citizen_text,
        )

        original_options = shared.simulation_shared_action_options
        original_start = shared.simulation_start_shared_action
        original_status = shared.simulation_shared_action_status
        original_client = shared.httpx.AsyncClient

        safe_option = {
            "option_key": "walk_east_5m",
            "action_kind": "shared_walk_inspect",
            "label": "Walk 5 m east together and inspect the arrival point",
            "objective": "Move together to the supplied nearby point, then inspect it.",
            "frame_id": "seed_site_local",
            "target_x_m": 5.0,
            "target_y_m": 0.0,
            "target_subject_type": "coordinate",
            "target_subject_id": None,
            "requested_tool_id": None,
        }

        try:
            # No Simulation legal option means dialogue cannot mint a proposal.
            shared.simulation_shared_action_options = lambda v, c: []
            no_options_context = shared_action_option_context(visitor, citizen_id)
            assert "none currently exposed" in no_options_context
            none = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange_id,
                    visitor_text=visitor_text,
                    citizen_text=citizen_text,
                    model="test-model",
                )
            )
            assert none is None

            # With one safe Simulation option, the classifier can only select its
            # key. Target coordinates/capability are copied from Simulation.
            shared.simulation_shared_action_options = lambda v, c: [dict(safe_option)]
            option_context = shared_action_option_context(visitor, citizen_id)
            assert "walk_east_5m" in option_context
            assert "seed_site_local (5.00, 0.00) m" in option_context
            assert "not physically started" in option_context
            FakeAsyncClient.queue = [{"proposal_key": "walk_east_5m"}]
            shared.httpx.AsyncClient = FakeAsyncClient

            proposal = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange_id,
                    visitor_text=visitor_text,
                    citizen_text=citizen_text,
                    model="test-model",
                )
            )
            assert proposal is not None
            assert proposal["status"] == "proposed"
            assert proposal["acceptance_available"] is True
            assert proposal["action_kind"] == "shared_walk_inspect"
            assert proposal["target"]["frame_id"] == "seed_site_local"
            assert proposal["target"]["x_m"] == 5.0
            assert proposal["target"]["y_m"] == 0.0
            assert proposal["simulation_action_id"] is None

            context = shared_action_context(visitor, citizen_id, visit_id=visit_id)
            assert "pending visitor acceptance" in context
            assert "has NOT physically started" in context

            # Same durable exchange is idempotent and does not need another model call.
            FakeAsyncClient.queue = []
            same = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange_id,
                    visitor_text=visitor_text,
                    citizen_text=citizen_text,
                    model="test-model",
                )
            )
            assert same is not None
            assert same["id"] == proposal["id"]

            # Explicit visitor acceptance revalidates the option and only becomes
            # physically started when Simulation returns a real action ID.
            shared.simulation_start_shared_action = lambda p: {
                "ok": True,
                "available": True,
                "action_id": "shared_42",
                "status": "active",
                "progress": 0.0,
                "start_minute": 1001,
                "end_minute": 1006,
                "observation_ids": [],
            }

            ok, message, started = accept_proposal(proposal["id"], visitor)
            assert ok is True
            assert "Simulation started" in message
            assert started is not None
            assert started["status"] == "started"
            assert started["simulation_action_id"] == "shared_42"
            assert started["progress"] == 0.0

            context = shared_action_context(visitor, citizen_id, visit_id=visit_id)
            assert "ACTIVE" in context
            assert "shared_42" in context

            # Completion/result evidence enters only through Simulation status.
            shared.simulation_shared_action_status = lambda action_id: {
                "action_id": action_id,
                "status": "completed",
                "progress": 1.0,
                "start_minute": 1001,
                "end_minute": 1006,
                "observation_ids": [77],
                "outcome": "Participants arrived and completed a baseline field inspection.",
            }
            completed = proposal_payload(proposal["id"], sync=True)
            assert completed is not None
            assert completed["status"] == "completed"
            assert completed["observation_ids"] == [77]
            assert "baseline field inspection" in completed["outcome"]

            # A separate proposal can be explicitly rejected and never starts.
            exchange2 = make_exchange(
                visitor,
                citizen_id,
                visit_id,
                "We could walk east again if you want.",
                "I could, if you decide to.",
            )
            FakeAsyncClient.queue = [{"proposal_key": "walk_east_5m"}]
            proposal2 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange2,
                    visitor_text="We could walk east again if you want.",
                    citizen_text="I could, if you decide to.",
                    model="test-model",
                )
            )
            assert proposal2 is not None
            ok, message, rejected = reject_proposal(proposal2["id"], visitor)
            assert ok is True
            assert "No physical action was started" in message
            assert rejected is not None and rejected["status"] == "rejected"

            # Physical separation invalidates a still-pending proposal even when
            # a stale option list would otherwise contain the same key.
            exchange3 = make_exchange(
                visitor,
                citizen_id,
                visit_id,
                "Let's inspect that point together.",
                "We could do that.",
            )
            FakeAsyncClient.queue = [{"proposal_key": "walk_east_5m"}]
            proposal3 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange3,
                    visitor_text="Let's inspect that point together.",
                    citizen_text="We could do that.",
                    model="test-model",
                )
            )
            assert proposal3 is not None and proposal3["status"] == "proposed"

            with connect() as conn:
                conn.execute(
                    "UPDATE visitor_presence SET location_id = 'resin_grove', x_m = -1200, y_m = 0 WHERE visitor = ?",
                    (visitor,),
                )
                conn.commit()

            ok, _, expired = accept_proposal(proposal3["id"], visitor)
            assert ok is False
            assert expired is not None and expired["status"] == "expired"

            # Pending proposals can also be mass-expired when a visitor leaves/travels.
            with connect() as conn:
                conn.execute(
                    "UPDATE visitor_presence SET location_id = 'seed_site', x_m = 0, y_m = 0 WHERE visitor = ?",
                    (visitor,),
                )
                conn.commit()

            exchange4 = make_exchange(
                visitor,
                citizen_id,
                visit_id,
                "One more nearby walk?",
                "That is possible.",
            )
            FakeAsyncClient.queue = [{"proposal_key": "walk_east_5m"}]
            proposal4 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange4,
                    visitor_text="One more nearby walk?",
                    citizen_text="That is possible.",
                    model="test-model",
                )
            )
            assert proposal4 is not None
            expired_count = expire_pending_proposals_for_visitor(visitor)
            assert expired_count >= 1
            assert proposal_payload(proposal4["id"], sync=False)["status"] == "expired"

            visit_proposals = proposals_for_visit(visitor, citizen_id, visit_id=visit_id)
            assert any(item["id"] == proposal["id"] for item in visit_proposals)
            assert any(item["id"] == proposal2["id"] for item in visit_proposals)

            print("Agent City v0.8 Stage 2 Communication shared-action smoke test passed.")

        finally:
            shared.simulation_shared_action_options = original_options
            shared.simulation_start_shared_action = original_start
            shared.simulation_shared_action_status = original_status
            shared.httpx.AsyncClient = original_client


if __name__ == "__main__":
    main()
