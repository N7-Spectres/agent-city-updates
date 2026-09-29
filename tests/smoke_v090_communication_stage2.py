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
            "I remember guided extraction practice with Cato, but that was one event, "
            "not a title. I can explain what I remember, and a real guided session is "
            "separate from ordinary conversation."
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

        import agent_city.simulation as simulation

        original_competence = sys.modules.get("agent_city.competence")
        original_guided_memory = sys.modules.get("agent_city.guided_practice_memory")
        original_possible_actions = simulation.possible_actions

        competence_calls: list[str] = []

        fake_competence = types.ModuleType("agent_city.competence")

        def competence_snapshot(conn, citizen_id: str):
            competence_calls.append(citizen_id)
            if citizen_id == "bex":
                return [
                    {
                        "family": "extraction",
                        "practice_count": 7,
                        "completed_count": 7,
                        "failed_count": 0,
                        "weighted_evidence": 7.0,
                        "duration_multiplier": 0.94,
                        "source_practice_event_ids": [1, 2, 3, 4, 5, 6, 7],
                    },
                    {
                        "family": "fabrication",
                        "practice_count": 0,
                        "completed_count": 0,
                        "failed_count": 0,
                        "weighted_evidence": 0.0,
                        "duration_multiplier": 1.0,
                        "source_practice_event_ids": [],
                    },
                ]
            if citizen_id == "cato":
                return [
                    {
                        "family": "extraction",
                        "practice_count": 1,
                        "completed_count": 1,
                        "failed_count": 0,
                        "weighted_evidence": 1.0,
                        "duration_multiplier": 0.98,
                        "source_practice_event_ids": [8],
                    }
                ]
            return []

        fake_competence.competence_snapshot = competence_snapshot
        sys.modules["agent_city.competence"] = fake_competence

        fake_guided = types.ModuleType("agent_city.guided_practice_memory")

        def guided_practice_recall_snapshot_for(
            citizen_id: str,
            *,
            family: str | None = None,
            counterpart_id: str | None = None,
            role: str | None = None,
            now_minute=None,
            limit: int = 8,
        ):
            rows = []
            if citizen_id == "bex":
                rows.append({
                    "memory_event_id": 90,
                    "sim_minute": 2000,
                    "sim_label": "Day 2 09:20",
                    "source_type": "simulation_guided_practice_session",
                    "source_id": 12,
                    "source_role": "teacher",
                    "summary": "Completed guided extraction practice with Cato as the guide.",
                    "verification": "verified",
                    "facets": [
                        {"kind": "guided_practice_session", "value": "12"},
                        {"kind": "competence_family", "value": "extraction"},
                        {"kind": "guided_role", "value": "teacher"},
                        {"kind": "counterparty", "value": "cato"},
                    ],
                })
            elif citizen_id == "cato":
                rows.append({
                    "memory_event_id": 91,
                    "sim_minute": 2000,
                    "sim_label": "Day 2 09:20",
                    "source_type": "simulation_guided_practice_session",
                    "source_id": 12,
                    "source_role": "learner",
                    "summary": "Completed guided extraction practice with Bex as the learner.",
                    "verification": "verified",
                    "facets": [
                        {"kind": "guided_practice_session", "value": "12"},
                        {"kind": "competence_family", "value": "extraction"},
                        {"kind": "guided_role", "value": "learner"},
                        {"kind": "counterparty", "value": "bex"},
                    ],
                })

            if family:
                rows = [
                    row for row in rows
                    if any(
                        f["kind"] == "competence_family" and f["value"] == family
                        for f in row["facets"]
                    )
                ]
            if counterpart_id:
                rows = [
                    row for row in rows
                    if any(
                        f["kind"] == "counterparty" and f["value"] == counterpart_id
                        for f in row["facets"]
                    )
                ]
            if role:
                rows = [
                    row for row in rows
                    if any(
                        f["kind"] == "guided_role" and f["value"] == role
                        for f in row["facets"]
                    )
                ]
            return rows[:limit]

        def guided_practice_recall_context_for(
            citizen_id: str,
            *,
            family: str | None = None,
            counterpart_id: str | None = None,
            role: str | None = None,
            now_minute=None,
            limit: int = 6,
        ):
            rows = guided_practice_recall_snapshot_for(
                citizen_id,
                family=family,
                counterpart_id=counterpart_id,
                role=role,
                now_minute=now_minute,
                limit=limit,
            )
            if not rows:
                return "- no actively recalled source-backed guided-practice experience matched"
            return "\n".join(
                f"- Verified, {row['sim_label']} ({row['source_type']} #{row['source_id']}, role {row['source_role']}): {row['summary']}"
                for row in rows
            )

        fake_guided.guided_practice_recall_snapshot_for = guided_practice_recall_snapshot_for
        fake_guided.guided_practice_recall_context_for = guided_practice_recall_context_for
        sys.modules["agent_city.guided_practice_memory"] = fake_guided

        def fake_possible_actions(citizen_id: str):
            if citizen_id == "bex":
                return [
                    {
                        "action": "guided_practice",
                        "target": "cato:extraction",
                        "learner_id": "cato",
                        "activity_family": "extraction",
                        "label": "Guide Cato through a short extraction practice session.",
                    },
                    {"action": "wait", "target": "seed_site", "label": "Wait."},
                ]
            return [{"action": "wait", "target": "seed_site", "label": "Wait."}]

        simulation.possible_actions = fake_possible_actions

        try:
            from agent_city.continuity_language import (
                guided_practice_context,
                help_question_context,
                measured_competence_context,
                self_assessment_context,
            )

            # Objective self-effect is allowed, but hidden ledger counts/weights
            # are not injected into model-facing language.
            competence_calls.clear()
            measured = measured_competence_context("bex")
            assert "extraction" in measured
            assert "6.0% shorter duration" in measured
            assert "practice_count" not in measured
            assert "weighted_evidence" not in measured
            assert "7 practice" not in measured
            assert "expert" not in measured.lower()
            assert competence_calls == ["bex"]

            # Active autobiographical recall remains separate from measured effect.
            # With no practice recall seeded in Memory, self-assessment does not
            # invent the seven archive events from the measured effect.
            self_text = self_assessment_context("bex", activity="extract")
            assert "no actively recalled source-backed physical practice" in self_text
            assert "several times" not in self_text.lower() or "do not claim" in self_text.lower()

            # Bex recalls one real teacher-role event and currently has a legal
            # guided-practice action with Cato.
            guidance_bex = guided_practice_context(
                "bex",
                counterpart_id="cato",
            )
            assert "simulation_guided_practice_session #12" in guidance_bex
            assert "role teacher" in guidance_bex
            assert "guide Cato in extraction" in guidance_bex
            assert "not permanent mentor/trainer/expert identities" in guidance_bex
            assert "does not justify saying you are socially known to be more experienced" in guidance_bex

            # Cato remembers being learner, but does not magically inherit a
            # current ability to guide Bex.
            guidance_cato = guided_practice_context(
                "cato",
                counterpart_id="bex",
            )
            assert "simulation_guided_practice_session #12" in guidance_cato
            assert "role learner" in guidance_cato
            assert "no guided-practice action with this counterpart is currently exposed as legal" in guidance_cato

            # Asking for help is permitted without inventing superiority.
            help_text = help_question_context("cato", "bex")
            assert "may ask Bex about their experience" in help_text
            assert "A question is not a competence claim" in help_text
            assert "hidden/global competence data" in help_text

            # Private citizen context may inspect only the speaker's objective
            # competence snapshot. It must not fetch Bex's hidden competence
            # while building Cato's recognition packet.
            import agent_city.comms as comms

            competence_calls.clear()
            cato_private = comms._citizen_private_context("cato", "bex")
            assert "MEASURED PHYSICAL PRACTICE EFFECTS (SELF ONLY)" in cato_private
            assert "GUIDED PRACTICE / HELP CONTEXT" in cato_private
            assert "ASKING FOR HELP / EXPLANATION" in cato_private
            assert competence_calls == ["cato"]

            # Planner rules distinguish guided practice from ordinary talk and
            # from permanent identity.
            from agent_city.db import snapshot
            from agent_city.planner import citizen_context

            state = snapshot()
            bex = next(row for row in state["citizens"] if row["id"] == "bex")
            planner_text = citizen_context(
                bex,
                state,
                fake_possible_actions("bex"),
            )
            assert "guided_practice" in planner_text
            assert "session itself creates no learner practice/competence" in planner_text
            assert "Ordinary talk/explanation is information transfer only" in planner_text
            assert "expert, mentor, trainer, specialist, leader" in planner_text

            # Visitor dialogue gets own measured effect + recalled guided history,
            # but not the current citizen-to-citizen legal guidance option.
            ensure_visitor("N7")
            with connect() as conn:
                conn.execute(
                    """
                    UPDATE visitor_presence
                    SET location_id='seed_site', x_m=0, y_m=0,
                        from_location_id=NULL, to_location_id=NULL,
                        travel_start_minute=NULL, travel_end_minute=NULL
                    WHERE visitor='N7'
                    """
                )
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id='seed_site', location='Seed Site',
                        position_x_m=0, position_y_m=0,
                        active_job_id=NULL, current_activity='Available', energy=100
                    WHERE id='bex'
                    """
                )
                before_jobs = int(conn.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"])
                conn.commit()

            import main as app_module

            original_client = app_module.httpx.AsyncClient
            CaptureAsyncClient.payloads = []
            app_module.httpx.AsyncClient = CaptureAsyncClient
            try:
                req = app_module.TalkRequest(
                    visitor="N7",
                    citizen_id="bex",
                    message="Are you better at extraction now? Can you teach me?",
                )
                result = asyncio.run(app_module.talk(req))
                assert result["message"]

                system_text = CaptureAsyncClient.payloads[0]["messages"][0]["content"]
                assert "MEASURED PHYSICAL PRACTICE EFFECTS (SELF ONLY)" in system_text
                assert "simulation_guided_practice_session #12" in system_text
                assert "Real guided-practice actions you can legally start right now" not in system_text
                assert "visitor is ordinary conversation and creates no practice" in system_text.lower()
            finally:
                app_module.httpx.AsyncClient = original_client

            with connect() as conn:
                after_jobs = int(conn.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"])
            assert after_jobs == before_jobs

            print("Agent City v0.9 Communication guided-practice Stage 2 smoke passed.")

        finally:
            simulation.possible_actions = original_possible_actions
            if original_competence is None:
                sys.modules.pop("agent_city.competence", None)
            else:
                sys.modules["agent_city.competence"] = original_competence

            if original_guided_memory is None:
                sys.modules.pop("agent_city.guided_practice_memory", None)
            else:
                sys.modules["agent_city.guided_practice_memory"] = original_guided_memory


if __name__ == "__main__":
    main()
