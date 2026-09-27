from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


PRESERVE_NAMES = {".venv", "data", "backups", "update_staging"}


def wait_for_process_exit(pid: int, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            return
        time.sleep(0.5)


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


def relaunch(project_root: Path, python_exe: str) -> None:
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    subprocess.Popen(
        [python_exe, "main.py"],
        cwd=str(project_root),
        creationflags=flags,
        close_fds=(os.name != "nt"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: update_runner.py <job.json>")

    job_path = Path(sys.argv[1]).resolve()
    job = json.loads(job_path.read_text(encoding="utf-8"))

    project_root = Path(job["project_root"]).resolve()
    staging_dir = Path(job["staging_dir"]).resolve()
    parent_pid = int(job["parent_pid"])
    python_exe = job["python_exe"]

    wait_for_process_exit(parent_pid)
    time.sleep(0.5)
    replace_program_files(project_root, staging_dir)
    relaunch(project_root, python_exe)


if __name__ == "__main__":
    main()
