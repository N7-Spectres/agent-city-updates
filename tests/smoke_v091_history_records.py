from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.db as db


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db

        init_db()

        with connect() as conn:
            for i in range(1, 11):
                conn.execute(
                    """
                    INSERT INTO citizen_conversations(
                        sim_minute, location_id, initiator_id, target_id,
                        initiator_text, target_text, summary, source_job_id
                    )
                    VALUES (?, 'seed_site', 'aris', 'bex', ?, ?, ?, NULL)
                    """,
                    (
                        1000 + i,
                        f"Aris line {i}",
                        f"Bex line {i}",
                        f"Conversation summary {i}",
                    ),
                )

            for i in range(1, 20):
                conn.execute(
                    "INSERT INTO history(sim_minute, category, message) VALUES (?, 'event', ?)",
                    (2000 + i, f"Chronology event {i}"),
                )
            conn.commit()

        import main as app_module

        first = app_module.get_records_history(
            conversation_page=1,
            chronology_page=1,
            conversation_page_size=8,
            chronology_page_size=12,
        )
        assert first["conversations"]["total"] == 10
        assert first["conversations"]["total_pages"] == 2
        assert first["conversations"]["page"] == 1
        assert len(first["conversations"]["items"]) == 8
        assert first["conversations"]["items"][0]["summary"] == "Conversation summary 10"

        assert first["chronology"]["total"] == 19
        assert first["chronology"]["total_pages"] == 2
        assert first["chronology"]["page"] == 1
        assert len(first["chronology"]["items"]) == 12
        assert first["chronology"]["items"][0]["message"] == "Chronology event 19"

        second = app_module.get_records_history(
            conversation_page=2,
            chronology_page=2,
            conversation_page_size=8,
            chronology_page_size=12,
        )
        assert len(second["conversations"]["items"]) == 2
        assert len(second["chronology"]["items"]) == 7

        clamped = app_module.get_records_history(
            conversation_page=999,
            chronology_page=999,
            conversation_page_size=8,
            chronology_page_size=12,
        )
        assert clamped["conversations"]["page"] == 2
        assert clamped["chronology"]["page"] == 2

    app = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    assert '@app.get("/api/records/history")' in main_py
    assert "HISTORY_CONVERSATIONS_PER_PAGE = 8" in app
    assert "HISTORY_CHRONOLOGY_PER_PAGE = 12" in app
    assert "openConversationIds = new Set()" in app
    assert 'details.classList' not in app
    assert 'data-conversation-id' in app
    assert 'details.open' in app
    assert "historyConversationPage" in app
    assert "historyChronologyPage" in app
    assert "history-records-grid" in html
    assert "conversation-pagination" in html
    assert "chronology-pagination" in html
    assert ".history-records-grid" in css
    assert "grid-template-columns: minmax(0, 1.65fr) minmax(320px, .85fr)" in css
    assert "@media (max-width: 1050px)" in css

    print("Agent City v0.9.1 History records smoke passed.")


if __name__ == "__main__":
    main()
