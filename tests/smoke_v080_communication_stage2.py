from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return {"message": {"content": json.dumps(self._payload)}}


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
            parse_explicit_relative_target,
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

        # Communication parses only explicit cardinal + meter intent.
        assert parse_explicit_relative_target("walk five meters east") == (5.0, 0.0)
        assert parse_explicit_relative_target("move 2 m north and 3 meters west") == (-3.0, 2.0)
        assert parse_explicit_relative_target("let's go over there") is None
        assert parse_explicit_relative_target("*points north* let's go") is None

        original_contract = shared._simulation_contract_available
        original_propose = shared.simulation_propose_shared_activity
        original_accept = shared.simulation_accept_shared_activity
        original_status = shared.simulation_shared_activity_status
        original_cancel = shared.simulation_cancel_shared_activity
        original_client = shared.httpx.AsyncClient

        # Directly verify the final Simulation adapter signatures. The unified
        # Stage 1 branch does not yet contain exploration.py, so inject a tiny
        # contract-faithful module for this adapter-only check.
        original_exploration_module = sys.modules.get("agent_city.exploration")
        fake_exploration = types.ModuleType("agent_city.exploration")
        lifecycle_calls: list[str] = []

        def fake_accept(conn, activity_id, who, *, now):
            lifecycle_calls.append("accept")
            return True, None, "accepted without movement"

        def fake_start(conn, activity_id, who, *, now):
            lifecycle_calls.append("start")
            return True, 901, "physical start"

        def fake_reject(conn, activity_id, who, *, now):
            lifecycle_calls.append("reject")
            return True, "rejected before physical start"

        def fake_payload(conn, activity_id, now):
            status = "active" if "start" in lifecycle_calls else "accepted"
            return {
                "id": activity_id,
                "status": status,
                "citizen_job_id": 901 if "start" in lifecycle_calls else None,
                "started_minute": now if "start" in lifecycle_calls else None,
                "completed_minute": None,
                "observation_id": None,
                "outcome": None,
                "failure_reason": None,
                "frame_id": "seed_site_local",
                "target_x_m": 5.0,
                "target_y_m": 0.0,
                "activity_type": "walk_inspect",
                "objective": "Walk together and inspect.",
                "tool_equipment_id": None,
                "movement": {"progress": 0.0} if "start" in lifecycle_calls else None,
            }

        fake_exploration.accept_shared_activity = fake_accept
        fake_exploration.start_shared_activity = fake_start
        fake_exploration.reject_shared_activity = fake_reject
        fake_exploration.shared_activity_payload = fake_payload
        fake_exploration.propose_shared_activity = lambda *args, **kwargs: (True, 41, "proposed")
        sys.modules["agent_city.exploration"] = fake_exploration

        adapter_start = shared.simulation_accept_shared_activity(41, visitor)
        assert adapter_start["ok"] is True
        assert adapter_start["payload"]["action_id"] == "901"
        assert lifecycle_calls[:2] == ["accept", "start"]

        adapter_reject = shared.simulation_cancel_shared_activity(
            42,
            visitor,
            reason="visitor_rejected",
        )
        assert adapter_reject["ok"] is True
        assert lifecycle_calls[-1] == "reject"

        if original_exploration_module is None:
            sys.modules.pop("agent_city.exploration", None)
        else:
            sys.modules["agent_city.exploration"] = original_exploration_module

        next_activity_id = 40

        def fake_propose(**kwargs):
            nonlocal next_activity_id
            next_activity_id += 1
            return {
                "available": True,
                "ok": True,
                "reason": "Simulation validated and persisted a shared proposal.",
                "payload": {
                    "activity_id": next_activity_id,
                    "status": "proposed",
                    "action_id": None,
                    "progress": None,
                    "start_minute": None,
                    "end_minute": None,
                    "observation_ids": [],
                    "outcome": None,
                    "frame_id": "seed_site_local",
                    "target_x_m": kwargs["target_x_m"],
                    "target_y_m": kwargs["target_y_m"],
                    "activity_type": "walk_inspect",
                    "objective": kwargs["objective"],
                    "tool_equipment_id": None,
                },
            }

        try:
            # No Simulation lifecycle means no structured proposal can exist.
            shared._simulation_contract_available = lambda: False
            no_options = shared_action_option_context(visitor, citizen_id)
            assert "not available" in no_options

            shared.simulation_propose_shared_activity = lambda **kwargs: {
                "available": False,
                "ok": False,
                "reason": "unavailable",
            }
            exchange0 = make_exchange(
                visitor,
                citizen_id,
                visit_id,
                "Let's walk five meters east together.",
                "I'd be willing to do that.",
            )
            FakeAsyncClient.queue = [{"propose": True}]
            shared.httpx.AsyncClient = FakeAsyncClient
            proposal0 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange0,
                    visitor_text="Let's walk five meters east together.",
                    citizen_text="I'd be willing to do that.",
                    model="test-model",
                )
            )
            assert proposal0 is None

            # With Simulation available, Communication supplies only the explicit
            # relative request; Simulation validates/persists canonical proposal.
            shared._simulation_contract_available = lambda: True
            shared.simulation_propose_shared_activity = fake_propose
            options = shared_action_option_context(visitor, citizen_id)
            assert "short local walk + baseline inspection" in options
            assert "explicitly gives a meter distance" in options

            visitor_text = "Let's walk five meters east together and inspect the ground there."
            citizen_text = "Yes, we could walk over together and inspect that point."
            exchange1 = make_exchange(visitor, citizen_id, visit_id, visitor_text, citizen_text)
            FakeAsyncClient.queue = [{"propose": True}]

            proposal = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange1,
                    visitor_text=visitor_text,
                    citizen_text=citizen_text,
                    model="test-model",
                )
            )
            assert proposal is not None
            assert proposal["status"] == "proposed"
            assert proposal["acceptance_available"] is True
            assert proposal["simulation_activity_id"] == 41
            assert proposal["simulation_action_id"] is None
            assert proposal["target"]["frame_id"] == "seed_site_local"
            assert proposal["target"]["x_m"] == 5.0
            assert proposal["target"]["y_m"] == 0.0

            context = shared_action_context(visitor, citizen_id, visit_id=visit_id)
            assert "pending visitor acceptance" in context
            assert "NOT physically started" in context

            # Idempotent by durable visitor exchange.
            FakeAsyncClient.queue = []
            same = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange1,
                    visitor_text=visitor_text,
                    citizen_text=citizen_text,
                    model="test-model",
                )
            )
            assert same is not None and same["id"] == proposal["id"]

            # Explicit acceptance only becomes physical after Simulation returns
            # an active shared activity + real citizen job ID.
            shared.simulation_accept_shared_activity = lambda activity_id, who: {
                "available": True,
                "ok": True,
                "reason": "Shared activity accepted and physically started.",
                "payload": {
                    "activity_id": activity_id,
                    "status": "active",
                    "action_id": "900",
                    "progress": 0.0,
                    "start_minute": 1001,
                    "end_minute": None,
                    "observation_ids": [],
                    "outcome": None,
                    "frame_id": "seed_site_local",
                    "target_x_m": 5.0,
                    "target_y_m": 0.0,
                    "activity_type": "walk_inspect",
                    "objective": "Walk together and inspect.",
                    "tool_equipment_id": None,
                },
            }

            ok, message, started = accept_proposal(proposal["id"], visitor)
            assert ok is True
            assert "Simulation started" in message
            assert started is not None
            assert started["status"] == "started"
            assert started["simulation_activity_id"] == 41
            assert started["simulation_action_id"] == "900"

            # Completion evidence can only arrive from canonical Simulation status.
            shared.simulation_shared_activity_status = lambda activity_id: {
                "activity_id": activity_id,
                "status": "complete",
                "action_id": "900",
                "progress": 1.0,
                "start_minute": 1001,
                "end_minute": 1006,
                "observation_ids": [77],
                "outcome": "success",
                "failure_reason": None,
                "frame_id": "seed_site_local",
                "target_x_m": 5.0,
                "target_y_m": 0.0,
                "activity_type": "walk_inspect",
                "objective": "Walk together and inspect.",
                "tool_equipment_id": None,
            }
            completed = proposal_payload(proposal["id"], sync=True)
            assert completed is not None
            assert completed["status"] == "completed"
            assert completed["observation_ids"] == [77]
            assert completed["outcome"] == "success"

            # Rejection fails closed until Simulation also cancels the canonical
            # proposed activity.
            exchange2 = make_exchange(
                visitor,
                citizen_id,
                visit_id,
                "Let's walk three meters north together.",
                "I could do that.",
            )
            FakeAsyncClient.queue = [{"propose": True}]
            proposal2 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange2,
                    visitor_text="Let's walk three meters north together.",
                    citizen_text="I could do that.",
                    model="test-model",
                )
            )
            assert proposal2 is not None

            shared.simulation_cancel_shared_activity = lambda *args, **kwargs: {
                "available": False,
                "ok": False,
                "reason": "Simulation cancellation unavailable.",
            }
            ok, _, still_proposed = reject_proposal(proposal2["id"], visitor)
            assert ok is False
            assert still_proposed is not None
            assert still_proposed["status"] == "proposed"

            shared.simulation_cancel_shared_activity = lambda *args, **kwargs: {
                "available": True,
                "ok": True,
                "reason": "Simulation cancelled proposal.",
            }
            ok, message, rejected = reject_proposal(proposal2["id"], visitor)
            assert ok is True
            assert "No physical action was started" in message
            assert rejected is not None and rejected["status"] == "rejected"

            # If participants separate before acceptance, Communication only marks
            # expired after Simulation cancellation also succeeds.
            exchange3 = make_exchange(
                visitor,
                citizen_id,
                visit_id,
                "Let's walk two meters south together.",
                "That is possible.",
            )
            FakeAsyncClient.queue = [{"propose": True}]
            proposal3 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange3,
                    visitor_text="Let's walk two meters south together.",
                    citizen_text="That is possible.",
                    model="test-model",
                )
            )
            assert proposal3 is not None

            with connect() as conn:
                conn.execute(
                    "UPDATE visitor_presence SET location_id = 'resin_grove', x_m = -1200, y_m = 0 WHERE visitor = ?",
                    (visitor,),
                )
                conn.commit()

            shared.simulation_cancel_shared_activity = lambda *args, **kwargs: {
                "available": True,
                "ok": True,
                "reason": "Simulation cancelled stale proposal.",
            }
            ok, _, expired = accept_proposal(proposal3["id"], visitor)
            assert ok is False
            assert expired is not None and expired["status"] == "expired"

            # Mass expiration uses the same canonical-cancellation requirement.
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
                "Let's walk one meter west together.",
                "We could.",
            )
            FakeAsyncClient.queue = [{"propose": True}]
            proposal4 = asyncio.run(
                maybe_create_proposal_from_exchange(
                    visitor=visitor,
                    citizen_id=citizen_id,
                    visit_id=visit_id,
                    source_exchange_id=exchange4,
                    visitor_text="Let's walk one meter west together.",
                    citizen_text="We could.",
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
            shared._simulation_contract_available = original_contract
            shared.simulation_propose_shared_activity = original_propose
            shared.simulation_accept_shared_activity = original_accept
            shared.simulation_shared_activity_status = original_status
            shared.simulation_cancel_shared_activity = original_cancel
            shared.httpx.AsyncClient = original_client
            if original_exploration_module is None:
                sys.modules.pop("agent_city.exploration", None)
            else:
                sys.modules["agent_city.exploration"] = original_exploration_module


if __name__ == "__main__":
    main()
