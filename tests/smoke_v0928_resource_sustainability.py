from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


HIDDEN_LEGACY_MATERIALS = {
    "Ferrite Stone",
    "Veyra Ore",
    "Silicate",
    "Copper-like Ore",
    "Carbonaceous Rock",
    "Clay",
    "Plant Fiber",
    "Native Resin",
}


def active_job(citizen_id: str) -> dict:
    from agent_city.db import connect

    with connect() as conn:
        row = conn.execute(
            """
            SELECT j.*
            FROM citizens c
            JOIN jobs j ON j.id = c.active_job_id
            WHERE c.id = ?
            """,
            (citizen_id,),
        ).fetchone()
        assert row is not None
        return dict(row)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.comms import known_deposits_for
        from agent_city.continuity_language import guided_practice_context
        from agent_city.db import connect, init_db, snapshot
        from agent_city.grounding import grounding_policy_text
        from agent_city.memory import ensure_memory_schema
        from agent_city.planner import citizen_context
        from agent_city.simulation import (
            complete_due_jobs,
            local_resource_sustainability_attention,
            possible_actions,
            start_action,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        # At Seed Site, a citizen can assess finite manufactured starter stock.
        rows = local_resource_sustainability_attention("cato")
        assert rows
        by_material = {row["material"]: row for row in rows}
        assert by_material["Fasteners"]["stored"] == 100
        assert by_material["Mechanical components"]["stored"] == 60
        assert all(
            row["replenishment_status"] == "no_validated_production_process"
            for row in rows
        )

        state = snapshot()
        cato = next(c for c in state["citizens"] if c["id"] == "cato")
        actions = possible_actions("cato")
        prompt = citizen_context(cato, state, actions)
        sustainability = prompt.split(
            "CURRENT LOCALLY OBSERVABLE RESOURCE SUSTAINABILITY:", 1
        )[1].split("RESOURCE SUSTAINABILITY RULES:", 1)[0]

        assert "Fasteners: 100 units stored" in sustainability
        assert "Mechanical components: 60 units stored" in sustainability
        assert "no validated production process currently available to you" in sustainability
        assert not any(material in sustainability for material in HIDDEN_LEGACY_MATERIALS)
        assert "This is strategic context, not an assigned objective." in prompt
        assert "A survey may reveal a real deposit or produce no new finding." in prompt
        assert "Do not infer that a particular region" in prompt

        # Exact Seed Site stock state disappears when the citizen is physically remote.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'northern_ridge', location = 'Northern Ridge',
                    position_x_m = 0, position_y_m = 1800,
                    energy = 100, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            conn.commit()

        assert local_resource_sustainability_attention("cato") == []
        remote_state = snapshot()
        remote_cato = next(c for c in remote_state["citizens"] if c["id"] == "cato")
        remote_prompt = citizen_context(
            remote_cato,
            remote_state,
            possible_actions("cato"),
        )
        remote_sustainability = remote_prompt.split(
            "CURRENT LOCALLY OBSERVABLE RESOURCE SUSTAINABILITY:", 1
        )[1].split("RESOURCE SUSTAINABILITY RULES:", 1)[0]
        assert "Fasteners: 100 units stored" not in remote_sustainability
        assert "no exact Seed Site starter-stock sustainability state is directly observable here" in remote_sustainability

        # Hidden deposit truth remains unknown until a real Simulation survey finishes.
        assert known_deposits_for("cato") == []
        survey = next(
            action for action in possible_actions("cato")
            if action["action"] == "survey"
            and action["target"] == "northern_ridge"
        )
        ok, message = start_action(
            "cato",
            {
                "action": "survey",
                "target": survey["target"],
                "reason": (
                    "Investigate the region without assuming what materials, if any, "
                    "will be found."
                ),
            },
        )
        assert ok, message
        job = active_job("cato")
        complete_due_jobs(int(job["end_minute"]))

        discovered = known_deposits_for("cato")
        assert discovered, "A completed legitimate survey should create a real discovery here."
        assert discovered[0]["location_name"] == "Northern Ridge"
        assert discovered[0]["material"] in {"Ferrite Stone", "Veyra Ore"}

        # Generic practice categories must not mutate into invented named procedures.
        grounding = grounding_policy_text(visitor_facing=False)
        assert "Do not coin or casually treat a named procedure" in grounding
        guidance = guided_practice_context(
            "cato",
            counterpart_id="bex",
            include_current_options=True,
        )
        assert "Guided-practice families are generic" in guidance
        assert "do not invent a named procedure" in guidance

        print("v0.9.28 resource-sustainability / grounding smoke passed")


if __name__ == "__main__":
    main()
