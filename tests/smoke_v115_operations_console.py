from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.db as db
import agent_city.updater as updater


def main() -> None:
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    for fragment in [
        'id="system-health-summary"',
        'id="refresh-system-health"',
        'id="copy-support-bundle"',
        'id="backup-history-list"',
        'id="refresh-backups"',
    ]:
        assert fragment in index

    for fragment in [
        "/api/admin/system-health",
        "/api/admin/backups",
        "/api/admin/support-bundle",
        "refreshOperationsConsole",
        "Copy Support Bundle",
        "formatByteCount",
    ]:
        assert fragment in app_js or fragment in main_py

    assert ".system-health-summary" in styles
    assert ".backup-history-item" in styles
    assert '@app.get("/api/admin/system-health")' in main_py
    assert '@app.get("/api/admin/backups")' in main_py
    assert '@app.get("/api/admin/support-bundle")' in main_py

    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        data_dir = project / "data"
        backup_dir = project / "backups"
        staging_dir = project / "update_staging"
        project.mkdir(parents=True)
        data_dir.mkdir(parents=True)
        staging_dir.mkdir(parents=True)

        (project / "main.py").write_text("print('fixture')\n", encoding="utf-8")
        (project / "VERSION").write_text("1.1.5-test\n", encoding="utf-8")

        db.DB_PATH = data_dir / "agent_city.db"
        updater.PROJECT_ROOT = project
        updater.DATA_DIR = data_dir
        updater.BACKUP_DIR = backup_dir
        updater.STAGING_DIR = staging_dir
        updater.SETTINGS_PATH = data_dir / "update_settings.json"
        updater.VERSION_PATH = project / "VERSION"

        from agent_city.db import connect, init_db

        init_db()
        with connect() as conn:
            conn.execute(
                "INSERT INTO history(sim_minute, category, message) VALUES (900, 'diagnostic', 'Fixture event')"
            )
            conn.commit()

        # Local desktop/system evidence.
        (data_dir / "launcher_status.json").write_text(
            json.dumps(
                {
                    "state": "Running",
                    "text": "Agent City is running.",
                    "launcher_pid": 111,
                    "updated_at": "2026-10-02T20:00:00",
                }
            ),
            encoding="utf-8",
        )
        (data_dir / "server.pid").write_text("222\n", encoding="utf-8")
        (data_dir / "launcher.log").write_text("launcher line 1\nlauncher line 2\n", encoding="utf-8")
        (data_dir / "server.log").write_text("server line 1\nserver line 2\n", encoding="utf-8")
        (data_dir / "ollama.log").write_text("ollama line\n", encoding="utf-8")
        (data_dir / "update_runner.log").write_text("updater line\n", encoding="utf-8")
        (staging_dir / "old-stage").mkdir()

        updater.save_settings("https://example.com/update.json")

        import main as app_main

        app_main.PROJECT_ROOT = project
        app_main.OLLAMA_URL = "http://127.0.0.1:1"

        backup_result = app_main.create_manual_backup()
        assert backup_result["ok"] is True

        listed = app_main.get_backups()
        assert listed["count"] == 1
        assert listed["backups"][0]["name"].startswith("manual_")
        assert listed["backups"][0]["version"] == "1.1.5-test"
        assert listed["backups"][0]["has_database"] is True
        assert listed["backups"][0]["has_program_archive"] is True
        assert "intentionally not exposed" in listed["note"]

        health = asyncio.run(app_main.get_system_health())
        assert health["version"] == "1.1.5-test"
        assert health["database"]["status"] == "ok"
        assert health["database"]["detail"].lower() == "ok"
        assert health["launcher"]["status"]["state"] == "Running"
        assert health["launcher"]["server_pid"] == 222
        assert health["backups"]["count"] == 1
        assert health["backups"]["latest"]["name"].startswith("manual_")
        assert health["updates"]["feed_configured"] is True
        assert "old-stage" in health["updates"]["staging_entries"]
        assert health["ollama"]["online"] is False
        assert health["logs"]["launcher"]["exists"] is True
        assert health["logs"]["server"]["exists"] is True

        bundle = asyncio.run(app_main.get_support_bundle())
        assert bundle["bundle_type"] == "agent_city_support"
        assert bundle["health"]["database"]["status"] == "ok"
        assert bundle["troubleshooting_snapshot"]["snapshot_type"] == "agent_city_troubleshooting"
        assert bundle["recent_logs"]["launcher"]["tail"].endswith("launcher line 2")
        assert bundle["recent_logs"]["server"]["tail"].endswith("server line 2")
        assert bundle["privacy"]["local_only_until_copied"] is True
        assert bundle["privacy"]["hidden_world_seed_included"] is False
        assert bundle["privacy"]["undiscovered_world_truth_included"] is False

        serialized = json.dumps(bundle)
        assert "planet_seed" not in serialized
        assert "generated_deposits" not in serialized
        assert "world_properties" not in serialized

    print("Agent City v1.1.5 operations-console smoke passed.")


if __name__ == "__main__":
    main()
