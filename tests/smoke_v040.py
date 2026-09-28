from __future__ import annotations

import tempfile
from pathlib import Path

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db, snapshot
        from agent_city.memory import (
            ensure_memory_schema,
            relationship_snapshot,
            social_context_for,
        )
        from agent_city.comms import record_dialogue
        from agent_city.planner import citizen_context
        from agent_city.simulation import possible_actions
        from agent_city.visits import ensure_visit_schema
        from agent_city.visitors import presence_payload, start_visitor_travel

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # Fresh DB basics.
        state = snapshot()
        assert len(state["citizens"]) == 6
        assert state["sim_minute"] == 360

        # Persist a real citizen conversation and ensure both directional memories exist.
        record_dialogue(
            365,
            "seed_site",
            "bex",
            "aris",
            "Before I travel, what have you seen nearby?",
            "Nothing beyond what we can see here yet.",
            "Bex asked Aris for local information before considering travel.",
        )

        bex_rel = relationship_snapshot("bex")
        aris_rel = relationship_snapshot("aris")
        assert bex_rel and bex_rel[0]["other_id"] == "aris"
        assert aris_rel and aris_rel[0]["other_id"] == "bex"
        assert bex_rel[0]["conversation_count"] == 1
        assert aris_rel[0]["conversation_count"] == 1

        # Re-running migration/backfill must not inflate relationship counts.
        ensure_memory_schema()
        bex_rel_again = relationship_snapshot("bex")
        assert bex_rel_again[0]["conversation_count"] == 1

        social = social_context_for("bex")
        assert "Aris" in social
        assert "claims, not automatic physical facts" in social

        # Anti-omniscience: move Aris away and ensure Bex's planner context
        # does not receive Aris's live remote activity/location.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'northern_ridge',
                    location = 'Northern Ridge',
                    current_activity = 'Surveying Northern Ridge'
                WHERE id = 'aris'
                """
            )
            conn.commit()

        state = snapshot()
        bex = next(c for c in state["citizens"] if c["id"] == "bex")
        ctx = citizen_context(bex, state, possible_actions("bex"))
        assert "Surveying Northern Ridge" not in ctx
        assert "Aris: Surveying Northern Ridge" not in ctx

        # Visitor presence and travel still initialize on the migrated schema.
        presence = presence_payload("N7")
        assert presence["location_id"] == "seed_site"
        ok, _ = start_visitor_travel("N7", "resin_grove")
        assert ok
        traveling = presence_payload("N7")
        assert traveling["traveling"] is True
        assert traveling["to_location_id"] == "resin_grove"

        # Importing the FastAPI application must succeed with the integrated modules.
        import main as app_module
        assert app_module.app.title == "Agent City"

        print("Agent City v0.4.0 smoke test passed.")


if __name__ == "__main__":
    main()
