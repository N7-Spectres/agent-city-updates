from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent_city.updater as updater
import update_runner


def main() -> None:
    updater_py = (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    runner_py = (ROOT / "update_runner.py").read_text(encoding="utf-8")

    assert "def cleanup_stale_update_staging()" in updater_py
    assert "cleanup_stale_update_staging()" in main_py
    assert "cleanup_stale_update_staging()" in updater_py.split("async def stage_update", 1)[1]
    assert "def cleanup_installed_staging(" in runner_py
    assert "cleanup_installed_staging(project_root, staging_dir)" in runner_py

    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        staging = project / "update_staging"
        staging.mkdir(parents=True)

        updater.PROJECT_ROOT = project
        updater.STAGING_DIR = staging

        # Ordinary stale update payloads are removed completely.
        (staging / "v_1.0.0").mkdir()
        (staging / "v_1.0.0" / "update.zip").write_text("old", encoding="utf-8")
        (staging / "v_1.1.0").mkdir()
        (staging / "loose.tmp").write_text("old", encoding="utf-8")

        result = updater.cleanup_stale_update_staging()
        assert result["skipped"] is False
        assert set(result["removed"]) == {"v_1.0.0", "v_1.1.0", "loose.tmp"}
        assert result["errors"] == []
        assert list(staging.iterdir()) == []

        # Any active updater handoff freezes cleanup rather than risking the
        # staging tree currently being installed.
        active = staging / "v_1.1.6"
        active.mkdir()
        (staging / "update_job.json").write_text("{}", encoding="utf-8")
        protected = updater.cleanup_stale_update_staging()
        assert protected["skipped"] is True
        assert protected["reason"] == "active_update_handoff"
        assert active.exists()
        assert (staging / "update_job.json").exists()

        # The launcher handoff flag alone also protects the whole staging tree.
        (staging / "update_job.json").unlink()
        (staging / "launcher_exit_for_update.flag").write_text("{}", encoding="utf-8")
        protected_flag = updater.cleanup_stale_update_staging()
        assert protected_flag["skipped"] is True
        assert active.exists()

        # Once the handoff is gone, normal startup cleanup can remove leftovers.
        (staging / "launcher_exit_for_update.flag").unlink()
        final = updater.cleanup_stale_update_staging()
        assert final["skipped"] is False
        assert final["removed"] == ["v_1.1.6"]
        assert list(staging.iterdir()) == []

        # The update runner removes only the top-level workspace containing the
        # package it just installed, never the staging root itself or siblings.
        completed = staging / "v_1.1.7"
        package_root = completed / "extracted" / "agent-city-release"
        package_root.mkdir(parents=True)
        (package_root / "main.py").write_text("print('new')", encoding="utf-8")
        sibling = staging / "v_other"
        sibling.mkdir()

        update_runner.cleanup_installed_staging(project, package_root)
        assert not completed.exists()
        assert sibling.exists()
        assert staging.exists()

        # Unexpected paths outside update_staging are never removed.
        outside = project / "outside"
        outside.mkdir()
        update_runner.cleanup_installed_staging(project, outside)
        assert outside.exists()

    print("Agent City v1.1.6 staging-cleanup smoke passed.")


if __name__ == "__main__":
    main()
