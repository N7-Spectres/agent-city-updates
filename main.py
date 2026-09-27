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
from pydantic import BaseModel, Field

from agent_city.db import connect, get_meta, init_db, set_meta, snapshot
from agent_city.planner import planning_loop
from agent_city.world import WorldClock, format_sim_time
from agent_city.updater import (
    PROJECT_ROOT, check_for_update, current_version, fetch_manifest,
    load_settings, make_backup, save_settings, stage_update
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
OLLAMA_URL = "http://127.0.0.1:11434"

clock = WorldClock()
clock_task: asyncio.Task | None = None
planner_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global clock_task, planner_task
    init_db()
    clock_task = asyncio.create_task(clock.run())
    planner_task = asyncio.create_task(planning_loop())
    yield
    clock.stop()
    for task in (clock_task, planner_task):
        if task:
            task.cancel()


app = FastAPI(title="Agent City", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class PauseRequest(BaseModel):
    paused: bool


class UpdateSettingsRequest(BaseModel):
    manifest_url: str = Field(default="", max_length=1000)


class TalkRequest(BaseModel):
    visitor: str = Field(default="N7", min_length=1, max_length=40)
    citizen_id: str = Field(min_length=1, max_length=40)
    message: str = Field(min_length=1, max_length=1200)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def get_state():
    state = snapshot()
    state["sim_label"] = format_sim_time(state["sim_minute"])
    return state


@app.post("/api/pause")
def set_pause(req: PauseRequest):
    with connect() as conn:
        set_meta(conn, "paused", "true" if req.paused else "false")
        conn.commit()
    return {"ok": True, "paused": req.paused}


@app.get("/api/ollama")
async def ollama_status():
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            response.raise_for_status()
            names = [m.get("name") for m in response.json().get("models", [])]
            return {"online": True, "models": names}
    except Exception as exc:
        return {"online": False, "error": str(exc)}


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


@app.post("/api/update/install")
async def install_update():
    settings = load_settings()
    manifest_url = settings.get("manifest_url", "")
    if not manifest_url:
        raise HTTPException(400, "No update feed is configured.")

    try:
        manifest = await fetch_manifest(manifest_url)
        if not manifest["version"]:
            raise ValueError("Manifest version is missing.")
        if not tuple(int(x) for x in manifest["version"].lstrip("vV").split(".")[:3]) > tuple(
            int(x) for x in current_version().lstrip("vV").split(".")[:3]
        ):
            return {"ok": True, "message": "Agent City is already up to date."}

        backup_dir = make_backup()
        staged = await stage_update(manifest)

        job = {
            "project_root": str(PROJECT_ROOT),
            "staging_dir": staged["staging_dir"],
            "parent_pid": os.getpid(),
            "python_exe": sys.executable,
            "backup_dir": str(backup_dir),
            "target_version": manifest["version"],
        }
        job_path = PROJECT_ROOT / "update_staging" / "update_job.json"
        job_path.parent.mkdir(parents=True, exist_ok=True)
        job_path.write_text(json.dumps(job, indent=2), encoding="utf-8")

        flags = 0
        if os.name == "nt":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

        subprocess.Popen(
            [sys.executable, str(PROJECT_ROOT / "update_runner.py"), str(job_path)],
            cwd=str(PROJECT_ROOT),
            creationflags=flags,
            close_fds=(os.name != "nt"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )

        threading.Thread(target=_delayed_exit, daemon=True).start()

        return {
            "ok": True,
            "restarting": True,
            "target_version": manifest["version"],
            "backup_dir": str(backup_dir),
            "message": "Update staged. Agent City is restarting.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Update failed safely. Nothing was installed. {exc}")


@app.post("/api/talk")
async def talk(req: TalkRequest):
    state = snapshot()
    citizen = next((c for c in state["citizens"] if c["id"] == req.citizen_id), None)
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT visitor_text, citizen_text, sim_minute
            FROM conversations
            WHERE visitor = ? AND citizen_id = ?
            ORDER BY id DESC LIMIT 8
            """,
            (req.visitor, req.citizen_id),
        ).fetchall()
        prior = list(reversed([dict(r) for r in rows]))

        last_exchange = prior[-1] if prior else None

        history_rows = conn.execute(
            """
            SELECT sim_minute, message
            FROM history
            WHERE message LIKE ?
            ORDER BY id DESC LIMIT 8
            """,
            (f"{citizen['name']}%",),
        ).fetchall()
        citizen_history = list(reversed([dict(r) for r in history_rows]))

        active_job = None
        if citizen.get("active_job_id") is not None:
            row = conn.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (citizen["active_job_id"],),
            ).fetchone()
            active_job = dict(row) if row else None

    resource_summary = ", ".join(f"{r['name']}: {r['amount']:g}" for r in state["resources"])

    known_deposits = []
    for dep in state["deposits"]:
        if dep["discovered"]:
            loc = next((l["name"] for l in state["locations"] if l["id"] == dep["location_id"]), dep["location_id"])
            known_deposits.append(f"{dep['material']} at {loc}")
    deposit_summary = ", ".join(known_deposits) or "none confirmed"

    inventory = [r for r in state["inventory"] if r["citizen_id"] == citizen["id"] and r["amount"] > 0]
    inventory_summary = ", ".join(f"{r['amount']:g} {r['material']}" for r in inventory) or "nothing"

    prior_topics_text = "\n".join(f"- {r['visitor_text']}" for r in prior) or "- none"
    has_met_before = "yes" if prior else "no"

    if last_exchange:
        recent_gap = max(0, state["sim_minute"] - int(last_exchange["sim_minute"]))
        if recent_gap <= 90:
            conversation_phase = "same ongoing visit"
        elif recent_gap <= 360:
            conversation_phase = "recent return visit"
        else:
            conversation_phase = "returning visitor after some time"

        last_conversation_text = (
            f"Visitor previously said: {last_exchange['visitor_text']}\n"
            f"You previously replied: {last_exchange['citizen_text']}"
        )
    else:
        conversation_phase = "first conversation"
        last_conversation_text = "none"

    confirmed_history_text = "\n".join(
        f"- {format_sim_time(h['sim_minute'])}: {h['message']}"
        for h in citizen_history
    ) or "- no confirmed personal activity yet"

    if active_job:
        current_intent = (
            f"- Action: {active_job['action']}\n"
            f"- Target: {active_job['target']}\n"
            f"- Reason chosen at decision time: {active_job.get('intent_reason') or 'no reason was recorded'}"
        )
    else:
        current_intent = "- no active job"

    system_prompt = f"""
You are {citizen['name']}, one of six equal mechanical citizens living at the beginning of Agent City.

Starting aptitude: {citizen['aptitude']}. It is not a permanent role.
The visitor speaking with you is {req.visitor}.
You have spoken with this visitor before: {has_met_before}.

Visitors are not gods, rulers, operators, or commanders.
You may agree, disagree, ask questions, be uncertain, or simply say you do not know.

CONFIRMED CURRENT FACTS:
- Time: {format_sim_time(state['sim_minute'])}
- Your location: {citizen['location']}
- Your current activity: {citizen['current_activity']}
- Your energy: {citizen['energy']:.0f}%
- Your integrity: {citizen['integrity']:.0f}%
- You are carrying: {inventory_summary}
- Seed Site has a habitat/workshop, solar array, battery bank, charging station, storage unit, basic workbench, and crude smelter.
- Seed Site stores: {resource_summary}
- The six citizens are Aris, Bex, Cato, Iri, Noma, and Vale.
- No leader has been appointed.
- No long-term objective has been assigned.
- Confirmed material deposits known to the settlement: {deposit_summary}

YOUR CONFIRMED PERSONAL ACTIVITY HISTORY:
{confirmed_history_text}

YOUR CURRENT RECORDED INTENT:
{current_intent}

WHAT THIS VISITOR HAS PREVIOUSLY TALKED TO YOU ABOUT:
{prior_topics_text}

CONVERSATION CONTINUITY:
- Conversation phase: {conversation_phase}
- Most recent exchange:
{last_conversation_text}

The previous citizen reply above is conversational context only, NOT authoritative world history.
Use it to avoid repeating the same greeting, question, or answer structure.
If this is the same ongoing visit, do not greet the visitor again unless the visitor explicitly greets you again.
If nothing has materially changed since your last answer, say so briefly instead of restating the same information in different words.
For status-check questions such as "anything new?", answer the status check directly and stop; do not automatically add a reciprocal social question.
Do not ask the visitor the same generic question repeatedly (for example, "How are you?" / "How have you been?" / "Anything new on your end?") unless the visitor's message genuinely calls for it.
If your current activity is "Available", describe yourself as available or idle at your current location. Do not reinterpret "Available" as gathering data, checking systems, organizing supplies, inspecting equipment, or doing another task.
Do not say you are "still" doing an activity unless that exact activity appears in CONFIRMED CURRENT FACTS or YOUR CONFIRMED PERSONAL ACTIVITY HISTORY.

STRICT REALITY RULES:
1. Only the confirmed current facts, confirmed personal activity history, and current recorded intent above are authoritative.
2. Previous visitor messages are conversation topics, not proof that something physically happened.
3. Previous citizen replies are NOT authoritative and must not be treated as history.
4. Never claim a completed physical action unless it appears in confirmed history/current activity.
5. If asked WHY you are performing your current action, use the recorded intent reason above. Do not invent a different motivation after the fact.
6. If no intent reason was recorded, say you do not have a clear recorded reason rather than making one up.
7. You may discuss future ideas, but phrase them as intentions, possibilities, or plans.
8. The simulation determines physical outcomes.

Keep conversation natural and fairly concise. Do not speak like an AI assistant or narrator.
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    if prior:
        messages.append({
            "role": "system",
            "content": (
                f"You recognize {req.visitor}. The current conversation phase is: {conversation_phase}. "
                "Maintain continuity and avoid repeating greetings or the same response unless the visitor explicitly restarts the conversation."
            ),
        })
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model": state["ollama_model"],
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.60, "num_ctx": 4096},
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            answer = response.json()["message"]["content"].strip()
    except Exception as exc:
        raise HTTPException(
            503,
            f"Ollama could not answer. Make sure Ollama is running and {state['ollama_model']} is installed. Details: {exc}",
        )

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO conversations
            (sim_minute, visitor, citizen_id, visitor_text, citizen_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (state["sim_minute"], req.visitor, req.citizen_id, req.message, answer),
        )
        conn.commit()

    return {"citizen": citizen["name"], "visitor": req.visitor, "message": answer, "sim_label": format_sim_time(state["sim_minute"])}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
