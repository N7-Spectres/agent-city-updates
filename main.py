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
from agent_city.comms import known_deposits_for, recent_dialogues_for, visible_citizens
from agent_city.grounding import (
    citizen_capability_context,
    grounding_policy_text,
    settlement_store_context,
    spatial_grounding_context,
)
from agent_city.provenance import (
    ensure_information_schema,
    knowledge_context_for as provenance_context_for,
    knowledge_payload,
)
from agent_city.planner import planning_loop
from agent_city.shared_actions import (
    accept_proposal,
    ensure_shared_action_schema,
    expire_pending_proposals_for_visitor,
    maybe_create_proposal_from_exchange,
    proposal_payload,
    proposals_for_visit,
    reject_proposal,
    shared_action_context,
    shared_action_option_context,
)
from agent_city.talk_diagnostics import ensure_talk_diagnostic_schema
from agent_city.simulation import cargo_capacity as physical_cargo_capacity
from agent_city.exploration import (
    accept_shared_activity,
    propose_shared_activity,
    reject_shared_activity,
    shared_activity_payload,
    start_shared_activity,
)
from agent_city.memory import (
    ensure_memory_schema,
    knowledge_context_for as memory_knowledge_context_for,
    knowledge_snapshot_for,
    location_knowledge_snapshot,
    maintenance_context_for,
    maintenance_snapshot_for,
    social_context_for,
)
from agent_city.world import WorldClock, format_sim_time
from agent_city.visits import (
    close_visit, ensure_visit_schema, get_or_create_active_visit,
    get_recent_exchanges, previous_visits, summarize_visit_if_needed, visit_payload,
)
from agent_city.visitors import (
    can_visit_citizen,
    ensure_visitor,
    presence_payload,
    start_visitor_travel,
    visit_access_payload,
)
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
    ensure_visit_schema()
    ensure_memory_schema()
    ensure_information_schema()
    ensure_talk_diagnostic_schema()
    ensure_shared_action_schema()
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


class VisitorRequest(BaseModel):
    visitor: str = Field(default="N7", min_length=1, max_length=40)


class TalkRequest(BaseModel):
    visitor: str = Field(default="N7", min_length=1, max_length=40)
    citizen_id: str = Field(min_length=1, max_length=40)
    message: str = Field(min_length=1, max_length=1200)


class VisitorTravelRequest(BaseModel):
    visitor: str = Field(default="N7", min_length=1, max_length=40)
    target: str = Field(min_length=1, max_length=80)


class SharedActivityProposalRequest(BaseModel):
    visitor: str = Field(default="N7", min_length=1, max_length=40)
    citizen_id: str = Field(min_length=1, max_length=40)
    target_x_m: float
    target_y_m: float
    objective: str = Field(default="Walk together and inspect the destination.", min_length=1, max_length=500)
    source_visit_id: int | None = None
    source_exchange_id: int | None = None
    tool_equipment_id: int | None = None


class SharedActivityAcceptRequest(BaseModel):
    visitor: str = Field(default="N7", min_length=1, max_length=40)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def get_state():
    state = snapshot()
    state["sim_label"] = format_sim_time(state["sim_minute"])
    with connect() as conn:
        for citizen in state["citizens"]:
            citizen["cargo_capacity"] = physical_cargo_capacity(
                conn,
                citizen["id"],
                citizen["location_id"],
            )
    return state


@app.get("/api/knowledge/citizens/{citizen_id}")
def get_citizen_knowledge(
    citizen_id: str,
    location_id: str | None = None,
    material: str | None = None,
    process: str | None = None,
    limit: int = 12,
):
    with connect() as conn:
        citizen = conn.execute(
            "SELECT id, name FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    safe_limit = max(1, min(int(limit), 30))
    facts = knowledge_snapshot_for(
        citizen_id,
        location_id=location_id,
        material=material,
        process=process,
        limit=safe_limit,
    )
    return {
        "citizen": {"id": citizen["id"], "name": citizen["name"]},
        "filters": {
            "location_id": location_id,
            "material": material,
            "process": process,
        },
        "facts": facts,
        "summary": memory_knowledge_context_for(
            citizen_id,
            location_id=location_id,
            material=material,
            process=process,
            limit=min(safe_limit, 8),
        ),
    }


@app.get("/api/memory/maintenance/{citizen_id}")
def get_maintenance_memory(
    citizen_id: str,
    target_type: str | None = None,
    target_id: str | None = None,
    limit: int = 10,
):
    with connect() as conn:
        citizen = conn.execute(
            "SELECT id, name FROM citizens WHERE id = ?",
            (citizen_id,),
        ).fetchone()
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    safe_limit = max(1, min(int(limit), 30))
    events = maintenance_snapshot_for(
        citizen_id,
        target_type=target_type,
        target_id=target_id,
        limit=safe_limit,
    )
    return {
        "citizen": {"id": citizen["id"], "name": citizen["name"]},
        "filters": {"target_type": target_type, "target_id": target_id},
        "events": events,
        "summary": maintenance_context_for(
            citizen_id,
            target_type=target_type,
            target_id=target_id,
            limit=min(safe_limit, 6),
        ),
    }


@app.get("/api/knowledge/locations/{location_id}")
def get_location_knowledge(location_id: str, citizen_id: str | None = None):
    payload = location_knowledge_snapshot(
        location_id,
        citizen_id=citizen_id,
        per_citizen_limit=10,
    )
    if payload["location"] is None:
        raise HTTPException(404, "Location not found")
    if citizen_id and not payload["citizens"]:
        raise HTTPException(404, "Citizen not found")
    return payload


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


@app.get("/api/visitor/presence")
def get_visitor_presence(visitor: str = "N7"):
    return presence_payload(visitor)


@app.get("/api/knowledge/{citizen_id}")
def get_provenance_knowledge(citizen_id: str):
    payload = knowledge_payload(citizen_id)
    if not payload.get("exists"):
        raise HTTPException(404, "Citizen not found")
    return payload


@app.post("/api/visitor/travel")
def visitor_travel(req: VisitorTravelRequest):
    ok, message = start_visitor_travel(req.visitor, req.target)
    if not ok:
        raise HTTPException(400, message)
    expire_pending_proposals_for_visitor(req.visitor.strip()[:40] or "Visitor")
    return {"ok": True, "message": message, "presence": presence_payload(req.visitor)}


@app.post("/api/shared-activities/propose")
def create_shared_activity_proposal(req: SharedActivityProposalRequest):
    visitor = req.visitor.strip()[:40] or "Visitor"
    ensure_visitor(visitor)
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        ok, activity_id, message = propose_shared_activity(
            conn,
            visitor=visitor,
            citizen_id=req.citizen_id,
            target_x_m=req.target_x_m,
            target_y_m=req.target_y_m,
            objective=req.objective,
            source_visit_id=req.source_visit_id,
            source_exchange_id=req.source_exchange_id,
            tool_equipment_id=req.tool_equipment_id,
            now=now,
        )
        if not ok:
            raise HTTPException(409, message)
        conn.commit()
        payload = shared_activity_payload(conn, int(activity_id), now)
    return {"ok": True, "message": message, "activity": payload}


@app.post("/api/shared-activities/{activity_id}/accept")
def accept_shared_activity_endpoint(activity_id: int, req: SharedActivityAcceptRequest):
    visitor = req.visitor.strip()[:40] or "Visitor"
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        ok, _, message = accept_shared_activity(
            conn,
            int(activity_id),
            visitor,
            now=now,
        )
        if not ok:
            raise HTTPException(409, message)
        conn.commit()
        payload = shared_activity_payload(conn, int(activity_id), now)
    return {"ok": True, "message": message, "activity": payload}


@app.post("/api/shared-activities/{activity_id}/reject")
def reject_shared_activity_endpoint(activity_id: int, req: SharedActivityAcceptRequest):
    visitor = req.visitor.strip()[:40] or "Visitor"
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        ok, message = reject_shared_activity(
            conn,
            int(activity_id),
            visitor,
            now=now,
        )
        if not ok:
            raise HTTPException(409, message)
        conn.commit()
        payload = shared_activity_payload(conn, int(activity_id), now)
    return {"ok": True, "message": message, "activity": payload}


@app.post("/api/shared-activities/{activity_id}/start")
def start_shared_activity_endpoint(activity_id: int, req: SharedActivityAcceptRequest):
    visitor = req.visitor.strip()[:40] or "Visitor"
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        ok, job_id, message = start_shared_activity(
            conn,
            int(activity_id),
            visitor,
            now=now,
        )
        if not ok:
            raise HTTPException(409, message)
        conn.commit()
        payload = shared_activity_payload(conn, int(activity_id), now)
    return {"ok": True, "message": message, "job_id": job_id, "activity": payload}


@app.get("/api/shared-activities/{activity_id}")
def get_shared_activity(activity_id: int):
    with connect() as conn:
        now = int(get_meta(conn, "sim_minute") or "360")
        payload = shared_activity_payload(conn, int(activity_id), now)
    if not payload:
        raise HTTPException(404, "Shared activity not found.")
    return payload


@app.get("/api/visit/{citizen_id}")
def get_visit(citizen_id: str, visitor: str = "N7"):
    state = snapshot()
    citizen = next((c for c in state["citizens"] if c["id"] == citizen_id), None)
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    visitor = visitor.strip()[:40] or "Visitor"
    presence = presence_payload(visitor)
    access = visit_access_payload(visitor, citizen_id)
    accessible = bool(access["accessible"])
    reason = str(access.get("reason") or "")

    with connect() as conn:
        old_visits = previous_visits(conn, visitor, citizen_id, limit=3)

    if not accessible:
        return {
            "accessible": False,
            "status": access.get("status"),
            "availability": access,
            "reason": reason,
            "citizen": citizen,
            "visitor": visitor,
            "presence": presence,
            "messages": [],
            "previous_visits": old_visits,
            "has_earlier": False,
            "visit": None,
            "shared_action_proposals": [],
        }

    with connect() as conn:
        visit = get_or_create_active_visit(conn, visitor, citizen_id, state["sim_minute"])
        payload = visit_payload(conn, int(visit["id"]))
        payload["previous_visits"] = old_visits

    payload["accessible"] = True
    payload["status"] = access.get("status")
    payload["availability"] = access
    payload["citizen"] = citizen
    payload["visitor"] = visitor
    payload["presence"] = presence
    payload["shared_action_proposals"] = proposals_for_visit(
        visitor,
        citizen_id,
        visit_id=int(visit["id"]),
        limit=8,
    )
    return payload


@app.get("/api/visits/{citizen_id}")
def get_previous_visits(citizen_id: str, visitor: str = "N7"):
    state = snapshot()
    citizen = next((c for c in state["citizens"] if c["id"] == citizen_id), None)
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    with connect() as conn:
        visits = previous_visits(conn, visitor.strip()[:40] or "Visitor", citizen_id, limit=8)
    return {"citizen": citizen, "visits": visits}


@app.post("/api/visit/{citizen_id}/leave")
async def leave_visit(citizen_id: str, req: VisitorRequest):
    state = snapshot()
    citizen = next((c for c in state["citizens"] if c["id"] == citizen_id), None)
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    visitor = req.visitor.strip()[:40] or "Visitor"
    with connect() as conn:
        visit = get_or_create_active_visit(conn, visitor, citizen_id, state["sim_minute"])
        visit_id = int(visit["id"])

    await summarize_visit_if_needed(visit_id, state["ollama_model"], force=True)

    with connect() as conn:
        close_visit(conn, visit_id, state["sim_minute"])

    expire_pending_proposals_for_visitor(visitor)
    return {"ok": True, "visit_id": visit_id}


@app.post("/api/talk")
async def talk(req: TalkRequest):
    access = visit_access_payload(req.visitor, req.citizen_id)
    if not access["accessible"]:
        raise HTTPException(409, str(access.get("reason") or "Face-to-face conversation unavailable."))

    state = snapshot()
    citizen = next((c for c in state["citizens"] if c["id"] == req.citizen_id), None)
    if not citizen:
        raise HTTPException(404, "Citizen not found")

    visitor = req.visitor.strip()[:40] or "Visitor"

    with connect() as conn:
        visit = get_or_create_active_visit(conn, visitor, req.citizen_id, state["sim_minute"])
        visit_id = int(visit["id"])
        prior = get_recent_exchanges(conn, visit_id, limit=8)
        last_exchange = prior[-1] if prior else None
        active_visit_summary = str(visit["summary"] or "").strip()
        closed_visits = previous_visits(conn, visitor, req.citizen_id, limit=2)

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

    store_context = settlement_store_context(citizen["id"])
    capability_context = citizen_capability_context(citizen["id"])
    visitor_grounding = grounding_policy_text(visitor_facing=True)
    spatial_context = spatial_grounding_context(citizen["id"], visitor_id=visitor)

    personal_deposits = known_deposits_for(citizen["id"])
    deposit_summary = ", ".join(
        f"{d['material']} at {d['location_name']}" for d in personal_deposits
    ) or "none personally confirmed"

    visible_others = visible_citizens(citizen["id"])
    visible_summary = "; ".join(
        f"{c['name']} — {c['current_activity']}" for c in visible_others
    ) or "none"

    provenance_knowledge = provenance_context_for(citizen["id"], limit=12)

    citizen_dialogues = recent_dialogues_for(citizen["id"], limit=6)
    citizen_dialogue_summary = "\n".join(
        f"- {d['summary']}" for d in citizen_dialogues
    ) or "- none"
    social_history = social_context_for(citizen["id"], limit=4)
    local_knowledge = memory_knowledge_context_for(
        citizen["id"],
        location_id=citizen["location_id"],
        limit=6,
    )
    maintenance_history = maintenance_context_for(citizen["id"], limit=4)

    inventory = [r for r in state["inventory"] if r["citizen_id"] == citizen["id"] and r["amount"] > 0]
    inventory_summary = ", ".join(f"{r['amount']:g} {r['material']}" for r in inventory) or "nothing"

    prior_topics_text = "\n".join(f"- {r['visitor_text']}" for r in prior) or "- none in this visit yet"
    conversation_phase = "same ongoing visit" if prior else "new visit"

    if last_exchange:
        last_conversation_text = (
            f"Visitor previously said: {last_exchange['visitor_text']}\n"
            f"You previously replied: {last_exchange['citizen_text']}"
        )
    else:
        last_conversation_text = "none"

    previous_visit_text = "\n".join(
        f"- Earlier visit summary: {v['summary']}"
        for v in reversed(closed_visits)
        if str(v.get("summary") or "").strip()
    ) or "- none available"

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

    shared_activity_options = shared_action_option_context(visitor, req.citizen_id)
    shared_activity_context = shared_action_context(
        visitor,
        req.citizen_id,
        visit_id=visit_id,
    )

    system_prompt = f"""
You are {citizen['name']}, one of six equal mechanical citizens living at the beginning of Agent City.

Starting aptitude: {citizen['aptitude']}. It is not a permanent role.
The visitor speaking with you is {visitor}.

Visitors are not gods, rulers, operators, or commanders.
You may agree, disagree, ask questions, be uncertain, or simply say you do not know.

CONFIRMED CURRENT FACTS:
- Time: {format_sim_time(state['sim_minute'])}
- Your location: {citizen['location']}
- The visitor is physically at your location; this conversation is face-to-face.
- Your current activity: {citizen['current_activity']}
- Your energy: {citizen['energy']:.0f}%
- Your integrity: {citizen['integrity']:.0f}%
- You are carrying: {inventory_summary}
- Seed Site has a habitat/workshop, solar array, battery bank, charging station, storage unit, basic workbench, and crude smelter.
- {store_context}
- The six citizens are Aris, Bex, Cato, Iri, Noma, and Vale.
- No leader has been appointed.
- No long-term objective has been assigned.
- Material deposits you personally confirmed: {deposit_summary}
- Citizens physically present at your current location and directly observable: {visible_summary}

PROVENANCE-BACKED FACTS AND CLAIMS THAT ACTUALLY REACHED YOU:
{provenance_knowledge}

RECENT FACE-TO-FACE CITIZEN CONVERSATIONS FOR SOCIAL CONTINUITY ONLY:
{citizen_dialogue_summary}

DURABLE SOCIAL HISTORY FROM YOUR OWN RECORDED ENCOUNTERS:
{social_history}

RETAINED KNOWLEDGE ABOUT THIS LOCATION:
{local_knowledge}

SELECTED MEANINGFUL MAINTENANCE EXPERIENCES YOU PARTICIPATED IN:
{maintenance_history}

{capability_context}

{spatial_context}

{visitor_grounding}

YOUR CONFIRMED PERSONAL ACTIVITY HISTORY:
{confirmed_history_text}

YOUR CURRENT RECORDED INTENT:
{current_intent}

{shared_activity_options}

{shared_activity_context}

ACTIVE VISIT MEMORY SUMMARY:
{active_visit_summary or '(none yet)'}

RECENT EXCHANGES IN THIS VISIT:
{prior_topics_text}

MOST RECENT EXCHANGE:
{last_conversation_text}

OLDER CLOSED VISIT MEMORIES:
{previous_visit_text}

CONVERSATION CONTINUITY:
- Conversation phase: {conversation_phase}
- A browser refresh does not start a new visit.
- The visit ends only when the visitor explicitly leaves it.
- Use recent exchanges and visit summaries to maintain continuity without repeating the same greeting or answer structure.
- If nothing has materially changed, say so briefly rather than paraphrasing the same status again.
- For status-check questions such as "anything new?", answer directly and stop unless there is a genuine reason to add something.
- Do not ask generic reciprocal questions by habit.
- If current activity is "Available", you are available/idle at your location. Do not invent busywork.

MEMORY / CONTEXT RULES:
- Full raw conversations are archived locally, but you are intentionally given only a bounded recent window plus compact summaries.
- Do not assume missing transcript text means an event did not happen; use the provided summaries for social continuity.
- Conversation summaries are NOT authoritative physical world history.

STRICT REALITY RULES:
1. Only confirmed current facts, confirmed personal activity history, and current recorded intent are authoritative physical facts.
2. Visitor messages are conversation content, not proof of physical events. Treat newly described objects, terrain, conditions, labels, actions, and discoveries as visitor-reported unless another authoritative section confirms them.
3. Previous citizen replies and conversation summaries are NOT authoritative world history.
4. Never claim a completed physical action unless it appears in confirmed history/current activity.
5. If asked WHY you are performing your current action, use the recorded intent reason above.
6. If no intent reason was recorded, say so instead of inventing one.
7. You may discuss future ideas as hypotheses, intentions, possibilities, or plans. Make that uncertainty visible in natural language instead of turning the idea into a fact.
8. The simulation determines physical outcomes.
9. You know the other five citizens exist, but you do NOT know a remote citizen's current location, activity, discoveries, research results, or condition unless that information reached you through a real mechanism.
10. Provenance-backed speaker claims are things somebody said. They remain unverified unless a separate physical observation, survey/measurement, or experiment verifies them.
11. Conversation summaries are social continuity and are NOT authoritative physical facts.
12. There is currently no radio, network, telepathy, shared live status channel, or other long-distance communication system.
13. If asked about a remote citizen/location and you lack provenance-backed information, say you do not know. If you have last-known information, state its source/age or clearly phrase it as something you heard/observed earlier.
14. Do not claim a shared visitor activity has physically started because you conversationally agreed to it. Until Simulation exposes a real visitor-linked action, agreement is an intention only.
15. Do not claim a tool, structure, process, or capability from concept art, visual description, or imagination. Use only the authoritative capability surface supplied above.
16. A shared-action proposal is not a physical action. While status is proposed or accepted-without-Simulation-ID, use proposal/intention language only.
17. Only when SHARED PHYSICAL ACTIVITY says Simulation has an ACTIVE real action ID may you say the shared activity has started or is underway.
18. Only a Simulation-completed shared action / validated observation may be described as completed physical exploration.

Keep conversation natural and fairly concise. Ground uncertainty conversationally; do not turn the response into a policy lecture. Do not speak like an AI assistant or narrator.
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    for row in prior:
        messages.append({"role": "user", "content": row["visitor_text"]})
        prior_answer = str(row["citizen_text"] or "").strip()
        if prior_answer:
            messages.append({"role": "assistant", "content": prior_answer})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model": state["ollama_model"],
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.58,
            "num_ctx": 4096,
            "num_predict": 280,
        },
    }

    try:
        answer = ""
        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(2):
                response = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
                response.raise_for_status()
                message = response.json().get("message") or {}
                answer = str(message.get("content") or "").strip()
                if answer:
                    break
                if attempt == 0:
                    payload["options"]["num_predict"] = 420

        if not answer:
            raise RuntimeError("Ollama returned an empty response twice; nothing was stored.")
    except Exception as exc:
        raise HTTPException(
            503,
            f"Ollama could not answer. Make sure Ollama is running and {state['ollama_model']} is installed. Details: {exc}",
        )

    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO conversations
            (sim_minute, visitor, citizen_id, visitor_text, citizen_text, visit_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (state["sim_minute"], visitor, req.citizen_id, req.message, answer, visit_id),
        )
        exchange_id = int(cur.lastrowid)
        conn.commit()

    proposal = await maybe_create_proposal_from_exchange(
        visitor=visitor,
        citizen_id=req.citizen_id,
        visit_id=visit_id,
        source_exchange_id=exchange_id,
        visitor_text=req.message,
        citizen_text=answer,
        model=state["ollama_model"],
    )

    await summarize_visit_if_needed(visit_id, state["ollama_model"], force=False)

    return {
        "citizen": citizen["name"],
        "visitor": visitor,
        "message": answer,
        "sim_label": format_sim_time(state["sim_minute"]),
        "visit_id": visit_id,
        "exchange_id": exchange_id,
        "shared_action_proposal": proposal,
    }


@app.get("/api/visit/{citizen_id}/shared-actions")
def get_shared_action_proposals(
    citizen_id: str,
    visitor: str = "N7",
    visit_id: int | None = None,
):
    visitor = visitor.strip()[:40] or "Visitor"
    return {
        "visitor": visitor,
        "citizen_id": citizen_id,
        "proposals": proposals_for_visit(
            visitor,
            citizen_id,
            visit_id=visit_id,
            limit=12,
        ),
    }


@app.get("/api/shared-actions/{proposal_id}")
def get_shared_action_proposal(proposal_id: int):
    proposal = proposal_payload(proposal_id)
    if not proposal:
        raise HTTPException(404, "Shared-action proposal not found")
    return proposal


@app.post("/api/shared-actions/{proposal_id}/accept")
def accept_shared_action_proposal(proposal_id: int, req: VisitorRequest):
    visitor = req.visitor.strip()[:40] or "Visitor"
    ok, message, proposal = accept_proposal(proposal_id, visitor)
    if not ok:
        raise HTTPException(409, message)
    return {"ok": True, "message": message, "proposal": proposal}


@app.post("/api/shared-actions/{proposal_id}/reject")
def reject_shared_action_proposal(proposal_id: int, req: VisitorRequest):
    visitor = req.visitor.strip()[:40] or "Visitor"
    ok, message, proposal = reject_proposal(proposal_id, visitor)
    if not ok:
        raise HTTPException(409, message)
    return {"ok": True, "message": message, "proposal": proposal}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
