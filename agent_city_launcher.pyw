from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
APP_URL = "http://127.0.0.1:8000/"
STATE_URL = "http://127.0.0.1:8000/api/state"
LAUNCHER_LOG = DATA_DIR / "launcher.log"
SERVER_LOG = DATA_DIR / "server.log"
STARTUP_TIMEOUT_SECONDS = 30.0


def _log(message: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LAUNCHER_LOG.open("a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def _show_error(message: str) -> None:
    _log(f"ERROR: {message}")
    if os.name == "nt":
        try:
            ctypes.windll.user32.MessageBoxW(0, message, "Agent City", 0x10)
            return
        except Exception:
            pass


def _agent_city_is_ready() -> bool:
    try:
        with urllib.request.urlopen(STATE_URL, timeout=0.75) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
            return isinstance(payload, dict) and "citizens" in payload and "sim_minute" in payload
    except Exception:
        return False


def _python_without_console() -> str:
    venv_pythonw = PROJECT_ROOT / ".venv" / "Scripts" / "pythonw.exe"
    if os.name == "nt" and venv_pythonw.exists():
        return str(venv_pythonw)

    current = Path(sys.executable)
    if os.name == "nt":
        if current.name.lower() == "pythonw.exe":
            return str(current)
        sibling = current.with_name("pythonw.exe")
        if sibling.exists():
            return str(sibling)
    return str(current)


def _start_server() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    python_exe = _python_without_console()
    command = [python_exe, str(PROJECT_ROOT / "main.py")]

    creationflags = 0
    if os.name == "nt":
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    server_log = SERVER_LOG.open("a", encoding="utf-8")
    try:
        subprocess.Popen(
            command,
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=server_log,
            stderr=server_log,
            creationflags=creationflags,
            start_new_session=(os.name != "nt"),
        )
    finally:
        server_log.close()

    _log(f"Started Agent City with {python_exe}")


def _wait_until_ready(timeout: float = STARTUP_TIMEOUT_SECONDS) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _agent_city_is_ready():
            return True
        time.sleep(0.35)
    return False


def main() -> None:
    try:
        if _agent_city_is_ready():
            _log("Agent City was already running; opening the browser only.")
            webbrowser.open(APP_URL, new=2)
            return

        _start_server()
        if not _wait_until_ready():
            _show_error(
                "Agent City did not finish starting. "
                "Check data\\server.log inside the Agent City folder for details."
            )
            return

        _log("Agent City is ready; opening the browser.")
        webbrowser.open(APP_URL, new=2)
    except Exception as exc:
        _show_error(f"Agent City could not start: {exc}")


if __name__ == "__main__":
    main()
