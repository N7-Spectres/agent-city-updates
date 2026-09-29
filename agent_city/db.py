import secrets
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "agent_city.db"

STARTING_CITIZENS = [
    ("aris", "Aris", "Extraction / prospecting"),
    ("bex", "Bex", "Fabrication"),
    ("cato", "Cato", "Logistics / resource planning"),
    ("iri", "Iri", "Construction"),
    ("noma", "Noma", "Research / experimentation"),
    ("vale", "Vale", "Generalist / cooperation"),
]

STARTING_STRUCTURES = [
    ("Habitat / Workshop", 100.0),
    ("Solar Array", 100.0),
    ("Battery Bank", 100.0),
    ("Charging Station", 100.0),
    ("Storage Unit", 100.0),
    ("Basic Workbench", 100.0),
    ("Crude Smelter", 100.0),
]

STARTING_RESOURCES = {
    "Processed structural material": 120,
    "Conductive wire": 80,
    "Mechanical components": 60,
    "Lubricant": 40,
    "Fasteners": 100,
    "Battery cells": 24,
    "Basic electronics": 30,
}

LOCATIONS = [
    ("seed_site", "Seed Site", "Starter settlement and shared infrastructure.", 1),
    ("northern_ridge", "Northern Ridge", "Raised rocky terrain north of Seed Site.", 1),
    ("rocky_basin", "Rocky Basin", "Broken basin terrain east of Seed Site.", 1),
    ("southern_flats", "Southern Flats", "Open mineral flats south of Seed Site.", 1),
    ("resin_grove", "Resin Grove", "Sparse native vegetation west of Seed Site.", 1),
]

ROUTES = [
    ("seed_site", "northern_ridge", 1.8),
    ("seed_site", "rocky_basin", 1.4),
    ("seed_site", "southern_flats", 2.1),
    ("seed_site", "resin_grove", 1.2),
]

DEPOSITS = [
    ("dep_ferrite", "northern_ridge", "Ferrite Stone", 240.0, 0),
    ("dep_veyra", "northern_ridge", "Veyra Ore", 120.0, 0),
    ("dep_silicate", "rocky_basin", "Silicate", 300.0, 0),
    ("dep_copper", "rocky_basin", "Copper-like Ore", 180.0, 0),
    ("dep_carbon", "southern_flats", "Carbonaceous Rock", 260.0, 0),
    ("dep_clay", "southern_flats", "Clay", 420.0, 0),
    ("dep_fiber", "resin_grove", "Plant Fiber", 180.0, 0),
    ("dep_resin", "resin_grove", "Native Resin", 90.0, 0),
]

# Stable local coordinates are deliberately simple groundwork, not free-roam geography.
# Future structures may use coordinates between landmarks without changing location IDs.
LOCATION_COORDINATES = {
    "seed_site": (0.0, 0.0),
    "northern_ridge": (0.0, 1.8),
    "rocky_basin": (1.4, 0.0),
    "southern_flats": (0.0, -2.1),
    "resin_grove": (-1.2, 0.0),
}

# Hidden physical truth. These rows are seeded into world_properties but NEVER
# exposed directly through the ordinary state snapshot. A fact becomes visible
# only through a validated discovery record.
WORLD_PROPERTIES = [
    ("prop_ferrite_field", "material", "Ferrite Stone", "field_response", "strong response to a simple magnetic field", None, "electrical_assay"),
    ("prop_veyra_thermal", "material", "Veyra Ore", "thermal_stability", "retains structural coherence through moderate heating", None, "thermal_assay"),
    ("prop_silicate_phase", "material", "Silicate", "heated_phase", "forms a glassy phase after sustained heating", None, "thermal_assay"),
    ("prop_copper_conduct", "material", "Copper-like Ore", "conductivity", "shows strong electrical conductivity after basic mechanical separation", None, "electrical_assay"),
    ("prop_carbon_resist", "material", "Carbonaceous Rock", "electrical_resistance", "shows high electrical resistance in a dry sample", None, "electrical_assay"),
    ("prop_clay_form", "material", "Clay", "compressive_formability", "holds shaped form well under slow mechanical compression", None, "mechanical_assay"),
    ("prop_fiber_tensile", "material", "Plant Fiber", "tensile_behavior", "has high tensile strength for its mass", None, "mechanical_assay"),
    ("prop_resin_cure", "material", "Native Resin", "thermal_curing", "hardens significantly after controlled moderate heating", None, "thermal_assay"),
    ("prop_north_exposure", "location", "northern_ridge", "surface_exposure", "ridge surface is highly exposed with loose stone accumulation", None, "field_survey"),
    ("prop_basin_stability", "location", "rocky_basin", "surface_stability", "fractured basin includes stable shelves between loose rubble zones", None, "field_survey"),
    ("prop_flats_compaction", "location", "southern_flats", "surface_compaction", "broad sections of the flats are firm and consistently compacted", None, "field_survey"),
    ("prop_grove_growth", "location", "resin_grove", "growth_pattern", "fibrous growth is concentrated around resin-producing native plants", None, "field_survey"),
]


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def add_column_if_missing(conn: sqlite3.Connection, table: str, column_sql: str, name: str) -> None:
    if name not in table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_sql}")


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS citizens (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                aptitude TEXT NOT NULL,
                energy REAL NOT NULL DEFAULT 100,
                integrity REAL NOT NULL DEFAULT 100,
                joint_wear REAL NOT NULL DEFAULT 0,
                battery_health REAL NOT NULL DEFAULT 100,
                last_service_minute INTEGER,
                location TEXT NOT NULL DEFAULT 'Seed Site',
                current_activity TEXT NOT NULL DEFAULT 'Orienting at Seed Site',
                position_x_m REAL,
                position_y_m REAL
            );

            CREATE TABLE IF NOT EXISTS structures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                condition REAL NOT NULL,
                location_id TEXT,
                x_km REAL,
                y_km REAL,
                kind TEXT NOT NULL DEFAULT 'structure',
                provides_charging INTEGER NOT NULL DEFAULT 0,
                project_id INTEGER,
                last_service_minute INTEGER,
                use_count INTEGER NOT NULL DEFAULT 0,
                x_m REAL,
                y_m REAL
            );

            CREATE TABLE IF NOT EXISTS resources (
                name TEXT PRIMARY KEY,
                amount REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_minute INTEGER NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_minute INTEGER NOT NULL,
                visitor TEXT NOT NULL,
                citizen_id TEXT NOT NULL,
                visitor_text TEXT NOT NULL,
                citizen_text TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                mapped INTEGER NOT NULL DEFAULT 1,
                surveyed INTEGER NOT NULL DEFAULT 0,
                x_km REAL,
                y_km REAL,
                x_m REAL,
                y_m REAL
            );

            CREATE TABLE IF NOT EXISTS routes (
                a TEXT NOT NULL,
                b TEXT NOT NULL,
                distance_km REAL NOT NULL,
                PRIMARY KEY(a, b)
            );

            CREATE TABLE IF NOT EXISTS deposits (
                id TEXT PRIMARY KEY,
                location_id TEXT NOT NULL,
                material TEXT NOT NULL,
                amount REAL NOT NULL,
                discovered INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS citizen_inventory (
                citizen_id TEXT NOT NULL,
                material TEXT NOT NULL,
                amount REAL NOT NULL DEFAULT 0,
                PRIMARY KEY(citizen_id, material)
            );

            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT NOT NULL,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                owner_citizen_id TEXT,
                location_id TEXT,
                condition REAL NOT NULL DEFAULT 100,
                extraction_speed_multiplier REAL NOT NULL DEFAULT 1.0,
                cargo_bonus REAL NOT NULL DEFAULT 0,
                created_job_id INTEGER,
                created_minute INTEGER NOT NULL,
                last_service_minute INTEGER,
                use_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blueprint_id TEXT NOT NULL,
                name TEXT NOT NULL,
                location_id TEXT NOT NULL,
                x_km REAL,
                y_km REAL,
                status TEXT NOT NULL DEFAULT 'planned',
                created_by TEXT NOT NULL,
                created_minute INTEGER NOT NULL,
                reserved_minute INTEGER,
                started_minute INTEGER,
                completed_minute INTEGER,
                active_job_id INTEGER,
                resulting_structure_id INTEGER,
                x_m REAL,
                y_m REAL
            );

            CREATE TABLE IF NOT EXISTS project_materials (
                project_id INTEGER NOT NULL,
                material TEXT NOT NULL,
                required_amount REAL NOT NULL,
                reserved_amount REAL NOT NULL DEFAULT 0,
                PRIMARY KEY(project_id, material)
            );

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

            CREATE INDEX IF NOT EXISTS idx_discoveries_subject
            ON discoveries(discovery_kind, subject_type, subject_id, id);

            CREATE INDEX IF NOT EXISTS idx_discoveries_job
            ON discoveries(source_job_id, id);

            CREATE TABLE IF NOT EXISTS citizen_knowledge (
                citizen_id TEXT NOT NULL,
                discovery_id INTEGER NOT NULL,
                learned_minute INTEGER NOT NULL,
                acquisition_kind TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                verification_state TEXT NOT NULL DEFAULT 'verified',
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

            CREATE TABLE IF NOT EXISTS learned_processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                citizen_id TEXT NOT NULL,
                process_key TEXT NOT NULL,
                name TEXT NOT NULL,
                process_kind TEXT NOT NULL,
                source_discovery_id INTEGER NOT NULL,
                learned_minute INTEGER NOT NULL,
                UNIQUE(citizen_id, process_key)
            );

            CREATE TABLE IF NOT EXISTS maintenance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL UNIQUE,
                citizen_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                before_value REAL,
                after_value REAL,
                materials_json TEXT,
                outcome TEXT NOT NULL,
                sim_minute INTEGER NOT NULL,
                summary TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_maintenance_events_target
            ON maintenance_events(target_type, target_id, id);

            CREATE TABLE IF NOT EXISTS generated_deposits (
                id TEXT PRIMARY KEY,
                source_kind TEXT NOT NULL DEFAULT 'procedural',
                material TEXT NOT NULL,
                source_chunk_x INTEGER NOT NULL,
                source_chunk_y INTEGER NOT NULL,
                center_x_m REAL NOT NULL,
                center_y_m REAL NOT NULL,
                long_axis_m REAL NOT NULL,
                short_axis_m REAL NOT NULL,
                angle_rad REAL NOT NULL,
                richness REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_generated_deposits_center
            ON generated_deposits(center_x_m, center_y_m);

            CREATE TABLE IF NOT EXISTS spatial_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                observer_id TEXT NOT NULL,
                source_job_id INTEGER,
                observation_kind TEXT NOT NULL,
                detail_level TEXT NOT NULL DEFAULT 'field',
                frame_id TEXT NOT NULL,
                x_m REAL NOT NULL,
                y_m REAL NOT NULL,
                radius_m REAL NOT NULL DEFAULT 1,
                observed_minute INTEGER NOT NULL,
                terrain_class TEXT NOT NULL,
                elevation_m REAL NOT NULL,
                geology_class TEXT NOT NULL,
                deposit_id TEXT,
                material TEXT,
                summary TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_spatial_observations_observer
            ON spatial_observations(observer_id, observed_minute, id);

            CREATE INDEX IF NOT EXISTS idx_spatial_observations_deposit
            ON spatial_observations(deposit_id, id);

            CREATE TABLE IF NOT EXISTS shared_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visitor TEXT NOT NULL,
                citizen_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                objective TEXT NOT NULL,
                frame_id TEXT NOT NULL,
                start_x_m REAL NOT NULL,
                start_y_m REAL NOT NULL,
                target_x_m REAL NOT NULL,
                target_y_m REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'proposed',
                proposed_minute INTEGER NOT NULL,
                accepted_minute INTEGER,
                started_minute INTEGER,
                completed_minute INTEGER,
                source_visit_id INTEGER,
                source_exchange_id INTEGER,
                tool_equipment_id INTEGER,
                citizen_job_id INTEGER,
                observation_id INTEGER,
                outcome TEXT,
                failure_reason TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_shared_activities_participants
            ON shared_activities(visitor, citizen_id, status, id);

            CREATE TABLE IF NOT EXISTS citizen_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT NOT NULL,
                created_minute INTEGER NOT NULL,
                updated_minute INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                current_intent TEXT NOT NULL,
                next_step TEXT NOT NULL,
                unresolved_question TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_citizen_plans_owner
            ON citizen_plans(owner_id, status, updated_minute, id);

            CREATE TABLE IF NOT EXISTS plan_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                owner_id TEXT NOT NULL,
                sim_minute INTEGER NOT NULL,
                transition_type TEXT NOT NULL,
                from_status TEXT,
                to_status TEXT NOT NULL,
                source_job_id INTEGER,
                summary TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_plan_transitions_plan
            ON plan_transitions(plan_id, sim_minute, id);

            CREATE TABLE IF NOT EXISTS plan_memory_sources (
                plan_id INTEGER NOT NULL,
                transition_id INTEGER NOT NULL,
                owner_id TEXT NOT NULL,
                memory_event_id INTEGER NOT NULL,
                source_role TEXT NOT NULL,
                linked_minute INTEGER NOT NULL,
                PRIMARY KEY(plan_id, transition_id, memory_event_id, source_role)
            );

            CREATE INDEX IF NOT EXISTS idx_plan_memory_sources_owner
            ON plan_memory_sources(owner_id, memory_event_id, plan_id);

            CREATE TABLE IF NOT EXISTS practice_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                citizen_id TEXT NOT NULL,
                job_id INTEGER NOT NULL UNIQUE,
                plan_id INTEGER,
                activity_type TEXT NOT NULL,
                job_status TEXT NOT NULL,
                outcome TEXT NOT NULL,
                completed_minute INTEGER NOT NULL,
                location_id TEXT,
                target TEXT,
                material TEXT,
                project_id INTEGER,
                observation_id INTEGER,
                shared_activity_id INTEGER,
                summary TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_practice_events_citizen
            ON practice_events(citizen_id, activity_type, completed_minute, id);

            CREATE TABLE IF NOT EXISTS guided_practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER UNIQUE,
                teacher_id TEXT NOT NULL,
                learner_id TEXT NOT NULL,
                activity_family TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                started_minute INTEGER NOT NULL,
                completed_minute INTEGER,
                source_conversation_id INTEGER,
                teacher_practice_count INTEGER NOT NULL DEFAULT 0,
                learner_practice_count INTEGER NOT NULL DEFAULT 0,
                consumed_by_job_id INTEGER,
                summary TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_guided_practice_learner
            ON guided_practice_sessions(learner_id, activity_family, status, id);

            CREATE INDEX IF NOT EXISTS idx_guided_practice_teacher
            ON guided_practice_sessions(teacher_id, activity_family, status, id);

            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                citizen_id TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                material TEXT,
                amount REAL,
                start_minute INTEGER NOT NULL,
                end_minute INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                detail TEXT,
                project_id INTEGER,
                outcome TEXT,
                experiment_method TEXT,
                result_discovery_id INTEGER,
                maintenance_event_id INTEGER,
                spatial_frame_id TEXT,
                start_x_m REAL,
                start_y_m REAL,
                target_x_m REAL,
                target_y_m REAL,
                path_distance_m REAL,
                terrain_multiplier REAL,
                result_observation_id INTEGER,
                shared_activity_id INTEGER,
                plan_id INTEGER,
                guided_practice_id INTEGER
            );

            CREATE TABLE IF NOT EXISTS citizen_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sim_minute INTEGER NOT NULL,
                location_id TEXT NOT NULL,
                initiator_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                initiator_text TEXT NOT NULL,
                target_text TEXT NOT NULL,
                summary TEXT NOT NULL,
                source_job_id INTEGER
            );

            CREATE INDEX IF NOT EXISTS idx_citizen_conversations_people
            ON citizen_conversations(initiator_id, target_id, id);

            CREATE TABLE IF NOT EXISTS visitor_presence (
                visitor TEXT PRIMARY KEY,
                location_id TEXT NOT NULL DEFAULT 'seed_site',
                from_location_id TEXT,
                to_location_id TEXT,
                travel_start_minute INTEGER,
                travel_end_minute INTEGER,
                x_m REAL,
                y_m REAL
            );
            """
        )

        add_column_if_missing(conn, "citizens", "location_id TEXT NOT NULL DEFAULT 'seed_site'", "location_id")
        add_column_if_missing(conn, "citizens", "last_planned_minute INTEGER NOT NULL DEFAULT 0", "last_planned_minute")
        add_column_if_missing(conn, "citizens", "active_job_id INTEGER", "active_job_id")
        add_column_if_missing(conn, "citizens", "battery_health REAL NOT NULL DEFAULT 100", "battery_health")
        add_column_if_missing(conn, "citizens", "last_service_minute INTEGER", "last_service_minute")
        add_column_if_missing(conn, "citizens", "position_x_m REAL", "position_x_m")
        add_column_if_missing(conn, "citizens", "position_y_m REAL", "position_y_m")
        add_column_if_missing(conn, "jobs", "intent_reason TEXT", "intent_reason")
        add_column_if_missing(conn, "jobs", "project_id INTEGER", "project_id")
        add_column_if_missing(conn, "jobs", "outcome TEXT", "outcome")
        add_column_if_missing(conn, "jobs", "experiment_method TEXT", "experiment_method")
        add_column_if_missing(conn, "jobs", "result_discovery_id INTEGER", "result_discovery_id")
        add_column_if_missing(conn, "jobs", "maintenance_event_id INTEGER", "maintenance_event_id")
        add_column_if_missing(conn, "jobs", "spatial_frame_id TEXT", "spatial_frame_id")
        add_column_if_missing(conn, "jobs", "start_x_m REAL", "start_x_m")
        add_column_if_missing(conn, "jobs", "start_y_m REAL", "start_y_m")
        add_column_if_missing(conn, "jobs", "target_x_m REAL", "target_x_m")
        add_column_if_missing(conn, "jobs", "target_y_m REAL", "target_y_m")
        add_column_if_missing(conn, "jobs", "path_distance_m REAL", "path_distance_m")
        add_column_if_missing(conn, "jobs", "terrain_multiplier REAL", "terrain_multiplier")
        add_column_if_missing(conn, "jobs", "result_observation_id INTEGER", "result_observation_id")
        add_column_if_missing(conn, "jobs", "shared_activity_id INTEGER", "shared_activity_id")
        add_column_if_missing(conn, "jobs", "plan_id INTEGER", "plan_id")
        add_column_if_missing(conn, "jobs", "guided_practice_id INTEGER", "guided_practice_id")
        add_column_if_missing(conn, "spatial_observations", "detail_level TEXT NOT NULL DEFAULT 'field'", "detail_level")
        add_column_if_missing(conn, "deposits", "discoverer_id TEXT", "discoverer_id")
        add_column_if_missing(conn, "deposits", "discovered_minute INTEGER", "discovered_minute")
        add_column_if_missing(conn, "locations", "x_km REAL", "x_km")
        add_column_if_missing(conn, "locations", "y_km REAL", "y_km")
        add_column_if_missing(conn, "locations", "x_m REAL", "x_m")
        add_column_if_missing(conn, "locations", "y_m REAL", "y_m")
        add_column_if_missing(conn, "structures", "location_id TEXT", "location_id")
        add_column_if_missing(conn, "structures", "x_km REAL", "x_km")
        add_column_if_missing(conn, "structures", "y_km REAL", "y_km")
        add_column_if_missing(conn, "structures", "kind TEXT NOT NULL DEFAULT 'structure'", "kind")
        add_column_if_missing(conn, "structures", "provides_charging INTEGER NOT NULL DEFAULT 0", "provides_charging")
        add_column_if_missing(conn, "structures", "project_id INTEGER", "project_id")
        add_column_if_missing(conn, "structures", "last_service_minute INTEGER", "last_service_minute")
        add_column_if_missing(conn, "structures", "use_count INTEGER NOT NULL DEFAULT 0", "use_count")
        add_column_if_missing(conn, "structures", "x_m REAL", "x_m")
        add_column_if_missing(conn, "structures", "y_m REAL", "y_m")
        add_column_if_missing(conn, "equipment", "last_service_minute INTEGER", "last_service_minute")
        add_column_if_missing(conn, "equipment", "use_count INTEGER NOT NULL DEFAULT 0", "use_count")
        add_column_if_missing(conn, "projects", "x_m REAL", "x_m")
        add_column_if_missing(conn, "projects", "y_m REAL", "y_m")
        add_column_if_missing(conn, "visitor_presence", "x_m REAL", "x_m")
        add_column_if_missing(conn, "visitor_presence", "y_m REAL", "y_m")
        add_column_if_missing(conn, "citizen_conversations", "source_job_id INTEGER", "source_job_id")
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_citizen_conversations_source_job
            ON citizen_conversations(source_job_id)
            WHERE source_job_id IS NOT NULL
            """
        )

        if get_meta(conn, "planet_seed") is None:
            set_meta(conn, "planet_seed", secrets.token_hex(16))

        if get_meta(conn, "initialized") is None:
            set_meta(conn, "initialized", "true")
            set_meta(conn, "sim_minute", "360")
            set_meta(conn, "paused", "false")
            set_meta(conn, "time_ratio", "4.0")
            set_meta(conn, "ollama_model", "qwen3.5:9b")

            for cid, name, aptitude in STARTING_CITIZENS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO citizens
                    (id, name, aptitude, energy, integrity, joint_wear, location, current_activity, location_id)
                    VALUES (?, ?, ?, 100, 100, 0, 'Seed Site', 'Orienting at Seed Site', 'seed_site')
                    """,
                    (cid, name, aptitude),
                )

            for name, condition in STARTING_STRUCTURES:
                conn.execute(
                    "INSERT OR IGNORE INTO structures(name, condition) VALUES (?, ?)",
                    (name, condition),
                )

            for name, amount in STARTING_RESOURCES.items():
                conn.execute(
                    "INSERT OR IGNORE INTO resources(name, amount) VALUES (?, ?)",
                    (name, amount),
                )

            add_history(conn, 360, "origin", "Six mechanical citizens activated at Seed Site.")
            add_history(conn, 360, "world", "Seed Site systems operational. No long-term objective has been assigned.")

        for lid, name, desc, mapped in LOCATIONS:
            surveyed = 1 if lid == "seed_site" else 0
            conn.execute(
                """
                INSERT OR IGNORE INTO locations(id, name, description, mapped, surveyed)
                VALUES (?, ?, ?, ?, ?)
                """,
                (lid, name, desc, mapped, surveyed),
            )

        for a, b, distance in ROUTES:
            conn.execute("INSERT OR IGNORE INTO routes(a, b, distance_km) VALUES (?, ?, ?)", (a, b, distance))
            conn.execute("INSERT OR IGNORE INTO routes(a, b, distance_km) VALUES (?, ?, ?)", (b, a, distance))

        for did, location_id, material, amount, discovered in DEPOSITS:
            conn.execute(
                """
                INSERT OR IGNORE INTO deposits(id, location_id, material, amount, discovered)
                VALUES (?, ?, ?, ?, ?)
                """,
                (did, location_id, material, amount, discovered),
            )

        for prop in WORLD_PROPERTIES:
            conn.execute(
                """
                INSERT OR IGNORE INTO world_properties
                (id, subject_type, subject_id, property_key, value_text, unit, assay_method)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                prop,
            )

        for lid, (x_km, y_km) in LOCATION_COORDINATES.items():
            conn.execute(
                """
                UPDATE locations
                SET x_km = COALESCE(x_km, ?),
                    y_km = COALESCE(y_km, ?),
                    x_m = COALESCE(x_m, ?),
                    y_m = COALESCE(y_m, ?)
                WHERE id = ?
                """,
                (x_km, y_km, x_km * 1000.0, y_km * 1000.0, lid),
            )

        # Existing v0.4.x structures are all physically at Seed Site.
        conn.execute(
            """
            UPDATE structures
            SET location_id = COALESCE(location_id, 'seed_site'),
                x_km = COALESCE(x_km, 0.0),
                y_km = COALESCE(y_km, 0.0),
                x_m = COALESCE(x_m, x_km * 1000.0, 0.0),
                y_m = COALESCE(y_m, y_km * 1000.0, 0.0)
            """
        )
        conn.execute("UPDATE structures SET kind = 'charger', provides_charging = 1 WHERE name = 'Charging Station'")
        conn.execute("UPDATE structures SET kind = 'storage' WHERE name = 'Storage Unit'")
        conn.execute("UPDATE structures SET kind = 'workbench' WHERE name = 'Basic Workbench'")
        conn.execute("UPDATE structures SET kind = 'smelter' WHERE name = 'Crude Smelter'")

        conn.execute("UPDATE citizens SET location_id = 'seed_site' WHERE location_id IS NULL OR location_id = ''")
        conn.execute(
            """
            UPDATE citizens
            SET position_x_m = COALESCE(
                    position_x_m,
                    (SELECT x_m FROM locations WHERE locations.id = citizens.location_id),
                    0.0
                ),
                position_y_m = COALESCE(
                    position_y_m,
                    (SELECT y_m FROM locations WHERE locations.id = citizens.location_id),
                    0.0
                )
            """
        )
        conn.execute(
            """
            UPDATE projects
            SET x_m = COALESCE(x_m, x_km * 1000.0),
                y_m = COALESCE(y_m, y_km * 1000.0)
            """
        )
        conn.execute(
            """
            UPDATE visitor_presence
            SET x_m = COALESCE(
                    x_m,
                    (SELECT x_m FROM locations WHERE locations.id = visitor_presence.location_id),
                    0.0
                ),
                y_m = COALESCE(
                    y_m,
                    (SELECT y_m FROM locations WHERE locations.id = visitor_presence.location_id),
                    0.0
                )
            """
        )

        from .spatial import legacy_body_geometry
        planet_seed = get_meta(conn, "planet_seed") or ""
        for dep in conn.execute(
            """
            SELECT d.id, d.material, l.x_m, l.y_m
            FROM deposits d
            JOIN locations l ON l.id = d.location_id
            """
        ).fetchall():
            body = legacy_body_geometry(
                planet_seed,
                str(dep["id"]),
                str(dep["material"]),
                float(dep["x_m"] or 0.0),
                float(dep["y_m"] or 0.0),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO generated_deposits
                (id, source_kind, material, source_chunk_x, source_chunk_y,
                 center_x_m, center_y_m, long_axis_m, short_axis_m, angle_rad, richness)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    body["id"], body["source_kind"], body["material"],
                    body["source_chunk_x"], body["source_chunk_y"],
                    body["center_x_m"], body["center_y_m"],
                    body["long_axis_m"], body["short_axis_m"],
                    body["angle_rad"], body["richness"],
                ),
            )
        conn.execute(
            "UPDATE jobs SET outcome = 'legacy_complete' WHERE status = 'complete' AND outcome IS NULL"
        )
        conn.execute(
            "UPDATE citizens SET battery_health = 100 WHERE battery_health IS NULL OR battery_health <= 0"
        )
        if get_meta(conn, "maintenance_wear_minute") is None:
            set_meta(conn, "maintenance_wear_minute", get_meta(conn, "sim_minute") or "360")

        if get_meta(conn, "v0_2_migrated") is None:
            current = int(get_meta(conn, "sim_minute") or "360")
            add_history(conn, current, "system", "Agent City action layer activated.")
            set_meta(conn, "v0_2_migrated", "true")

        # Backfill who personally discovered already-known deposits when old survey jobs exist.
        for dep in conn.execute(
            "SELECT id, location_id FROM deposits WHERE discovered = 1 AND discoverer_id IS NULL"
        ).fetchall():
            survey = conn.execute(
                """
                SELECT citizen_id, end_minute
                FROM jobs
                WHERE action = 'survey' AND target = ? AND status = 'complete'
                ORDER BY end_minute DESC, id DESC LIMIT 1
                """,
                (dep["location_id"],),
            ).fetchone()
            if survey:
                conn.execute(
                    "UPDATE deposits SET discoverer_id = ?, discovered_minute = COALESCE(discovered_minute, ?) WHERE id = ?",
                    (survey["citizen_id"], int(survey["end_minute"]), dep["id"]),
                )

        # Migrate pre-v0.6 deposit discoveries into the explicit discovery/knowledge model.
        for dep in conn.execute(
            """
            SELECT d.id, d.location_id, d.material, d.discoverer_id, d.discovered_minute
            FROM deposits d
            WHERE d.discovered = 1
              AND d.discoverer_id IS NOT NULL
              AND d.discovered_minute IS NOT NULL
            """
        ).fetchall():
            existing = conn.execute(
                """
                SELECT id FROM discoveries
                WHERE discovery_kind = 'deposit'
                  AND subject_id = ?
                  AND citizen_id = ?
                ORDER BY id LIMIT 1
                """,
                (dep["id"], dep["discoverer_id"]),
            ).fetchone()
            if existing:
                discovery_id = int(existing["id"])
            else:
                source_job = conn.execute(
                    """
                    SELECT id FROM jobs
                    WHERE action = 'survey'
                      AND citizen_id = ?
                      AND target = ?
                      AND end_minute = ?
                    ORDER BY id LIMIT 1
                    """,
                    (dep["discoverer_id"], dep["location_id"], int(dep["discovered_minute"])),
                ).fetchone()
                cur = conn.execute(
                    """
                    INSERT INTO discoveries
                    (discovery_kind, subject_type, subject_id, property_id, citizen_id,
                     location_id, source_job_id, discovered_minute, summary)
                    VALUES ('deposit', 'deposit', ?, NULL, ?, ?, ?, ?, ?)
                    """,
                    (
                        dep["id"],
                        dep["discoverer_id"],
                        dep["location_id"],
                        int(source_job["id"]) if source_job else None,
                        int(dep["discovered_minute"]),
                        f"Confirmed deposit of {dep['material']} at {dep['location_id']}.",
                    ),
                )
                discovery_id = int(cur.lastrowid)

            conn.execute(
                """
                INSERT OR IGNORE INTO citizen_knowledge
                (citizen_id, discovery_id, learned_minute, acquisition_kind,
                 source_type, source_id, verification_state)
                VALUES (?, ?, ?, 'direct_survey', 'discovery', ?, 'verified')
                """,
                (
                    dep["discoverer_id"],
                    discovery_id,
                    int(dep["discovered_minute"]),
                    str(discovery_id),
                ),
            )

        from .continuity import sync_practice_events_in_conn
        sync_practice_events_in_conn(conn)

        conn.commit()


def get_meta(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_meta(conn: sqlite3.Connection, key: str, value: Any) -> None:
    conn.execute(
        """
        INSERT INTO meta(key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, str(value)),
    )


def add_history(conn: sqlite3.Connection, sim_minute: int, category: str, message: str) -> None:
    conn.execute(
        "INSERT INTO history(sim_minute, category, message) VALUES (?, ?, ?)",
        (sim_minute, category, message),
    )


def snapshot() -> dict[str, Any]:
    """
    Safe civilization-facing state.

    Hidden world_properties are intentionally absent. Undiscovered deposits are
    also absent rather than returned with a discovered=false flag.
    """
    with connect() as conn:
        citizens = [dict(r) for r in conn.execute("SELECT * FROM citizens ORDER BY rowid")]
        structures = [dict(r) for r in conn.execute("SELECT * FROM structures ORDER BY id")]

        def condition_state(value: float) -> str:
            if value <= 20:
                return "critical"
            if value < 60:
                return "degraded"
            if value < 90:
                return "service_due"
            return "nominal"

        for citizen in citizens:
            battery = float(citizen.get("battery_health") or 0)
            wear = float(citizen.get("joint_wear") or 0)
            citizen["battery_state"] = condition_state(battery)
            citizen["usable_energy_capacity"] = battery
            citizen["battery_replacement_due"] = battery < 85
            citizen["chassis_service_state"] = (
                "critical" if wear >= 60
                else "service_due" if wear >= 12
                else "nominal"
            )
            citizen["chassis_service_due"] = wear >= 12

        for structure in structures:
            condition = float(structure.get("condition") or 0)
            factor = max(0.0, min(1.0, condition / 100.0)) if condition > 20 else 0.0
            structure["condition_state"] = condition_state(condition)
            structure["operational"] = condition > 20
            structure["efficiency_multiplier"] = factor
            structure["service_due"] = condition < 90
        resources = [dict(r) for r in conn.execute("SELECT * FROM resources ORDER BY name")]
        history = [dict(r) for r in conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 60")]
        locations = [dict(r) for r in conn.execute("SELECT * FROM locations ORDER BY rowid")]

        # Only validated deposit discoveries cross the ordinary read boundary.
        deposits = [
            dict(r) for r in conn.execute(
                """
                SELECT id, location_id, material, 1 AS discovered,
                       discoverer_id, discovered_minute
                FROM deposits
                WHERE discovered = 1
                ORDER BY location_id, material
                """
            )
        ]

        inventory = [dict(r) for r in conn.execute("SELECT * FROM citizen_inventory WHERE amount > 0 ORDER BY citizen_id, material")]
        equipment = [dict(r) for r in conn.execute("SELECT * FROM equipment ORDER BY id")]
        for item in equipment:
            condition = float(item.get("condition") or 0)
            factor = max(0.0, min(1.0, condition / 100.0)) if condition > 20 else 0.0
            base_speed = float(item.get("extraction_speed_multiplier") or 1.0)
            item["condition_state"] = condition_state(condition)
            item["operational"] = condition > 20
            item["service_due"] = condition < 90
            item["effective_cargo_bonus"] = float(item.get("cargo_bonus") or 0) * factor
            item["effective_extraction_speed_multiplier"] = (
                1.0 + (base_speed - 1.0) * factor if factor > 0 else 1.0
            )
        projects = [dict(r) for r in conn.execute("SELECT * FROM projects ORDER BY id DESC LIMIT 50")]
        project_materials = [dict(r) for r in conn.execute("SELECT * FROM project_materials ORDER BY project_id, material")]
        jobs = [dict(r) for r in conn.execute("SELECT * FROM jobs WHERE status = 'active' ORDER BY id")]
        routes = [dict(r) for r in conn.execute("SELECT * FROM routes ORDER BY a, b")]
        plans = [
            dict(r) for r in conn.execute(
                """
                SELECT * FROM citizen_plans
                ORDER BY
                    CASE status WHEN 'active' THEN 0 WHEN 'paused' THEN 1 ELSE 2 END,
                    updated_minute DESC, id DESC
                LIMIT 80
                """
            )
        ]
        for plan in plans:
            pid = int(plan["id"])
            plan["memory_event_ids"] = [
                int(row["memory_event_id"])
                for row in conn.execute(
                    """
                    SELECT DISTINCT memory_event_id
                    FROM plan_memory_sources
                    WHERE plan_id = ?
                    ORDER BY memory_event_id
                    """,
                    (pid,),
                )
            ]
        plan_transitions = [
            dict(r) for r in conn.execute(
                "SELECT * FROM plan_transitions ORDER BY id DESC LIMIT 160"
            )
        ]
        practice_events = [
            dict(r) for r in conn.execute(
                "SELECT * FROM practice_events ORDER BY id DESC LIMIT 160"
            )
        ]
        guided_practice_sessions = [
            dict(r) for r in conn.execute(
                """
                SELECT * FROM guided_practice_sessions
                ORDER BY COALESCE(completed_minute, started_minute) DESC, id DESC
                LIMIT 80
                """
            )
        ]

        from .exploration import active_local_movement_payload, shared_activity_payload
        sim_now = int(get_meta(conn, "sim_minute") or "360")
        for citizen in citizens:
            movement = active_local_movement_payload(conn, citizen["id"], sim_now)
            citizen["local_movement"] = movement
            if movement:
                citizen["position_x_m"] = movement["x_m"]
                citizen["position_y_m"] = movement["y_m"]

        shared_activities = []
        for row in conn.execute(
            """
            SELECT id FROM shared_activities
            WHERE status IN ('proposed', 'active', 'complete', 'failed')
            ORDER BY id DESC LIMIT 60
            """
        ):
            payload = shared_activity_payload(conn, int(row["id"]), sim_now)
            if payload:
                shared_activities.append(payload)

        discovery_rows = conn.execute(
            """
            SELECT d.*,
                   wp.property_key,
                   wp.value_text,
                   wp.unit,
                   dep.material AS deposit_material
            FROM discoveries d
            LEFT JOIN world_properties wp ON wp.id = d.property_id
            LEFT JOIN deposits dep
              ON d.discovery_kind = 'deposit' AND dep.id = d.subject_id
            ORDER BY d.id
            """
        ).fetchall()
        discoveries = [dict(r) for r in discovery_rows]

        citizen_knowledge = [
            dict(r) for r in conn.execute(
                """
                SELECT ck.*,
                       d.discovery_kind, d.subject_type, d.subject_id, d.property_id,
                       d.location_id, d.discovered_minute, d.summary,
                       wp.property_key, wp.value_text, wp.unit,
                       dep.material AS deposit_material
                FROM citizen_knowledge ck
                JOIN discoveries d ON d.id = ck.discovery_id
                LEFT JOIN world_properties wp ON wp.id = d.property_id
                LEFT JOIN deposits dep
                  ON d.discovery_kind = 'deposit' AND dep.id = d.subject_id
                ORDER BY ck.citizen_id, ck.learned_minute, ck.discovery_id
                """
            )
        ]

        experiment_results = [
            dict(r) for r in conn.execute(
                "SELECT * FROM experiment_results ORDER BY id DESC LIMIT 60"
            )
        ]
        learned_processes = [
            dict(r) for r in conn.execute(
                "SELECT * FROM learned_processes ORDER BY citizen_id, id"
            )
        ]
        maintenance_events = [
            dict(r) for r in conn.execute(
                "SELECT * FROM maintenance_events ORDER BY id DESC LIMIT 80"
            )
        ]
        from .spatial import SPATIAL_FRAME_ID, safe_observation_payload
        spatial_observations = [
            safe_observation_payload(r) for r in conn.execute(
                "SELECT * FROM spatial_observations ORDER BY id DESC LIMIT 120"
            )
        ]

        # Location cards begin sparse and accumulate only validated facts.
        facts_by_location: dict[str, list[dict[str, Any]]] = {loc["id"]: [] for loc in locations}
        for loc in locations:
            if loc["surveyed"]:
                facts_by_location[loc["id"]].append({
                    "kind": "survey",
                    "label": "Field survey completed",
                })
        for discovery in discoveries:
            location_id = discovery.get("location_id")
            if location_id not in facts_by_location:
                continue
            if discovery["discovery_kind"] == "deposit":
                facts_by_location[location_id].append({
                    "kind": "deposit",
                    "discovery_id": discovery["id"],
                    "label": f"Confirmed deposit: {discovery.get('deposit_material') or discovery['subject_id']}",
                })
            elif discovery["subject_type"] == "location" and discovery.get("property_key"):
                facts_by_location[location_id].append({
                    "kind": "property",
                    "discovery_id": discovery["id"],
                    "property_key": discovery["property_key"],
                    "value": discovery["value_text"],
                    "unit": discovery["unit"],
                })
        for loc in locations:
            loc["known_facts"] = facts_by_location.get(loc["id"], [])

        citizen_conversations = [
            dict(r) for r in conn.execute(
                """
                SELECT cc.*,
                       'citizen_conversation' AS source_type,
                       cc.id AS source_id,
                       cc.id AS transfer_event_id,
                       ci.name AS initiator_name,
                       ct.name AS target_name,
                       l.name AS location_name
                FROM citizen_conversations cc
                JOIN citizens ci ON ci.id = cc.initiator_id
                JOIN citizens ct ON ct.id = cc.target_id
                JOIN locations l ON l.id = cc.location_id
                ORDER BY cc.id DESC LIMIT 30
                """
            )
        ]

        return {
            "sim_minute": int(get_meta(conn, "sim_minute") or "360"),
            "paused": (get_meta(conn, "paused") or "false") == "true",
            "time_ratio": float(get_meta(conn, "time_ratio") or "4.0"),
            "ollama_model": get_meta(conn, "ollama_model") or "qwen3.5:9b",
            "citizens": citizens,
            "structures": structures,
            "resources": resources,
            "history": history,
            "locations": locations,
            "deposits": deposits,
            "inventory": inventory,
            "equipment": equipment,
            "projects": projects,
            "project_materials": project_materials,
            "jobs": jobs,
            "routes": routes,
            "plans": plans,
            "plan_transitions": plan_transitions,
            "practice_events": practice_events,
            "guided_practice_sessions": guided_practice_sessions,
            "discoveries": discoveries,
            "citizen_knowledge": citizen_knowledge,
            "experiment_results": experiment_results,
            "learned_processes": learned_processes,
            "maintenance_events": maintenance_events,
            "spatial_frame": {
                "id": SPATIAL_FRAME_ID,
                "units": "meters",
                "origin_location_id": "seed_site",
                "frame_type": "local_tangent_plane",
                "x_axis": "east",
                "y_axis": "north",
                "global_mapping": "not_yet_assigned",
            },
            "spatial_observations": spatial_observations,
            "shared_activities": shared_activities,
            "citizen_conversations": citizen_conversations,
        }
