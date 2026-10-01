from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


PRESERVE_NAMES = {".venv", "data", "backups", "update_staging"}


def _log(project_root: Path, message: str) -> None:
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "update_runner.log"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def wait_for_process_exit(pid: int, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            return True
        time.sleep(0.5)
    return False


def replace_program_files(project_root: Path, staging_dir: Path) -> None:
    for item in project_root.iterdir():
        if item.name in PRESERVE_NAMES:
            continue
        if item.name == "update_runner.py":
            continue
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        except FileNotFoundError:
            pass

    for src in staging_dir.iterdir():
        if src.name in PRESERVE_NAMES:
            continue
        dst = project_root / src.name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


def relaunch(project_root: Path, python_exe: str) -> str:
    flags = 0
    if os.name == "nt":
        flags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )

    launcher = project_root / "agent_city_launcher.pyw"
    if launcher.exists():
        command = [python_exe, str(launcher), "--resume-after-update"]
        mode = "desktop launcher"
    else:
        command = [python_exe, "main.py"]
        mode = "direct runtime fallback"

    subprocess.Popen(
        command,
        cwd=str(project_root),
        creationflags=flags,
        close_fds=(os.name != "nt"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    return mode


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: update_runner.py <job.json>")

    job_path = Path(sys.argv[1]).resolve()
    job = json.loads(job_path.read_text(encoding="utf-8"))

    project_root = Path(job["project_root"]).resolve()
    staging_dir = Path(job["staging_dir"]).resolve()
    parent_pid = int(job["parent_pid"])
    python_exe = job["python_exe"]
    target_version = str(job.get("target_version") or "unknown")

    _log(project_root, f"Update runner started for {target_version}; waiting for runtime PID {parent_pid}.")

    if not wait_for_process_exit(parent_pid):
        _log(
            project_root,
            f"Update aborted: runtime PID {parent_pid} did not exit within the safety timeout.",
        )
        raise SystemExit(2)

    time.sleep(0.5)
    _log(project_root, "Runtime stopped. Replacing program files.")
    replace_program_files(project_root, staging_dir)

    mode = relaunch(project_root, python_exe)
    _log(project_root, f"Update files installed. Relaunched through {mode}.")


if __name__ == "__main__":
    main()
