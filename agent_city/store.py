"""Saving the world to disk (SQLite at data/world.db).

v1's city lives in data/agent_city.db and is never touched by v2, so the old
city stays safe as a backup.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from .citizens import founders
from .world.facility import VISITOR_SPAWN, meeting_seats, starting_facility
from .world.planet import Planet, new_seed

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 1


def db_path() -> Path:
    override = os.environ.get("AGENT_CITY_WORLD_DB")
    if override:
        return Path(override)
    return PROJECT_ROOT / "data" / "world.db"


@contextmanager
def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS structures (
    id TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL,
    x_m REAL NOT NULL, y_m REAL NOT NULL, width_m REAL NOT NULL, depth_m REAL NOT NULL,
    height_m REAL NOT NULL, solid INTEGER NOT NULL, status TEXT NOT NULL,
    shape TEXT NOT NULL, meta TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS deposits (
    id TEXT PRIMARY KEY, material TEXT NOT NULL, x_m REAL NOT NULL, y_m REAL NOT NULL,
    amount_kg REAL NOT NULL, depth_m REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS citizens (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, division TEXT NOT NULL, role TEXT NOT NULL,
    height_m REAL NOT NULL, x_m REAL NOT NULL, y_m REAL NOT NULL, heading REAL NOT NULL,
    energy REAL NOT NULL, condition REAL NOT NULL, activity TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS visitors (
    name TEXT PRIMARY KEY, x_m REAL NOT NULL, y_m REAL NOT NULL, heading REAL NOT NULL,
    updated_at REAL NOT NULL
);
"""


def get_meta(conn, key: str, default: str | None = None) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_meta(conn, key: str, value) -> None:
    conn.execute(
        "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )


def init_world(seed: int | None = None) -> int:
    """Create the world on first start. Returns the planet seed.

    Calling it again on an existing world changes nothing.
    """
    with connect() as conn:
        conn.executescript(SCHEMA)
        existing = get_meta(conn, "seed")
        if existing is not None:
            return int(existing)

        seed = int(seed) if seed is not None else new_seed()
        planet = Planet(seed)
        set_meta(conn, "schema_version", SCHEMA_VERSION)
        set_meta(conn, "seed", seed)
        set_meta(conn, "created_at", time.time())
        set_meta(conn, "sim_seconds", 8 * 3600)  # first morning, 08:00
        set_meta(conn, "time_scale", 4)
        set_meta(conn, "paused", 0)

        for s in starting_facility():
            conn.execute(
                "INSERT INTO structures VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (s.id, s.kind, s.name, s.x_m, s.y_m, s.width_m, s.depth_m, s.height_m,
                 int(s.solid), s.status, s.shape, json.dumps(s.meta)),
            )
        for d in planet.deposits():
            conn.execute(
                "INSERT INTO deposits VALUES (?,?,?,?,?,?)",
                (d.id, d.material, d.x_m, d.y_m, d.amount_kg, d.depth_m),
            )
        # The founders begin seated around the meeting table.
        for citizen, (x, y, heading) in zip(founders(), meeting_seats(6)):
            conn.execute(
                "INSERT INTO citizens VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (citizen["id"], citizen["name"], citizen["division"], "director",
                 citizen["height_m"], x, y, heading, 1.0, 1.0, "at the meeting table"),
            )
        return seed


def ensure_visitor(conn, name: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM visitors WHERE name = ?", (name,)).fetchone()
    if row:
        return row
    x, y, heading = VISITOR_SPAWN
    conn.execute("INSERT INTO visitors VALUES (?,?,?,?,?)", (name, x, y, heading, time.time()))
    return conn.execute("SELECT * FROM visitors WHERE name = ?", (name,)).fetchone()


def load_structures(conn) -> list[dict]:
    rows = conn.execute("SELECT * FROM structures ORDER BY rowid").fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["solid"] = bool(item["solid"])
        meta = json.loads(item.pop("meta") or "{}")
        if meta:
            item["meta"] = meta
        out.append(item)
    return out
