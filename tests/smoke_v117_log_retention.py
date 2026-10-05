from __future__ import annotations

import os
import runpy
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.updater as updater
import update_runner


def main() -> None:
    launcher_path = ROOT / "agent_city_launcher.pyw"
    launcher = launcher_path.read_text(encoding="utf-8")
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")

    compile(launcher, str(launcher_path), "exec")

    for fragment in [
        "LOG_MAX_BYTES = 10 * 1024 * 1024",
        "LOG_BACKUP_COUNT = 3",
        "def _rotate_log_file(",
        "def _relay_process_output(",
        "def _start_log_relay(",
        "stdout=subprocess.PIPE",
        "stderr=subprocess.STDOUT",
        "_start_log_relay(process, SERVER_LOG)",
        "_rotate_log_file(OLLAMA_LOG)",
    ]:
        assert fragment in launcher, fragment

    for fragment in [
        'id="backup-retention"',
        'id="save-backup-retention"',
        'id="backup-retention-status"',
    ]:
        assert fragment in index

    for fragment in [
        "/api/admin/backup-retention",
        "saveBackupRetention",
        "Keep all",
        "total_size_bytes",
    ]:
        assert fragment in app_js or fragment in main_py or fragment in index

    assert ".backup-retention-controls" in styles
    assert "def backup_summary()" in (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")
    assert "def apply_backup_retention()" in (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")
    assert "def save_backup_retention(" in (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        data_dir = root / "data"
        backup_dir = root / "backups"
        data_dir.mkdir()
        backup_dir.mkdir()

        updater.DATA_DIR = data_dir
        updater.BACKUP_DIR = backup_dir
        updater.MAINTENANCE_SETTINGS_PATH = data_dir / "maintenance_settings.json"

        # Twelve fake backups, oldest -> newest.
        for index in range(12):
            path = backup_dir / f"manual_{index:02d}"
            path.mkdir()
            (path / "payload.bin").write_bytes(bytes([index]) * (index + 1))
            (path / "backup_info.json").write_text(
                '{"created_at":"2026-10-01T00:00:00","version":"1.1.6","kind":"manual"}',
                encoding="utf-8",
            )
            stamp = 1_700_000_000 + index
            os.utime(path, (stamp, stamp))

        # Keep all is the default and is non-destructive.
        assert updater.load_maintenance_settings()["backup_retention"] == 0
        keep_all = updater.apply_backup_retention()
        assert keep_all["retention"] == 0
        assert keep_all["removed"] == []
        assert len([p for p in backup_dir.iterdir() if p.is_dir()]) == 12

        summary = updater.backup_summary()
        assert summary["count"] == 12
        assert summary["retention"] == 0
        assert summary["latest"]["name"] == "manual_11"
        assert summary["total_size_bytes"] > 0

        # Only an explicit saved limit may remove older backups.
        assert updater.save_backup_retention(10) == 10
        pruned = updater.apply_backup_retention()
        assert pruned["retention"] == 10
        assert set(pruned["removed"]) == {"manual_00", "manual_01"}
        assert pruned["errors"] == []
        remaining = sorted(p.name for p in backup_dir.iterdir() if p.is_dir())
        assert len(remaining) == 10
        assert "manual_00" not in remaining
        assert "manual_11" in remaining

        try:
            updater.save_backup_retention(7)
            raise AssertionError("Unsupported retention value should fail")
        except ValueError:
            pass

        # Launcher rotation works independently of Windows process APIs.
        launcher_ns = runpy.run_path(str(launcher_path), run_name="agent_city_launcher_test")
        rotate = launcher_ns["_rotate_log_file"]
        log_path = root / "server.log"
        log_path.write_text("a" * 120, encoding="utf-8")
        assert rotate(log_path, max_bytes=100, backup_count=3) is True
        assert not log_path.exists()
        assert (root / "server.log.1").exists()

        # A second rotation shifts prior history without exceeding three generations.
        log_path.write_text("b" * 120, encoding="utf-8")
        assert rotate(log_path, max_bytes=100, backup_count=3) is True
        assert (root / "server.log.1").read_text(encoding="utf-8") == "b" * 120
        assert (root / "server.log.2").read_text(encoding="utf-8") == "a" * 120

        # Update-runner logs use the same bounded-generation policy.
        update_runner.LOG_MAX_BYTES = 100
        update_runner.LOG_BACKUP_COUNT = 3
        runner_log = data_dir / "update_runner.log"
        runner_log.write_text("u" * 120, encoding="utf-8")
        update_runner._rotate_log(runner_log)
        assert (data_dir / "update_runner.log.1").exists()

    print("Agent City v1.1.7 log-rotation / backup-retention smoke passed.")


if __name__ == "__main__":
    main()
