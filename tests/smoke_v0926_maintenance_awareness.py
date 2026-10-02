from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, snapshot
        from agent_city.memory import ensure_memory_schema
        from agent_city.planner import citizen_context
        from agent_city.simulation import (
            local_maintenance_attention,
            possible_actions,
            start_action,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()

        with connect() as conn:
            charger = conn.execute(
                "SELECT id FROM structures WHERE name = 'Charging Station'"
            ).fetchone()
            assert charger is not None
            charger_id = int(charger["id"])

            conn.execute(
                """
                UPDATE structures
                SET condition = 89.4
                WHERE id = ?
                """,
                (charger_id,),
            )
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    position_x_m = 0, position_y_m = 0,
                    energy = 100, active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id IN ('cato', 'iri')
                """
            )
            conn.execute("UPDATE resources SET amount = 1 WHERE name = 'Lubricant'")
            conn.execute("UPDATE resources SET amount = 1 WHERE name = 'Fasteners'")
            conn.execute("UPDATE resources SET amount = 0 WHERE name = 'Mechanical components'")
            conn.commit()

        # The due structure is perceptible even when the repair cannot legally start.
        attention = local_maintenance_attention("cato")
        charger_need = next(
            item for item in attention
            if item["target_type"] == "structure"
            and item["target_id"] == str(charger_id)
        )
        assert charger_need["service_state"] == "blocked_materials"
        assert charger_need["requirements"] == {
            "Lubricant": 1.0,
            "Fasteners": 2.0,
            "Mechanical components": 1.0,
        }
        assert charger_need["shortfalls"]["Fasteners"]["short"] == 1.0
        assert charger_need["shortfalls"]["Mechanical components"]["short"] == 1.0

        blocked_actions = possible_actions("cato")
        assert not any(
            action["action"] == "service_structure"
            and action["target"] == str(charger_id)
            for action in blocked_actions
        )

        state = snapshot()
        cato = next(c for c in state["citizens"] if c["id"] == "cato")
        prompt = citizen_context(cato, state, blocked_actions)
        assert "CURRENT LOCALLY OBSERVABLE MAINTENANCE ATTENTION" in prompt
        assert "Charging Station" in prompt
        assert "Fasteners: 2 required, 1 stored, 1 short" in prompt
        assert "Mechanical components: 1 required, 0 stored, 1 short" in prompt
        assert "Do not invent a source, conversion, fabrication recipe, or substitute" in prompt
        assert "A raw deposit is not automatically a source of Fasteners" in prompt

        # Once real stock exists, the same physical need becomes a legal service action.
        with connect() as conn:
            conn.execute("UPDATE resources SET amount = 2 WHERE name = 'Fasteners'")
            conn.execute("UPDATE resources SET amount = 1 WHERE name = 'Mechanical components'")
            conn.commit()

        ready_attention = local_maintenance_attention("cato")
        ready_charger = next(
            item for item in ready_attention
            if item["target_type"] == "structure"
            and item["target_id"] == str(charger_id)
        )
        assert ready_charger["service_state"] == "ready"
        assert not ready_charger["shortfalls"]

        ready_actions = possible_actions("iri")
        service = next(
            action for action in ready_actions
            if action["action"] == "service_structure"
            and action["target"] == str(charger_id)
        )

        # A real in-progress repair is visible as such and suppresses duplicates.
        ok, message = start_action(
            "iri",
            {
                "action": "service_structure",
                "target": service["target"],
                "reason": "Service the due Charging Station with the available parts.",
            },
        )
        assert ok, message

        during_attention = local_maintenance_attention("cato")
        during_charger = next(
            item for item in during_attention
            if item["target_type"] == "structure"
            and item["target_id"] == str(charger_id)
        )
        assert during_charger["service_state"] == "in_progress"
        assert not any(
            action["action"] == "service_structure"
            and action["target"] == str(charger_id)
            for action in possible_actions("cato")
        )

        # Exact Seed Site maintenance/stock state does not leak to a remote citizen.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'resin_grove', location = 'Resin Grove',
                    position_x_m = -1200, position_y_m = 0,
                    active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'cato'
                """
            )
            conn.commit()

        assert local_maintenance_attention("cato") == []
        remote_state = snapshot()
        remote_cato = next(c for c in remote_state["citizens"] if c["id"] == "cato")
        remote_prompt = citizen_context(
            remote_cato,
            remote_state,
            possible_actions("cato"),
        )
        current_section = remote_prompt.split(
            "CURRENT LOCALLY OBSERVABLE MAINTENANCE ATTENTION:", 1
        )[1].split("MAINTENANCE ATTENTION RULES:", 1)[0]
        assert "Charging Station" not in current_section
        assert "no service-due maintenance is directly observable" in current_section

        print("v0.9.26 maintenance-awareness smoke passed")


if __name__ == "__main__":
    main()
