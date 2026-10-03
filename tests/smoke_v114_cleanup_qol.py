from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.db as db
import agent_city.updater as updater


def main() -> None:
    # Runtime asset cleanup: verified PNG remains authoritative; obsolete WebP is gone.
    aris_world = ROOT / "static" / "assets" / "citizens" / "aris" / "world"
    assert (aris_world / "front.png").exists()
    assert not (aris_world / "front.webp").exists()

    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    updater_py = (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")

    # UI contracts exist without changing Simulation authority.
    assert 'id="history-search"' in index
    assert 'id="clear-history-search"' in index
    assert 'id="create-backup"' in index
    assert 'id="backup-status-text"' in index
    assert 'q: historySearchQuery' in app_js
    assert 'fetch("/api/admin/backup", { method: "POST" })' in app_js
    assert ".history-search-bar" in styles
    assert '@app.post("/api/admin/backup")' in main_py
    assert "q: str = \"\"" in main_py
    assert "sqlite3.connect(source_db)" in updater_py
    assert 'prefix: str = "before_update"' in updater_py

    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        data_dir = project / "data"
        backups_dir = project / "backups"
        project.mkdir(parents=True)
        data_dir.mkdir(parents=True)
        (project / "main.py").write_text("print('backup fixture')\n", encoding="utf-8")
        (project / "VERSION").write_text("1.1.4-test\n", encoding="utf-8")

        # Redirect canonical DB/updater globals to this isolated fixture.
        db.DB_PATH = data_dir / "agent_city.db"
        updater.PROJECT_ROOT = project
        updater.DATA_DIR = data_dir
        updater.BACKUP_DIR = backups_dir
        updater.STAGING_DIR = project / "update_staging"
        updater.SETTINGS_PATH = data_dir / "update_settings.json"
        updater.VERSION_PATH = project / "VERSION"

        from agent_city.db import connect, init_db

        init_db()
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO citizen_conversations
                (sim_minute, location_id, initiator_id, target_id,
                 initiator_text, target_text, summary)
                VALUES
                (1000, 'resin_grove', 'cato', 'bex',
                 'I noticed the resin plots again.',
                 'We can inspect them later.',
                 'Cato and Bex discussed the resin plots.'),
                (1010, 'rocky_basin', 'aris', 'iri',
                 'The quarry route is clear.',
                 'I will note that.',
                 'Aris and Iri discussed the quarry route.')
                """
            )
            conn.execute(
                "INSERT INTO history(sim_minute, category, message) VALUES (1000, 'world', 'Resin Grove inspection completed.')"
            )
            conn.execute(
                "INSERT INTO history(sim_minute, category, message) VALUES (1010, 'maintenance', 'Charging Station remains operational.')"
            )
            conn.commit()

        # Import after DB redirect so endpoint functions read this fixture.
        import main as app_main

        resin = app_main.get_records_history(q="resin")
        assert resin["query"] == "resin"
        assert resin["conversations"]["total"] == 1
        assert resin["conversations"]["items"][0]["initiator_name"] == "Cato"
        assert resin["chronology"]["total"] == 1
        assert "Resin Grove" in resin["chronology"]["items"][0]["message"]

        cato = app_main.get_records_history(q="cato")
        assert cato["conversations"]["total"] == 1
        assert cato["chronology"]["total"] == 0

        missing = app_main.get_records_history(q="no-such-history-term")
        assert missing["conversations"]["total"] == 0
        assert missing["chronology"]["total"] == 0

        # Manual backup uses SQLite's online backup API and leaves live state intact.
        result = app_main.create_manual_backup()
        assert result["ok"] is True
        assert result["backup_name"].startswith("manual_")
        backup_dir = Path(result["backup_dir"])
        backup_db = backup_dir / "data" / "agent_city.db"
        code_zip = backup_dir / "program_files.zip"
        info_path = backup_dir / "backup_info.json"
        assert backup_db.exists()
        assert code_zip.exists()
        assert info_path.exists()

        with sqlite3.connect(backup_db) as conn:
            assert conn.execute("SELECT COUNT(*) FROM citizens").fetchone()[0] == 6
            assert conn.execute("SELECT COUNT(*) FROM citizen_conversations").fetchone()[0] == 2
            assert conn.execute("SELECT COUNT(*) FROM history").fetchone()[0] >= 4

        with zipfile.ZipFile(code_zip, "r") as archive:
            assert "main.py" in archive.namelist()

        info = json.loads(info_path.read_text(encoding="utf-8"))
        assert info["kind"] == "manual"
        assert info["version"] == "1.1.4-test"

        with connect() as conn:
            assert conn.execute("SELECT COUNT(*) FROM citizen_conversations").fetchone()[0] == 2

    print("Agent City v1.1.4 cleanup/QoL smoke passed.")


if __name__ == "__main__":
    main()
