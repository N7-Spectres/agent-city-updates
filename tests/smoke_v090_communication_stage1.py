from __future__ import annotations

import asyncio
import sys
import tempfile
import types
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
            "I've done extraction a few times, so I can tell you what worked for me. "
            "That doesn't make me an expert, and explaining it won't give you practice by itself."
        )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema
        from agent_city.provenance import ensure_information_schema
        from agent_city.talk_diagnostics import ensure_talk_diagnostic_schema
        from agent_city.visitors import ensure_visitor
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()
        ensure_talk_diagnostic_schema()

        original_continuity = sys.modules.get("agent_city.continuity")
        original_causal = sys.modules.get("agent_city.causal_memory")
        original_practice_memory = sys.modules.get("agent_city.practice_memory")

        practice_calls: list[str] = []
        practice_recall_calls: list[tuple[str, str | None]] = []

        fake_continuity = types.ModuleType("agent_city.continuity")

        def practice_snapshot_for(citizen_id: str, *, limit: int = 40):
            practice_calls.append(citizen_id)
            if citizen_id == "bex":
                return [
                    {
                        "id": 1,
                        "job_id": 101,
                        "citizen_id": "bex",
                        "activity_type": "extract",
                        "job_status": "complete",
                        "outcome": "success",
                        "completed_minute": 1000,
                    },
                    {
                        "id": 2,
                        "job_id": 102,
                        "citizen_id": "bex",
                        "activity_type": "extract",
                        "job_status": "complete",
                        "outcome": "success",
                        "completed_minute": 1100,
                    },
                    {
                        "id": 3,
                        "job_id": 103,
                        "citizen_id": "bex",
                        "activity_type": "extract",
                        "job_status": "failed",
                        "outcome": "failed",
                        "completed_minute": 1200,
                    },
                    {
                        "id": 4,
                        "job_id": 104,
                        "citizen_id": "bex",
                        "activity_type": "extract",
                        "job_status": "complete",
                        "outcome": "success",
                        "completed_minute": 1300,
                    },
                    {
                        "id": 5,
                        "job_id": 105,
                        "citizen_id": "bex",
                        "activity_type": "service_equipment",
                        "job_status": "complete",
                        "outcome": "success",
                        "completed_minute": 1350,
                    },
                ]
            if citizen_id == "cato":
                return [
                    {
                        "id": 6,
                        "job_id": 201,
                        "citizen_id": "cato",
                        "activity_type": "extract",
                        "job_status": "complete",
                        "outcome": "success",
                        "completed_minute": 1250,
                    }
                ]
            return []

        def plan_snapshot_for(citizen_id: str, *, include_closed: bool = True, limit: int = 12):
            if citizen_id == "bex":
                return [
                    {
                        "id": 44,
                        "owner_id": "bex",
                        "status": "active",
                        "current_intent": "Finish the Resin Grove follow-up survey.",
                        "next_step": "Return to Resin Grove when energy allows.",
                        "unresolved_question": "Whether the western edge needs another pass.",
                    }
                ]
            return []

        def plan_context_for_planner(owner_id: str, *, now=None):
            return "UNFINISHED PLANS:\n- none"

        def causal_candidates_for_new_plan(owner_id: str, *, now: int, limit: int = 6):
            return []

        def apply_planner_plan_decision(owner_id: str, decision: dict, *, now: int):
            return True, None, "No plan lifecycle change."

        fake_continuity.practice_snapshot_for = practice_snapshot_for
        fake_continuity.plan_snapshot_for = plan_snapshot_for
        fake_continuity.plan_context_for_planner = plan_context_for_planner
        fake_continuity.causal_candidates_for_new_plan = causal_candidates_for_new_plan
        fake_continuity.apply_planner_plan_decision = apply_planner_plan_decision
        sys.modules["agent_city.continuity"] = fake_continuity

        fake_causal = types.ModuleType("agent_city.causal_memory")

        def causal_recall_snapshot(owner_id: str, *, facet_filters=None, pinned_event_ids=None, limit=8, now_minute=None):
            filters = facet_filters or {}
            if owner_id == "cato" and filters.get("counterparty") == "bex":
                return [
                    {
                        "memory_event_id": 50,
                        "owner_id": "cato",
                        "sim_minute": 1400,
                        "sim_label": "Day 1 23:20",
                        "event_kind": "conversation",
                        "source_type": "citizen_conversation",
                        "source_id": 900,
                        "summary": "Bex said she has handled extraction work before.",
                        "verification": "unverified",
                        "reinforcement_count": 2,
                        "facets": [
                            {"kind": "counterparty", "value": "bex"},
                            {"kind": "activity", "value": "extract"},
                        ],
                    }
                ]
            if owner_id == "bex" and filters.get("visitor") == "N7":
                return [
                    {
                        "memory_event_id": 60,
                        "owner_id": "bex",
                        "sim_minute": 1500,
                        "sim_label": "Day 2 01:00",
                        "event_kind": "shared_exploration",
                        "source_type": "simulation_shared_activity",
                        "source_id": 12,
                        "summary": "N7 and Bex completed a shared local walk and inspection.",
                        "verification": "verified",
                        "reinforcement_count": 1,
                        "facets": [
                            {"kind": "visitor", "value": "N7"},
                        ],
                    }
                ]
            return []

        fake_causal.causal_recall_snapshot = causal_recall_snapshot
        sys.modules["agent_city.causal_memory"] = fake_causal

        fake_practice_memory = types.ModuleType("agent_city.practice_memory")

        def practice_recall_snapshot_for(
            citizen_id: str,
            *,
            activity: str | None = None,
            now_minute=None,
            limit: int = 8,
        ):
            practice_recall_calls.append((citizen_id, activity))
            if citizen_id != "bex":
                return []
            rows = [
                {
                    "memory_event_id": 70,
                    "sim_minute": 1200,
                    "sim_label": "Day 1 20:00",
                    "event_kind": "practice_extract",
                    "source_type": "simulation_practice_event",
                    "source_id": 301,
                    "summary": "Completed extract job #101 with outcome success.",
                    "verification": "verified",
                    "facets": [
                        {"kind": "practice_event", "value": "1"},
                        {"kind": "activity", "value": "extract"},
                    ],
                },
                {
                    "memory_event_id": 71,
                    "sim_minute": 1300,
                    "sim_label": "Day 1 21:40",
                    "event_kind": "practice_extract",
                    "source_type": "simulation_practice_event",
                    "source_id": 302,
                    "summary": "Completed extract job #102 with outcome success.",
                    "verification": "verified",
                    "facets": [
                        {"kind": "practice_event", "value": "2"},
                        {"kind": "activity", "value": "extract"},
                    ],
                },
                {
                    "memory_event_id": 72,
                    "sim_minute": 1400,
                    "sim_label": "Day 1 23:20",
                    "event_kind": "practice_extract",
                    "source_type": "simulation_practice_event",
                    "source_id": 303,
                    "summary": "Ended extract job #103 with outcome failed.",
                    "verification": "verified",
                    "facets": [
                        {"kind": "practice_event", "value": "3"},
                        {"kind": "activity", "value": "extract"},
                    ],
                },
                {
                    "memory_event_id": 73,
                    "sim_minute": 1450,
                    "sim_label": "Day 2 00:10",
                    "event_kind": "practice_service_equipment",
                    "source_type": "simulation_practice_event",
                    "source_id": 304,
                    "summary": "Completed service_equipment job #105 with outcome success.",
                    "verification": "verified",
                    "facets": [
                        {"kind": "practice_event", "value": "5"},
                        {"kind": "activity", "value": "service_equipment"},
                    ],
                },
            ]
            if activity:
                rows = [
                    row for row in rows
                    if any(
                        facet["kind"] == "activity" and facet["value"] == activity
                        for facet in row["facets"]
                    )
                ]
            return rows[:limit]

        def practice_recall_context_for(
            citizen_id: str,
            *,
            activity: str | None = None,
            now_minute=None,
            limit: int = 6,
        ):
            rows = practice_recall_snapshot_for(
                citizen_id,
                activity=activity,
                now_minute=now_minute,
                limit=limit,
            )
            if not rows:
                return "- no actively recalled source-backed physical practice matching this subject"
            return "\n".join(
                f"- Verified, {row['sim_label']} ({row['source_type']} #{row['source_id']}): {row['summary']}"
                for row in rows
            )

        fake_practice_memory.practice_recall_snapshot_for = practice_recall_snapshot_for
        fake_practice_memory.practice_recall_context_for = practice_recall_context_for
        sys.modules["agent_city.practice_memory"] = fake_practice_memory

        try:
            from agent_city.continuity_language import (
                continuity_language_snapshot,
                own_practice_summary,
                plan_discussion_context,
                recognition_context,
                self_assessment_context,
                teaching_boundary_context,
                visitor_continuity_context,
            )

            # Own physical practice can support ordinary self-description.
            own = own_practice_summary("bex")
            extraction = next(row for row in own if row["activity"] == "extract")
            assert extraction["practice_count"] == 4
            assert extraction["completed_count"] == 3
            assert extraction["failed_count"] == 1
            assert extraction["may_say_several_times"] is True

            # Model-facing self-assessment uses bounded active Memory recall,
            # not the full durable Simulation practice ledger.
            practice_calls.clear()
            practice_recall_calls.clear()
            self_text = self_assessment_context("bex", activity="extract")
            assert "simulation_practice_event #301" in self_text
            assert "simulation_practice_event #303" in self_text
            assert "at least 3 source-backed extract practice experiences" in self_text
            assert "bounded active Memory, not the full durable practice ledger" in self_text
            assert "not objective capability truth" in self_text
            assert practice_calls == []
            assert ("bex", "extract") in practice_recall_calls

            # Recognition of Bex from Cato uses Cato's own recall only. The
            # unverified report stays unverified despite reinforcement.
            practice_calls.clear()
            recognition = recognition_context("cato", "bex", activity="extract")
            assert "BEX" in recognition
            assert "remembered/report" in recognition
            assert "related recall x2" not in recognition
            assert "reinforcement_count" not in recognition
            assert "civilization-wide reputation" in recognition
            assert practice_calls == []

            # Noma cannot inherit Bex's hidden/global practice record.
            no_evidence = recognition_context("noma", "bex", activity="extract")
            assert "no source-backed personal recall" in no_evidence
            assert practice_calls == []

            # Teaching also uses bounded active practice recall, never the full ledger.
            practice_calls.clear()
            practice_recall_calls.clear()
            teaching = teaching_boundary_context("bex")
            assert "simulation_practice_event #301" in teaching
            assert "extract" in teaching
            assert "service_equipment" in teaching
            assert "bounded active Memory, not the full durable practice ledger" in teaching
            assert "does NOT create practice or competence for the listener" in teaching
            assert "future Simulation-owned guided-practice/teaching event" in teaching
            assert "reinforcement" not in teaching.lower() or "must not be spoken" in teaching.lower()
            assert practice_calls == []
            assert any(call[0] == "bex" for call in practice_recall_calls)

            # Plans are discussable but not writable through conversation.
            plan_text = plan_discussion_context("bex")
            assert "Plan #44 [active]" in plan_text
            assert "speaking about it does not create, complete, pause, revise" in plan_text.lower()
            assert "Simulation/planner plan lifecycle" in plan_text

            # Visitor recognition requires real retained visitor sources.
            visitor_text = visitor_continuity_context("bex", "N7")
            assert "simulation_shared_activity #12" in visitor_text
            assert "UI/account ownership creates no social authority" in visitor_text

            # Objective debug/read model may still use the full durable ledger.
            practice_calls.clear()
            read_model = continuity_language_snapshot("bex")
            assert "bex" in practice_calls
            assert read_model["practice"][0]["practice_count"] >= 1
            assert read_model["rules"]["global_reputation"] is False
            assert read_model["rules"]["authoritative_titles"] is False
            assert read_model["rules"]["conversation_grants_skill"] is False
            assert read_model["rules"]["self_assessment_is_interpretation"] is True
            assert not any(
                key in read_model
                for key in ("xp", "level", "role", "class", "reputation", "expertise_score")
            )

            # Citizen-to-citizen private context carries the perspective-safe
            # evidence packet for the actual counterpart.
            import agent_city.comms as comms

            private = comms._citizen_private_context("cato", "bex")
            assert "SELF-ASSESSMENT EVIDENCE" in private
            assert "PERSPECTIVE-SAFE RECOGNITION OF BEX" in private
            assert "TEACHING / EXPLANATION BOUNDARY" in private

            # Visitor dialogue receives the same continuity boundaries.
            ensure_visitor("N7")
            with connect() as conn:
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
                    WHERE visitor = 'N7'
                    """
                )
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = 'seed_site',
                        location = 'Seed Site',
                        position_x_m = 0,
                        position_y_m = 0,
                        active_job_id = NULL,
                        current_activity = 'Available'
                    WHERE id = 'bex'
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
                    citizen_id="bex",
                    message="You've done extraction a lot. Does that make you an expert, and can you teach me?",
                )
                result = asyncio.run(app_module.talk(req))
                assert result["message"]
                system_text = CaptureAsyncClient.payloads[0]["messages"][0]["content"]
                assert "SELF-ASSESSMENT EVIDENCE" in system_text
                assert "PERSISTENT PLAN DISCUSSION" in system_text
                assert "TEACHING / EXPLANATION BOUNDARY" in system_text
                assert "VISITOR CONTINUITY FOR N7" in system_text
                assert "Do not create or repeat authoritative titles" in system_text
                assert "Explaining or teaching in conversation does not create practice" in system_text
                assert "conversation itself does not alter canonical plan state" in system_text
            finally:
                app_module.httpx.AsyncClient = original_client

            print("Agent City v0.9 Communication recognition/teaching Stage 1 smoke test passed.")

        finally:
            if original_continuity is None:
                sys.modules.pop("agent_city.continuity", None)
            else:
                sys.modules["agent_city.continuity"] = original_continuity

            if original_causal is None:
                sys.modules.pop("agent_city.causal_memory", None)
            else:
                sys.modules["agent_city.causal_memory"] = original_causal

            if original_practice_memory is None:
                sys.modules.pop("agent_city.practice_memory", None)
            else:
                sys.modules["agent_city.practice_memory"] = original_practice_memory


if __name__ == "__main__":
    main()
