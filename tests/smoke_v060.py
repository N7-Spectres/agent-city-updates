from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def set_time(conn, minute: int) -> None:
    from agent_city.db import set_meta
    set_meta(conn, "sim_minute", minute)
    conn.commit()


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

        from agent_city.db import connect, init_db, snapshot
        from agent_city.knowledge import known_properties_for
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import complete_due_jobs, possible_actions, start_action
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        init_db()  # additive migrations remain idempotent

        # Hidden truth exists internally but the ordinary read model cannot see it.
        with connect() as conn:
            hidden = conn.execute(
                "SELECT * FROM world_properties WHERE id = 'prop_ferrite_field'"
            ).fetchone()
            assert hidden is not None
            hidden_value = str(hidden["value_text"])
            undiscovered_amount = float(
                conn.execute("SELECT amount FROM deposits WHERE id = 'dep_ferrite'").fetchone()["amount"]
            )

        state = snapshot()
        assert "world_properties" not in state
        assert state["deposits"] == []
        assert hidden_value not in json.dumps(state)
        assert all("amount" not in row for row in state["deposits"])

        # A physical survey creates stable discovery anchors and citizen-scoped knowledge.
        with connect() as conn:
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'northern_ridge', location = 'Northern Ridge',
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'aris'
                """
            )
            set_time(conn, 500)

        survey = next(a for a in possible_actions("aris") if a["action"] == "survey")
        ok, _ = start_action(
            "aris",
            {
                "action": "survey",
                "target": survey["target"],
                "reason": "Build a validated field record of this location.",
            },
        )
        assert ok
        survey_job = active_job("aris")
        complete_due_jobs(int(survey_job["end_minute"]))

        state = snapshot()
        assert any(d["id"] == "dep_ferrite" for d in state["deposits"])
        exposed_dep = next(d for d in state["deposits"] if d["id"] == "dep_ferrite")
        assert "amount" not in exposed_dep
        assert undiscovered_amount > 0  # truth still exists internally but quantity was not leaked
        north = next(loc for loc in state["locations"] if loc["id"] == "northern_ridge")
        assert north["known_facts"]
        assert any(f["kind"] == "deposit" for f in north["known_facts"])
        assert any(f["kind"] == "property" for f in north["known_facts"])

        aris_knowledge = [k for k in state["citizen_knowledge"] if k["citizen_id"] == "aris"]
        bex_knowledge = [k for k in state["citizen_knowledge"] if k["citizen_id"] == "bex"]
        assert aris_knowledge
        assert bex_knowledge == []

        # Put a physically obtained native sample in storage for controlled experiments.
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO resources(name, amount) VALUES ('Ferrite Stone', 4)
                ON CONFLICT(name) DO UPDATE SET amount = 4
                """
            )
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    energy = 100, active_job_id = NULL, current_activity = 'Available'
                WHERE id = 'noma'
                """
            )
            set_time(conn, 800)

        # Wrong method: legal experiment, real sample consumed, durable inconclusive outcome.
        wrong = next(
            a for a in possible_actions("noma")
            if a["action"] == "experiment"
            and a["target"] == "mechanical_assay:Ferrite Stone"
        )
        ok, _ = start_action(
            "noma",
            {
                "action": "experiment",
                "target": wrong["target"],
                "material": wrong["material"],
                "reason": "Test the sample's mechanical response without assuming an outcome.",
            },
        )
        assert ok
        wrong_job = active_job("noma")
        with connect() as conn:
            remaining = float(
                conn.execute("SELECT amount FROM resources WHERE name = 'Ferrite Stone'").fetchone()["amount"]
            )
            assert remaining == 3.0

        complete_due_jobs(int(wrong_job["end_minute"]))
        with connect() as conn:
            result = conn.execute(
                "SELECT * FROM experiment_results WHERE job_id = ?",
                (wrong_job["id"],),
            ).fetchone()
            assert result is not None
            assert result["outcome"] == "inconclusive"
            assert result["discovery_id"] is None
            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (wrong_job["id"],)).fetchone()
            assert job["status"] == "complete"
            assert job["outcome"] == "inconclusive"
            assert job["result_discovery_id"] is None

        state = snapshot()
        assert hidden_value not in json.dumps(state)
        assert known_properties_for("noma") == []

        # Matching method: Simulation reveals the pre-existing hidden property.
        with connect() as conn:
            set_time(conn, 1000)
            conn.execute(
                "UPDATE citizens SET energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'noma'"
            )
            conn.commit()

        correct = next(
            a for a in possible_actions("noma")
            if a["action"] == "experiment"
            and a["target"] == "electrical_assay:Ferrite Stone"
        )
        ok, _ = start_action(
            "noma",
            {
                "action": "experiment",
                "target": correct["target"],
                "material": correct["material"],
                "reason": "Compare the sample's electrical and field response.",
            },
        )
        assert ok
        correct_job = active_job("noma")
        complete_due_jobs(int(correct_job["end_minute"]))

        with connect() as conn:
            result = conn.execute(
                "SELECT * FROM experiment_results WHERE job_id = ?",
                (correct_job["id"],),
            ).fetchone()
            assert result is not None
            assert result["outcome"] == "discovery"
            discovery_id = int(result["discovery_id"])
            assert discovery_id > 0

            job = conn.execute("SELECT * FROM jobs WHERE id = ?", (correct_job["id"],)).fetchone()
            assert job["result_discovery_id"] == discovery_id
            process = conn.execute(
                """
                SELECT * FROM learned_processes
                WHERE citizen_id = 'noma' AND source_discovery_id = ?
                """,
                (discovery_id,),
            ).fetchone()
            assert process is not None
            assert process["process_kind"] == "verification"

        state = snapshot()
        assert hidden_value in json.dumps(state)
        noma_props = known_properties_for("noma")
        assert len(noma_props) == 1
        assert noma_props[0]["property_id"] == "prop_ferrite_field"
        assert noma_props[0]["value_text"] == hidden_value

        # Discovery by Noma does not silently grant the same knowledge to everybody.
        assert known_properties_for("bex") == []
        noma_rows = [k for k in state["citizen_knowledge"] if k["citizen_id"] == "noma"]
        bex_rows = [k for k in state["citizen_knowledge"] if k["citizen_id"] == "bex"]
        assert any(k["discovery_id"] == discovery_id for k in noma_rows)
        assert not any(k["discovery_id"] == discovery_id for k in bex_rows)

        # Repeating the learned assay reproduces the result without minting a fake new discovery.
        with connect() as conn:
            set_time(conn, 1200)
            conn.execute(
                "UPDATE citizens SET energy = 100, active_job_id = NULL, current_activity = 'Available' WHERE id = 'noma'"
            )
            conn.commit()

        ok, _ = start_action(
            "noma",
            {
                "action": "experiment",
                "target": correct["target"],
                "material": correct["material"],
                "reason": "Reproduce the earlier validated observation.",
            },
        )
        assert ok
        verify_job = active_job("noma")
        complete_due_jobs(int(verify_job["end_minute"]))
        with connect() as conn:
            verify = conn.execute(
                "SELECT * FROM experiment_results WHERE job_id = ?",
                (verify_job["id"],),
            ).fetchone()
            assert verify["outcome"] == "verified"
            assert verify["discovery_id"] is None
            property_discoveries = conn.execute(
                "SELECT COUNT(*) AS n FROM discoveries WHERE property_id = 'prop_ferrite_field' AND citizen_id = 'noma'"
            ).fetchone()["n"]
            assert int(property_discoveries) == 1

        print("Agent City v0.6 research/discovery smoke test passed.")


if __name__ == "__main__":
    main()
