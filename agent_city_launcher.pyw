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
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
APP_URL = "http://127.0.0.1:8000/"
STATE_URL = "http://127.0.0.1:8000/api/state"
SHUTDOWN_URL = "http://127.0.0.1:8000/api/launcher/shutdown"

LAUNCHER_LOG = DATA_DIR / "launcher.log"
SERVER_LOG = DATA_DIR / "server.log"
STATUS_PATH = DATA_DIR / "launcher_status.json"
COMMAND_PATH = DATA_DIR / "launcher_command.json"
LAUNCHER_PID_PATH = DATA_DIR / "launcher.pid"
SERVER_PID_PATH = DATA_DIR / "server.pid"
UPDATE_FLAG = PROJECT_ROOT / "update_staging" / "launcher_exit_for_update.flag"
TRAY_SCRIPT = PROJECT_ROOT / "agent_city_tray.ps1"

STARTUP_TIMEOUT_SECONDS = 30.0
STOP_TIMEOUT_SECONDS = 12.0
UPDATE_FLAG_FRESH_SECONDS = 300.0
MUTEX_NAME = "Local\\AgentCityDesktopLauncher"

_MUTEX_HANDLE: int | None = None


def _log(message: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LAUNCHER_LOG.open("a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {message}\n")


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp.replace(path)


def _set_status(state: str, text: str) -> None:
    _write_json_atomic(
        STATUS_PATH,
        {
            "state": state,
            "text": text,
            "launcher_pid": os.getpid(),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
    )


def _show_error(message: str) -> None:
    _log(f"ERROR: {message}")
    _set_status("Error", message)
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


def _post_local(url: str) -> bool:
    try:
        request = urllib.request.Request(url, data=b"", method="POST")
        with urllib.request.urlopen(request, timeout=2.0) as response:
            return response.status == 200
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


def _acquire_single_instance() -> bool:
    global _MUTEX_HANDLE
    if os.name != "nt":
        return True

    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not handle:
        _log("Could not create launcher mutex; continuing without a single-instance guard.")
        return True

    _MUTEX_HANDLE = int(handle)
    error_already_exists = 183
    return kernel32.GetLastError() != error_already_exists


def _release_single_instance() -> None:
    global _MUTEX_HANDLE
    if os.name == "nt" and _MUTEX_HANDLE:
        try:
            ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(_MUTEX_HANDLE))
        except Exception:
            pass
    _MUTEX_HANDLE = None


def _write_command(command: str) -> None:
    _write_json_atomic(
        COMMAND_PATH,
        {
            "command": command,
            "requested_at": datetime.now().isoformat(timespec="seconds"),
        },
    )


def _read_command() -> str | None:
    if not COMMAND_PATH.exists():
        return None

    try:
        payload = json.loads(COMMAND_PATH.read_text(encoding="utf-8"))
        command = str(payload.get("command") or "").strip().lower()
    except Exception:
        command = ""
    finally:
        try:
            COMMAND_PATH.unlink(missing_ok=True)
        except Exception:
            pass

    return command or None


def _start_server() -> subprocess.Popen:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    python_exe = _python_without_console()
    command = [python_exe, str(PROJECT_ROOT / "main.py")]

    creationflags = 0
    if os.name == "nt":
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    env = os.environ.copy()
    env["AGENT_CITY_LAUNCHER_PID"] = str(os.getpid())

    server_log = SERVER_LOG.open("a", encoding="utf-8")
    try:
        process = subprocess.Popen(
            command,
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=server_log,
            stderr=server_log,
            creationflags=creationflags,
            start_new_session=(os.name != "nt"),
            env=env,
        )
    finally:
        server_log.close()

    SERVER_PID_PATH.write_text(str(process.pid), encoding="utf-8")
    _log(f"Started Agent City runtime PID {process.pid} with {python_exe}")
    return process


def _wait_until_ready(timeout: float = STARTUP_TIMEOUT_SECONDS) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _agent_city_is_ready():
            return True
        time.sleep(0.35)
    return False


def _wait_until_stopped(timeout: float = STOP_TIMEOUT_SECONDS) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _agent_city_is_ready():
            return True
        time.sleep(0.25)
    return False


def _request_runtime_stop(server_process: subprocess.Popen | None) -> bool:
    if not _agent_city_is_ready():
        return True

    _post_local(SHUTDOWN_URL)
    if _wait_until_stopped():
        return True

    if server_process is not None and server_process.poll() is None:
        _log("Graceful runtime stop timed out; terminating owned runtime process.")
        try:
            server_process.terminate()
            server_process.wait(timeout=5.0)
        except Exception as exc:
            _log(f"Owned runtime termination failed: {exc}")

    return not _agent_city_is_ready()


def _restart_runtime(server_process: subprocess.Popen | None) -> subprocess.Popen | None:
    _set_status("Restarting", "Stopping the local runtime.")
    if not _request_runtime_stop(server_process):
        _show_error("Agent City could not stop cleanly for restart.")
        return server_process

    SERVER_PID_PATH.unlink(missing_ok=True)
    _set_status("Starting", "Starting the local runtime.")
    process = _start_server()
    if _wait_until_ready():
        _set_status("Running", "Agent City is running.")
        _log("Agent City runtime restarted successfully.")
        return process

    _show_error("Agent City did not finish restarting. Check data\\server.log.")
    return process


def _start_tray() -> subprocess.Popen | None:
    if os.name != "nt" or not TRAY_SCRIPT.exists():
        return None

    powershell = Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    executable = str(powershell) if powershell.exists() else "powershell.exe"
    pythonw = _python_without_console()

    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        process = subprocess.Popen(
            [
                executable,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-WindowStyle",
                "Hidden",
                "-File",
                str(TRAY_SCRIPT),
                "-ProjectRoot",
                str(PROJECT_ROOT),
                "-Pythonw",
                pythonw,
                "-LauncherPid",
                str(os.getpid()),
            ],
            cwd=str(PROJECT_ROOT),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        _log(f"Started tray host PID {process.pid}.")
        return process
    except Exception as exc:
        _log(f"Tray host could not start: {exc}")
        return None


def _stop_tray(tray_process: subprocess.Popen | None) -> None:
    if tray_process is None or tray_process.poll() is not None:
        return
    try:
        tray_process.terminate()
        tray_process.wait(timeout=3.0)
    except Exception:
        try:
            tray_process.kill()
        except Exception:
            pass


def _update_exit_requested() -> bool:
    if not UPDATE_FLAG.exists():
        return False

    try:
        age = time.time() - UPDATE_FLAG.stat().st_mtime
        if age <= UPDATE_FLAG_FRESH_SECONDS:
            return True
        UPDATE_FLAG.unlink(missing_ok=True)
        _log("Removed stale launcher update-exit flag.")
    except Exception:
        return True
    return False


def _cleanup_runtime_files() -> None:
    try:
        LAUNCHER_PID_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def _monitor(
    server_process: subprocess.Popen | None,
    tray_process: subprocess.Popen | None,
) -> None:
    last_health: bool | None = None
    last_tray_restart = 0.0

    while True:
        if _update_exit_requested():
            _set_status("Updating", "Handing control to the Agent City updater.")
            _log("Update handoff requested; closing the current desktop supervisor.")
            _stop_tray(tray_process)
            _cleanup_runtime_files()
            return

        command = _read_command()
        if command == "open":
            if _agent_city_is_ready():
                webbrowser.open(APP_URL, new=2)
            else:
                server_process = _restart_runtime(server_process)
                if _agent_city_is_ready():
                    webbrowser.open(APP_URL, new=2)
        elif command == "restart":
            server_process = _restart_runtime(server_process)
        elif command == "quit":
            _set_status("Stopping", "Stopping Agent City.")
            _request_runtime_stop(server_process)
            SERVER_PID_PATH.unlink(missing_ok=True)
            _stop_tray(tray_process)
            _cleanup_runtime_files()
            _set_status("Stopped", "Agent City is not running.")
            _log("Agent City quit from the tray.")
            return

        healthy = _agent_city_is_ready()
        if healthy != last_health:
            if healthy:
                _set_status("Running", "Agent City is running.")
            else:
                process_alive = server_process is not None and server_process.poll() is None
                if process_alive:
                    _set_status("Starting", "Agent City is starting.")
                else:
                    _set_status("Error", "Agent City is not responding. Use Restart from the tray.")
            last_health = healthy

        if os.name == "nt" and TRAY_SCRIPT.exists():
            if tray_process is None or tray_process.poll() is not None:
                now = time.monotonic()
                if now - last_tray_restart >= 5.0:
                    tray_process = _start_tray()
                    last_tray_restart = now

        time.sleep(0.5)


def main() -> None:
    startup_mode = "--startup" in sys.argv
    resume_after_update = "--resume-after-update" in sys.argv
    open_browser_on_ready = not startup_mode and not resume_after_update

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not _acquire_single_instance():
        if startup_mode:
            return
        if _agent_city_is_ready():
            webbrowser.open(APP_URL, new=2)
        else:
            _write_command("restart")
        return

    tray_process: subprocess.Popen | None = None
    server_process: subprocess.Popen | None = None

    try:
        COMMAND_PATH.unlink(missing_ok=True)
        LAUNCHER_PID_PATH.write_text(str(os.getpid()), encoding="utf-8")
        _set_status("Starting", "Starting Agent City.")

        if _agent_city_is_ready():
            _set_status("Running", "Agent City is running.")
            _log("Agent City was already running; desktop supervisor attached.")
        else:
            server_process = _start_server()
            if not _wait_until_ready():
                _show_error(
                    "Agent City did not finish starting. "
                    "Check data\\server.log inside the Agent City folder for details."
                )
            else:
                _set_status("Running", "Agent City is running.")
                _log("Agent City is ready.")

        if open_browser_on_ready and _agent_city_is_ready():
            webbrowser.open(APP_URL, new=2)

        tray_process = _start_tray()
        _monitor(server_process, tray_process)
    except Exception as exc:
        _show_error(f"Agent City desktop supervisor failed: {exc}")
    finally:
        _stop_tray(tray_process)
        _cleanup_runtime_files()
        _release_single_instance()


if __name__ == "__main__":
    main()
