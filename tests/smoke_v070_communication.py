from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


class FakeResponse:
    def __init__(self, content: str, status_code: int = 200):
        self._content = content
        self.status_code = status_code
        self.request = httpx.Request("POST", "http://127.0.0.1:11434/api/chat")

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=self.request,
                response=httpx.Response(self.status_code, request=self.request),
            )

    def json(self):
        return {"message": {"content": self._content}}


class FakeAsyncClient:
    queue: list[object] = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        if not self.queue:
            raise AssertionError("FakeAsyncClient queue exhausted")
        item = self.queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def active_job_id(citizen_id: str) -> int:
    from agent_city.db import connect

    with connect() as conn:
        row = conn.execute(
            "SELECT active_job_id FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
        assert row and row["active_job_id"] is not None
        return int(row["active_job_id"])


def job_row(job_id: int) -> dict:
    from agent_city.db import connect

    with connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        assert row
        return dict(row)


def conversation_for_job(job_id: int) -> dict | None:
    from agent_city.db import connect

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM citizen_conversations WHERE source_job_id = ?",
            (job_id,),
        ).fetchone()
        return dict(row) if row else None


def reset_pair(a: str, b: str, minute: int) -> None:
    from agent_city.db import connect, set_meta

    with connect() as conn:
        set_meta(conn, "sim_minute", minute)
        for citizen_id in (a, b):
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


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        import agent_city.comms as comms
        from agent_city.db import connect, init_db
        from agent_city.memory import ensure_memory_schema
        from agent_city.provenance import ensure_information_schema, information_receipts_for
        from agent_city.simulation import complete_due_jobs, start_action
        from agent_city.talk_diagnostics import (
            ensure_talk_diagnostic_schema,
            talk_diagnostics_for,
        )
        from agent_city.visits import ensure_visit_schema

        init_db()
        ensure_visit_schema()
        ensure_memory_schema()
        ensure_information_schema()
        ensure_talk_diagnostic_schema()

        original_client = comms.httpx.AsyncClient
        original_record_dialogue = comms.record_dialogue

        try:
            # 1) Malformed structured dialogue on first attempt retries. A valid
            # second response persists before claim extraction. Broken claim JSON
            # is degraded only and must not erase the raw exchange.
            reset_pair("bex", "aris", 1000)
            ok, _ = start_action(
                "bex",
                {
                    "action": "talk",
                    "target": "aris",
                    "reason": "Check the latest local observations.",
                },
            )
            assert ok
            job_id = active_job_id("bex")

            FakeAsyncClient.queue = [
                FakeResponse("this is not json"),
                FakeResponse(
                    json.dumps(
                        {
                            "initiator_text": "I wanted to compare what we have observed here.",
                            "target_text": "I have only confirmed what is visible at Seed Site.",
                            "summary": "Bex and Aris compared their local observations.",
                        }
                    )
                ),
                FakeResponse("{ definitely not valid claim json"),
            ]
            comms.httpx.AsyncClient = FakeAsyncClient

            result = asyncio.run(
                comms.generate_dialogue(
                    "bex",
                    "aris",
                    "Compare local observations.",
                    "test-model",
                    job_id,
                )
            )
            assert int(result["conversation_id"]) > 0
            stored = conversation_for_job(job_id)
            assert stored is not None
            assert stored["initiator_text"].startswith("I wanted to compare")

            diagnostics = talk_diagnostics_for(job_id)
            codes = [(d["outcome"], d["code"]) for d in diagnostics]
            assert ("retry", "dialogue_malformed_json") in codes
            assert ("success", "dialogue_generated") in codes
            assert ("success", "exchange_persisted") in codes
            assert ("degraded", "claim_malformed_json") in codes

            # Broken claim enrichment creates no fake receipts and does not
            # invalidate the real conversation.
            assert not any(
                r["source_conversation_id"] == stored["id"]
                for r in information_receipts_for("bex")
            )
            assert not any(
                r["source_conversation_id"] == stored["id"]
                for r in information_receipts_for("aris")
            )

            complete_due_jobs(int(job_row(job_id)["end_minute"]))
            assert job_row(job_id)["status"] == "complete"

            # 2) Hard Ollama/network failure produces no transcript and records
            # a precise diagnostic. Physical completion later remains failed.
            reset_pair("cato", "iri", 1200)
            ok, _ = start_action(
                "cato",
                {
                    "action": "talk",
                    "target": "iri",
                    "reason": "Ask a local question.",
                },
            )
            assert ok
            network_job_id = active_job_id("cato")

            request = httpx.Request("POST", "http://127.0.0.1:11434/api/chat")
            FakeAsyncClient.queue = [
                httpx.ConnectError("offline", request=request),
                httpx.ConnectError("offline", request=request),
            ]
            comms.httpx.AsyncClient = FakeAsyncClient

            failed = False
            try:
                asyncio.run(
                    comms.generate_dialogue(
                        "cato",
                        "iri",
                        "Ask a local question.",
                        "test-model",
                        network_job_id,
                    )
                )
            except RuntimeError:
                failed = True
            assert failed
            assert conversation_for_job(network_job_id) is None

            diagnostics = talk_diagnostics_for(network_job_id)
            assert diagnostics[-1]["outcome"] == "failure"
            assert diagnostics[-1]["code"] == "ollama_network_failure"

            complete_due_jobs(int(job_row(network_job_id)["end_minute"]))
            assert job_row(network_job_id)["status"] == "failed"

            with connect() as conn:
                history = [
                    dict(row)
                    for row in conn.execute(
                        "SELECT category, message FROM history ORDER BY id"
                    ).fetchall()
                ]
            assert any(
                row["category"] == "diagnostic"
                and f"Talk job #{network_job_id}" in row["message"]
                and "ollama_network_failure" in row["message"]
                for row in history
            )

            # 3) Persistence/database failure is distinguishable from model
            # generation failure.
            reset_pair("noma", "vale", 1400)
            ok, _ = start_action(
                "noma",
                {
                    "action": "talk",
                    "target": "vale",
                    "reason": "Share a short local note.",
                },
            )
            assert ok
            persistence_job_id = active_job_id("noma")

            FakeAsyncClient.queue = [
                FakeResponse(
                    json.dumps(
                        {
                            "initiator_text": "I have one local note to share.",
                            "target_text": "Go ahead.",
                            "summary": "Noma offered Vale a local note.",
                        }
                    )
                )
            ]
            comms.httpx.AsyncClient = FakeAsyncClient

            def fail_record(*args, **kwargs):
                raise sqlite3.OperationalError("forced persistence failure")

            comms.record_dialogue = fail_record

            failed = False
            try:
                asyncio.run(
                    comms.generate_dialogue(
                        "noma",
                        "vale",
                        "Share a local note.",
                        "test-model",
                        persistence_job_id,
                    )
                )
            except RuntimeError:
                failed = True
            assert failed
            assert conversation_for_job(persistence_job_id) is None

            diagnostics = talk_diagnostics_for(persistence_job_id)
            assert diagnostics[-1]["outcome"] == "failure"
            assert diagnostics[-1]["code"] == "persistence_database_failure"

            comms.record_dialogue = original_record_dialogue
            complete_due_jobs(int(job_row(persistence_job_id)["end_minute"]))
            assert job_row(persistence_job_id)["status"] == "failed"

            # 4) A physical invalidation between generation and persistence is
            # classified separately from a database failure.
            reset_pair("bex", "aris", 1600)
            ok, _ = start_action(
                "bex",
                {
                    "action": "talk",
                    "target": "aris",
                    "reason": "Short test.",
                },
            )
            assert ok
            invalid_job_id = active_job_id("bex")

            FakeAsyncClient.queue = [
                FakeResponse(
                    json.dumps(
                        {
                            "initiator_text": "Quick check.",
                            "target_text": "I am listening.",
                            "summary": "Bex checked in with Aris.",
                        }
                    )
                )
            ]
            comms.httpx.AsyncClient = FakeAsyncClient
            comms.record_dialogue = lambda *args, **kwargs: None

            failed = False
            try:
                asyncio.run(
                    comms.generate_dialogue(
                        "bex",
                        "aris",
                        "Short test.",
                        "test-model",
                        invalid_job_id,
                    )
                )
            except RuntimeError:
                failed = True
            assert failed
            diagnostics = talk_diagnostics_for(invalid_job_id)
            assert diagnostics[-1]["code"] == "physical_talk_invalid_before_persistence"

            print("Agent City v0.7 talk reliability smoke test passed.")

        finally:
            comms.httpx.AsyncClient = original_client
            comms.record_dialogue = original_record_dialogue


if __name__ == "__main__":
    main()
