from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ASSET_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "asset_worker.db"
RENDER_TIERS = {"individual", "bundle", "storage"}


@dataclass(frozen=True)
class AssetSpec:
    source_type: str
    source_id: str
    source_revision: str
    render_tier: str
    visual_kind: str
    generator_key: str
    spec_json: dict[str, Any]
    spec_version: int = 1

    def validate(self) -> None:
        for field_name, value in (
            ("source_type", self.source_type),
            ("source_id", self.source_id),
            ("source_revision", self.source_revision),
            ("visual_kind", self.visual_kind),
            ("generator_key", self.generator_key),
        ):
            if not str(value or "").strip():
                raise ValueError(f"{field_name} is required")
        if self.render_tier not in RENDER_TIERS:
            raise ValueError(f"Unsupported render tier: {self.render_tier}")
        if int(self.spec_version) < 1:
            raise ValueError("spec_version must be >= 1")
        if not isinstance(self.spec_json, dict):
            raise ValueError("spec_json must be an object")


class AssetQueue:
    """
    Presentation-only persistent queue.

    This database is intentionally separate from Agent City's physical save. It
    may cache specs/jobs/artifacts, but it cannot create or mutate Simulation
    objects, resources, equipment, quantities, or outcomes.
    """

    def __init__(self, db_path: str | Path = ASSET_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS asset_specs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_revision TEXT NOT NULL,
                    spec_version INTEGER NOT NULL,
                    render_tier TEXT NOT NULL,
                    visual_kind TEXT NOT NULL,
                    generator_key TEXT NOT NULL,
                    spec_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    UNIQUE (
                        source_type,
                        source_id,
                        source_revision,
                        spec_version,
                        generator_key
                    )
                );

                CREATE TABLE IF NOT EXISTS asset_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_spec_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    priority INTEGER NOT NULL DEFAULT 100,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    worker_id TEXT,
                    claimed_at INTEGER,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    completed_at INTEGER,
                    error_code TEXT,
                    error_text TEXT,
                    output_path TEXT,
                    output_format TEXT,
                    content_hash TEXT,
                    generator_version TEXT,
                    FOREIGN KEY(asset_spec_id) REFERENCES asset_specs(id)
                );

                CREATE INDEX IF NOT EXISTS idx_asset_jobs_claim
                ON asset_jobs(status, priority DESC, id);

                CREATE INDEX IF NOT EXISTS idx_asset_specs_source
                ON asset_specs(source_type, source_id, id DESC);
                """
            )

    def enqueue(self, spec: AssetSpec, *, priority: int = 100) -> dict[str, Any]:
        spec.validate()
        now = int(time.time())
        canonical_spec = json.dumps(spec.spec_json, sort_keys=True, separators=(",", ":"))

        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO asset_specs
                (source_type, source_id, source_revision, spec_version,
                 render_tier, visual_kind, generator_key, spec_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    spec.source_type,
                    spec.source_id,
                    spec.source_revision,
                    int(spec.spec_version),
                    spec.render_tier,
                    spec.visual_kind,
                    spec.generator_key,
                    canonical_spec,
                    now,
                ),
            )
            row = conn.execute(
                """
                SELECT * FROM asset_specs
                WHERE source_type = ?
                  AND source_id = ?
                  AND source_revision = ?
                  AND spec_version = ?
                  AND generator_key = ?
                """,
                (
                    spec.source_type,
                    spec.source_id,
                    spec.source_revision,
                    int(spec.spec_version),
                    spec.generator_key,
                ),
            ).fetchone()
            spec_id = int(row["id"])

            existing = conn.execute(
                """
                SELECT * FROM asset_jobs
                WHERE asset_spec_id = ?
                  AND status IN ('queued', 'working', 'ready')
                ORDER BY id DESC LIMIT 1
                """,
                (spec_id,),
            ).fetchone()
            if existing:
                return dict(existing)

            cur = conn.execute(
                """
                INSERT INTO asset_jobs
                (asset_spec_id, status, priority, created_at, updated_at)
                VALUES (?, 'queued', ?, ?, ?)
                """,
                (spec_id, int(priority), now, now),
            )
            job_id = int(cur.lastrowid)
            conn.commit()
            return dict(conn.execute("SELECT * FROM asset_jobs WHERE id = ?", (job_id,)).fetchone())

    def claim_next(self, worker_id: str) -> dict[str, Any] | None:
        worker_id = str(worker_id or "").strip()
        if not worker_id:
            raise ValueError("worker_id is required")

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                """
                SELECT * FROM asset_jobs
                WHERE status = 'queued'
                ORDER BY priority DESC, id
                LIMIT 1
                """
            ).fetchone()
            if not row:
                conn.commit()
                return None

            now = int(time.time())
            conn.execute(
                """
                UPDATE asset_jobs
                SET status = 'working',
                    worker_id = ?,
                    claimed_at = ?,
                    attempt_count = attempt_count + 1,
                    updated_at = ?
                WHERE id = ? AND status = 'queued'
                """,
                (worker_id, now, now, int(row["id"])),
            )
            conn.commit()
            return self.get_job(int(row["id"]), include_spec=True)
        finally:
            conn.close()

    def get_job(self, job_id: int, *, include_spec: bool = False) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM asset_jobs WHERE id = ?",
                (int(job_id),),
            ).fetchone()
            if not row:
                return None
            payload = dict(row)
            if include_spec:
                spec = conn.execute(
                    "SELECT * FROM asset_specs WHERE id = ?",
                    (int(row["asset_spec_id"]),),
                ).fetchone()
                if spec:
                    spec_payload = dict(spec)
                    spec_payload["spec_json"] = json.loads(spec_payload["spec_json"])
                    payload["spec"] = spec_payload
            return payload

    def mark_ready(
        self,
        job_id: int,
        *,
        output_path: str,
        output_format: str,
        content_hash: str,
        generator_version: str,
    ) -> dict[str, Any]:
        now = int(time.time())
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE asset_jobs
                SET status = 'ready',
                    output_path = ?,
                    output_format = ?,
                    content_hash = ?,
                    generator_version = ?,
                    completed_at = ?,
                    updated_at = ?,
                    error_code = NULL,
                    error_text = NULL
                WHERE id = ? AND status = 'working'
                """,
                (
                    str(output_path),
                    str(output_format),
                    str(content_hash),
                    str(generator_version),
                    now,
                    now,
                    int(job_id),
                ),
            )
            if cur.rowcount != 1:
                raise ValueError("Only a working asset job can be marked ready")
            conn.commit()
        return self.get_job(job_id, include_spec=True)

    def mark_failed(self, job_id: int, *, error_code: str, error_text: str = "") -> dict[str, Any]:
        now = int(time.time())
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE asset_jobs
                SET status = 'failed',
                    error_code = ?,
                    error_text = ?,
                    completed_at = ?,
                    updated_at = ?
                WHERE id = ? AND status = 'working'
                """,
                (
                    str(error_code)[:120],
                    str(error_text)[:1200],
                    now,
                    now,
                    int(job_id),
                ),
            )
            if cur.rowcount != 1:
                raise ValueError("Only a working asset job can be marked failed")
            conn.commit()
        return self.get_job(job_id, include_spec=True)
