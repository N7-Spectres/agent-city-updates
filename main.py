"""Agent City v2 server.

Run: python main.py  (the desktop launcher does this for you)
Then open http://127.0.0.1:8000/
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent_city import clock
from agent_city.store import connect, get_meta, init_world, load_structures
from agent_city.updater import (
    PROJECT_ROOT, check_for_update, cleanup_stale_update_staging, current_version,
    fetch_manifest, load_settings, make_backup, save_settings, stage_update,
)
from agent_city.visitor import move_visitor, visitor_state
from agent_city.world.planet import Planet

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
OLLAMA_URL = "http://127.0.0.1:11434"

_stop = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_world()
    cleanup_stale_update_staging()
    task = asyncio.create_task(clock.run_clock(_stop))
    yield
    _stop.set()
    task.cancel()


app = FastAPI(title="Agent City", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def no_stale_ui(request, call_next):
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.endswith((".js", ".css", ".html")):
        response.headers["Cache-Control"] = "no-store"
    return response


class MoveRequest(BaseModel):
    visitor: str = "N7"
    x_m: float
    y_m: float
    heading: float


class PauseRequest(BaseModel):
    paused: bool


class UpdateSettingsRequest(BaseModel):
    manifest_url: str


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


# --- world ---------------------------------------------------------------

@app.get("/api/state")
def get_state(visitor: str = "N7"):
    """Everything a visitor standing in the world can see.

    Deposits are world truth and are never sent: nobody knows them yet.
    """
    with connect() as conn:
        seed = int(get_meta(conn, "seed"))
        seconds = float(get_meta(conn, "sim_seconds", "0"))
        paused = get_meta(conn, "paused", "0") == "1"
        scale = float(get_meta(conn, "time_scale", "4"))
        citizens = [dict(r) for r in conn.execute("SELECT * FROM citizens ORDER BY rowid")]
        structures = load_structures(conn)
    return {
        "version": current_version(),
        "world": {"seed": seed, "facility": "Seed Station"},
        "time": {**clock.describe(seconds), "paused": paused, "time_scale": scale},
        "citizens": citizens,
        "structures": structures,
        "visitor": visitor_state(visitor[:40] or "N7"),
    }


@app.get("/api/world/terrain")
def get_terrain():
    with connect() as conn:
        seed = int(get_meta(conn, "seed"))
    planet = Planet(seed)
    return {**planet.heightfield(), "outcrops": planet.surface_outcrops()}


@app.post("/api/visitor/move")
def post_visitor_move(req: MoveRequest):
    return move_visitor(req.visitor.strip()[:40] or "N7", req.x_m, req.y_m, req.heading)


@app.post("/api/pause")
def set_pause(req: PauseRequest):
    clock.set_paused(req.paused)
    return {"ok": True, "paused": req.paused}


@app.get("/api/ollama")
async def ollama_status():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            return {"online": True, "models": [m.get("name") for m in r.json().get("models", [])]}
    except Exception as exc:
        return {"online": False, "error": str(exc)}


# --- updates and launcher (carried over from v1) --------------------------

@app.get("/api/update/status")
async def update_status():
    try:
        return await check_for_update()
    except Exception as exc:
        return {
            "configured": bool(load_settings().get("manifest_url")),
            "current_version": current_version(),
            "update_available": False,
            "manifest_url": load_settings().get("manifest_url", ""),
            "error": str(exc),
        }


@app.post("/api/update/settings")
def update_settings(req: UpdateSettingsRequest):
    url = req.manifest_url.strip()
    if url and not url.startswith("https://"):
        raise HTTPException(400, "The update feed URL must use HTTPS.")
    save_settings(url)
    return {"ok": True, "manifest_url": url}


def _delayed_exit():
    time.sleep(1.25)
    os._exit(0)


@app.post("/api/launcher/shutdown")
def launcher_shutdown():
    threading.Thread(target=_delayed_exit, daemon=True).start()
    return {"ok": True, "message": "Agent City is stopping."}


@app.post("/api/update/install")
async def install_update():
    settings = load_settings()
    manifest_url = settings.get("manifest_url", "")
    update_flag_path = PROJECT_ROOT / "update_staging" / "launcher_exit_for_update.flag"
    if not manifest_url:
        raise HTTPException(400, "No update feed is configured.")
    try:
        manifest = await fetch_manifest(manifest_url)
        if not manifest["version"]:
            raise ValueError("Manifest version is missing.")
        if not tuple(int(x) for x in manifest["version"].lstrip("vV").split("-")[0].split(".")[:3]) > tuple(
            int(x) for x in current_version().lstrip("vV").split("-")[0].split(".")[:3]
        ):
            return {"ok": True, "message": "Agent City is already up to date."}

        backup_dir = make_backup()
        staged = await stage_update(manifest)
        try:
            launcher_pid = int(os.environ.get("AGENT_CITY_LAUNCHER_PID", "").strip() or 0)
        except ValueError:
            launcher_pid = 0
        job = {
            "project_root": str(PROJECT_ROOT),
            "staging_dir": staged["staging_dir"],
            "parent_pid": os.getpid(),
            "launcher_pid": launcher_pid,
            "python_exe": sys.executable,
            "backup_dir": str(backup_dir),
            "target_version": manifest["version"],
        }
        job_path = PROJECT_ROOT / "update_staging" / "update_job.json"
        job_path.parent.mkdir(parents=True, exist_ok=True)
        job_path.write_text(json.dumps(job, indent=2), encoding="utf-8")
        update_flag_path.write_text(
            json.dumps({"target_version": manifest["version"], "launcher_pid": launcher_pid,
                        "created_at": time.time()}, indent=2),
            encoding="utf-8",
        )
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS if os.name == "nt" else 0
        subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "update_runner.py"), str(job_path)],
            cwd=str(PROJECT_ROOT), creationflags=flags, close_fds=(os.name != "nt"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
        )
        threading.Thread(target=_delayed_exit, daemon=True).start()
        return {"ok": True, "restarting": True, "target_version": manifest["version"],
                "backup_dir": str(backup_dir), "message": "Update staged. Agent City is restarting."}
    except HTTPException:
        update_flag_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        update_flag_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Update failed safely. Nothing was installed. {exc}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
