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
                location TEXT NOT NULL DEFAULT 'Seed Site',
                current_activity TEXT NOT NULL DEFAULT 'Orienting at Seed Site'
            );

            CREATE TABLE IF NOT EXISTS structures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                condition REAL NOT NULL
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
                surveyed INTEGER NOT NULL DEFAULT 0
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
                detail TEXT
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
                travel_end_minute INTEGER
            );
            """
        )

        add_column_if_missing(conn, "citizens", "location_id TEXT NOT NULL DEFAULT 'seed_site'", "location_id")
        add_column_if_missing(conn, "citizens", "last_planned_minute INTEGER NOT NULL DEFAULT 0", "last_planned_minute")
        add_column_if_missing(conn, "citizens", "active_job_id INTEGER", "active_job_id")
        add_column_if_missing(conn, "jobs", "intent_reason TEXT", "intent_reason")
        add_column_if_missing(conn, "deposits", "discoverer_id TEXT", "discoverer_id")
        add_column_if_missing(conn, "deposits", "discovered_minute INTEGER", "discovered_minute")
        add_column_if_missing(conn, "citizen_conversations", "source_job_id INTEGER", "source_job_id")
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_citizen_conversations_source_job
            ON citizen_conversations(source_job_id)
            WHERE source_job_id IS NOT NULL
            """
        )

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

        conn.execute("UPDATE citizens SET location_id = 'seed_site' WHERE location_id IS NULL OR location_id = ''")

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
    with connect() as conn:
        citizens = [dict(r) for r in conn.execute("SELECT * FROM citizens ORDER BY rowid")]
        structures = [dict(r) for r in conn.execute("SELECT * FROM structures ORDER BY id")]
        resources = [dict(r) for r in conn.execute("SELECT * FROM resources ORDER BY name")]
        history = [dict(r) for r in conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 60")]
        locations = [dict(r) for r in conn.execute("SELECT * FROM locations ORDER BY rowid")]
        deposits = [dict(r) for r in conn.execute("SELECT * FROM deposits ORDER BY location_id, material")]
        inventory = [dict(r) for r in conn.execute("SELECT * FROM citizen_inventory WHERE amount > 0 ORDER BY citizen_id, material")]
        jobs = [dict(r) for r in conn.execute("SELECT * FROM jobs WHERE status = 'active' ORDER BY id")]
        routes = [dict(r) for r in conn.execute("SELECT * FROM routes ORDER BY a, b")]
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
            "jobs": jobs,
            "routes": routes,
            "citizen_conversations": citizen_conversations,
        }
