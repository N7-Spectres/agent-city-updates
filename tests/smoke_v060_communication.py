from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.comms import record_dialogue
        from agent_city.db import connect, init_db, set_meta
        from agent_city.provenance import (
            ensure_information_schema,
            information_receipts_for,
            knowledge_context_for,
            knowledge_payload,
            record_validated_information,
        )
        from agent_city.memory import ensure_memory_schema
        from agent_city.simulation import complete_due_jobs, start_action
        from agent_city.visitors import ensure_visitor, visit_access_payload
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()

        # Create an unambiguous legacy survey discovery before the Communication
        # provenance migration, then ensure it becomes a verified receipt.
        with connect() as conn:
            set_meta(conn, "sim_minute", 400)
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'resin_grove',
                    location = 'Resin Grove',
                    energy = 100,
                    active_job_id = NULL,
                    current_activity = 'Available'
                WHERE id = 'noma'
                """
            )
            conn.execute("UPDATE locations SET surveyed = 0 WHERE id = 'resin_grove'")
            conn.commit()

        ok, _ = start_action(
            "noma",
            {
                "action": "survey",
                "target": "resin_grove",
                "reason": "Measure the grove directly.",
            },
        )
        assert ok
        with connect() as conn:
            survey_job = conn.execute(
                "SELECT * FROM jobs WHERE id = (SELECT active_job_id FROM citizens WHERE id = 'noma')"
            ).fetchone()
            survey_job_id = int(survey_job["id"])
            survey_end = int(survey_job["end_minute"])

        complete_due_jobs(survey_end)
        ensure_information_schema()

        noma_receipts = information_receipts_for("noma")
        survey_receipts = [
            r for r in noma_receipts
            if r["origin_event_type"] == "job"
            and r["origin_event_id"] == survey_job_id
        ]
        assert survey_receipts
        assert all(r["verification"] == "verified" for r in survey_receipts)
        assert all(r["assertion_kind"] == "validated_observation" for r in survey_receipts)
        assert any(r["channel"] == "survey_measurement" for r in survey_receipts)

        # A direct Simulation-grounded experiment result can be recorded through
        # the stable Communication ingestion surface without exposing hidden truth
        # to every other citizen.
        experiment_receipt = record_validated_information(
            recipient_id="noma",
            subject_type="material",
            subject_id="native_resin",
            topic="heat_response",
            value_text="Softens under controlled heat.",
            channel="experiment_result",
            origin_event_type="experiment",
            origin_event_id=77,
            observed_at_sim_minute=600,
        )
        assert experiment_receipt is not None
        assert not any(
            r["topic"] == "heat_response"
            for r in information_receipts_for("cato")
        )

        # Simulate the final v0.6 Simulation contract. Communication syncs only
        # citizen-local validated knowledge, never hidden truth by itself.
        with connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS world_properties (
                    id TEXT PRIMARY KEY,
                    subject_type TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    property_key TEXT NOT NULL,
                    value_text TEXT NOT NULL,
                    unit TEXT,
                    assay_method TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS discoveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discovery_kind TEXT NOT NULL,
                    subject_type TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    property_id TEXT,
                    citizen_id TEXT NOT NULL,
                    location_id TEXT NOT NULL,
                    source_job_id INTEGER,
                    discovered_minute INTEGER NOT NULL,
                    summary TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS citizen_knowledge (
                    citizen_id TEXT NOT NULL,
                    discovery_id INTEGER NOT NULL,
                    learned_minute INTEGER NOT NULL,
                    acquisition_kind TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    verification_state TEXT NOT NULL,
                    PRIMARY KEY(citizen_id, discovery_id)
                );

                CREATE TABLE IF NOT EXISTS experiment_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL UNIQUE,
                    citizen_id TEXT NOT NULL,
                    location_id TEXT NOT NULL,
                    material TEXT NOT NULL,
                    method TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    discovery_id INTEGER,
                    summary TEXT NOT NULL,
                    completed_minute INTEGER NOT NULL
                );
                """
            )
            conn.execute(
                """
                INSERT INTO world_properties
                (id, subject_type, subject_id, property_key, value_text, unit, assay_method)
                VALUES ('prop_test', 'material', 'Plant Fiber', 'tensile_behavior',
                        'high tensile strength for its mass', NULL, 'mechanical_assay')
                """
            )
            cur = conn.execute(
                """
                INSERT INTO discoveries
                (discovery_kind, subject_type, subject_id, property_id, citizen_id,
                 location_id, source_job_id, discovered_minute, summary)
                VALUES ('world_property', 'material', 'Plant Fiber', 'prop_test',
                        'noma', 'seed_site', 501, 650,
                        'Plant Fiber: tensile_behavior — high tensile strength for its mass.')
                """
            )
            discovery_id = int(cur.lastrowid)
            conn.execute(
                """
                INSERT INTO citizen_knowledge
                (citizen_id, discovery_id, learned_minute, acquisition_kind,
                 source_type, source_id, verification_state)
                VALUES ('noma', ?, 650, 'direct_experiment', 'discovery', ?, 'verified')
                """,
                (discovery_id, str(discovery_id)),
            )
            conn.execute(
                """
                INSERT INTO citizen_knowledge
                (citizen_id, discovery_id, learned_minute, acquisition_kind,
                 source_type, source_id, verification_state)
                VALUES ('cato', ?, 660, 'communicated_claim', 'citizen_conversation', '99', 'reported')
                """,
                (discovery_id,),
            )
            conn.execute(
                """
                INSERT INTO experiment_results
                (job_id, citizen_id, location_id, material, method, outcome,
                 discovery_id, summary, completed_minute)
                VALUES (502, 'vale', 'seed_site', 'Clay', 'electrical_assay',
                        'inconclusive', NULL,
                        'Vale tested Clay electrically; the assay produced no validated property finding.',
                        670)
                """
            )
            conn.commit()

        ensure_information_schema()

        synced_noma = [
            r for r in information_receipts_for("noma")
            if r["origin_event_type"] == "simulation_discovery"
            and r["origin_event_id"] == discovery_id
        ]
        assert len(synced_noma) == 1
        assert synced_noma[0]["verification"] == "verified"
        assert synced_noma[0]["channel"] == "experiment_result"
        assert "high tensile strength" in synced_noma[0]["value_text"]

        # A Simulation row marked merely reported is not upgraded into a verified
        # Communication receipt by synchronization.
        assert not any(
            r["origin_event_type"] == "simulation_discovery"
            and r["origin_event_id"] == discovery_id
            for r in information_receipts_for("cato")
        )

        vale_results = [
            r for r in information_receipts_for("vale")
            if r["origin_event_type"] == "simulation_experiment_result"
        ]
        assert len(vale_results) == 1
        assert vale_results[0]["topic"] == "experiment_inconclusive"
        assert "no validated property finding" in vale_results[0]["value_text"]

        # Put Bex/Aris together and persist one real talk with explicit claims.
        with connect() as conn:
            set_meta(conn, "sim_minute", 700)
            for citizen_id in ("bex", "aris"):
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = 'seed_site',
                        location = 'Seed Site',
                        active_job_id = NULL,
                        current_activity = 'Available',
                        energy = 100
                    WHERE id = ?
                    """,
                    (citizen_id,),
                )
            conn.commit()

        ok, _ = start_action(
            "bex",
            {
                "action": "talk",
                "target": "aris",
                "reason": "Share one specific observation.",
            },
        )
        assert ok
        with connect() as conn:
            talk_job_id = int(
                conn.execute(
                    "SELECT active_job_id FROM citizens WHERE id = 'bex'"
                ).fetchone()["active_job_id"]
            )

        conversation_id = record_dialogue(
            700,
            "seed_site",
            "bex",
            "aris",
            "I saw Plant Fiber at Resin Grove during my last trip.",
            "Thanks. I have not verified that myself.",
            "Bex told Aris that Bex had seen Plant Fiber at Resin Grove; Aris said it was not personally verified.",
            source_job_id=talk_job_id,
            claims=[
                {
                    "speaker": "initiator",
                    "subject_type": "location",
                    "subject_id": "resin_grove",
                    "topic": "plant_fiber_present",
                    "value": "I saw Plant Fiber at Resin Grove during my last trip.",
                },
                {
                    "speaker": "target",
                    "subject_type": "claim",
                    "subject_id": None,
                    "topic": "verification_status",
                    "value": "Thanks. I have not verified that myself.",
                },
            ],
        )
        assert conversation_id is not None

        aris_receipts = information_receipts_for("aris")
        transferred = [
            r for r in aris_receipts
            if r["source_conversation_id"] == conversation_id
        ]
        assert len(transferred) == 1
        claim = transferred[0]
        assert claim["source_actor_id"] == "bex"
        assert claim["channel"] == "face_to_face_claim"
        assert claim["assertion_kind"] == "speaker_claim"
        assert claim["verification"] == "unverified"
        assert claim["transfer_event_id"] == conversation_id

        # The speaker's own assertion is not redundantly inserted as something
        # they "heard"; only the other participant receives it.
        assert not any(
            r["source_conversation_id"] == conversation_id
            and r["topic"] == "plant_fiber_present"
            for r in information_receipts_for("bex")
        )

        context = knowledge_context_for("aris")
        assert "unverified claim" in context
        assert "Bex" in context
        assert "Plant Fiber" in context

        payload = knowledge_payload("aris")
        assert payload["exists"] is True
        assert payload["citizen_id"] == "aris"
        assert "seed_site" in payload["locations"]
        assert payload["locations"]["seed_site"]["current_direct_observation"] is True
        assert "resin_grove" in payload["locations"]
        assert any(
            f["topic"] == "plant_fiber_present"
            for f in payload["locations"]["resin_grove"]["facts"]
        )

        # Retrying the same claim projection is idempotent because each receipt
        # has a stable source key.
        from agent_city.provenance import record_face_to_face_claims
        record_face_to_face_claims(
            conversation_id,
            [{
                "speaker": "initiator",
                "subject_type": "location",
                "subject_id": "resin_grove",
                "topic": "plant_fiber_present",
                "value": "I saw Plant Fiber at Resin Grove during my last trip.",
            }],
        )
        assert len([
            r for r in information_receipts_for("aris")
            if r["source_conversation_id"] == conversation_id
            and r["topic"] == "plant_fiber_present"
        ]) == 1

        # Complete the talk before testing new jobs.
        with connect() as conn:
            talk = conn.execute("SELECT * FROM jobs WHERE id = ?", (talk_job_id,)).fetchone()
        complete_due_jobs(int(talk["end_minute"]))

        # Visitor access distinguishes initiator and target correctly.
        ensure_visitor("N7")
        with connect() as conn:
            set_meta(conn, "sim_minute", 800)
            for citizen_id in ("cato", "iri"):
                conn.execute(
                    """
                    UPDATE citizens
                    SET location_id = 'seed_site',
                        location = 'Seed Site',
                        active_job_id = NULL,
                        current_activity = 'Available',
                        energy = 100
                    WHERE id = ?
                    """,
                    (citizen_id,),
                )
            conn.commit()

        ok, _ = start_action(
            "cato",
            {
                "action": "talk",
                "target": "iri",
                "reason": "Check availability status.",
            },
        )
        assert ok

        cato_access = visit_access_payload("N7", "cato")
        iri_access = visit_access_payload("N7", "iri")
        assert cato_access["status"] == "citizen_talking"
        assert cato_access["other_citizen_id"] == "iri"
        assert cato_access["other_citizen_name"] == "Iri"
        assert iri_access["status"] == "citizen_talking"
        assert iri_access["other_citizen_id"] == "cato"
        assert iri_access["other_citizen_name"] == "Cato"
        assert "Iri" in cato_access["reason"]
        assert "Cato" in iri_access["reason"]

        # A co-located citizen doing another physical job is busy, not remote.
        with connect() as conn:
            talk_job = conn.execute(
                "SELECT * FROM jobs WHERE id = (SELECT active_job_id FROM citizens WHERE id = 'cato')"
            ).fetchone()
        complete_due_jobs(int(talk_job["end_minute"]))

        # Failed talk completion releases them, allowing a work job next.
        with connect() as conn:
            set_meta(conn, "sim_minute", 900)
            conn.execute(
                """
                UPDATE citizens
                SET location_id = 'seed_site', location = 'Seed Site',
                    active_job_id = NULL, current_activity = 'Available', energy = 50
                WHERE id = 'cato'
                """
            )
            conn.commit()

        ok, _ = start_action(
            "cato",
            {
                "action": "wait",
                "target": "seed_site",
                "reason": "Observe the settlement.",
            },
        )
        assert ok
        busy = visit_access_payload("N7", "cato")
        assert busy["status"] == "citizen_busy"
        assert busy["accessible"] is False
        assert "busy" in busy["reason"].lower()

        # Remote remains distinct and does not leak the local busy detail.
        with connect() as conn:
            conn.execute(
                "UPDATE visitor_presence SET location_id = 'resin_grove' WHERE visitor = 'N7'"
            )
            conn.commit()
        remote = visit_access_payload("N7", "cato")
        assert remote["status"] == "remote"
        assert "busy" not in remote["reason"].lower()

        # Startup schema migration is idempotent.
        ensure_information_schema()
        ensure_information_schema()

        import main as app_module
        assert app_module.app.title == "Agent City"

        print("Agent City v0.6 communication provenance smoke test passed.")


if __name__ == "__main__":
    main()
