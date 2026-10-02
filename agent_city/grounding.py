from __future__ import annotations

from typing import Any

from .db import connect, snapshot


EPISTEMIC_LANGUAGE_GUIDE = """
GROUNDING / EPISTEMIC LANGUAGE:
- KNOWN FACT: state it normally only when it is present in confirmed Simulation state, validated knowledge, or a verified provenance record supplied in context.
- CURRENT OBSERVATION: state only what the current physical context explicitly makes observable. A place name is not permission to invent terrain, weather, objects, or history.
- REPORTED CLAIM: attribute it to the speaker/source. Visitor descriptions and unverified citizen claims remain reports unless separately validated.
- HYPOTHESIS / PROPOSAL: ideas, interpretations, likely uses, economic/value judgments, explanations, and future plans must be phrased as possibilities rather than facts.
- VALIDATED CAPABILITY / ACTION: say you can use/do something only when the authoritative capability/action surface below actually supports it.

Factual nouns need evidence. Personality, tone, humor, curiosity, and style may improvise freely.
""".strip()


VISITOR_RP_GROUNDING_RULES = """
VISITOR ROLEPLAY GROUNDING:
- The visitor's newest message is conversation content. Any physical detail the visitor describes is a visitor-reported observation/claim unless confirmed elsewhere in authoritative context.
- You may respond naturally to a visitor report without endorsing it as fact: refer to "what you're seeing", "the feature you described", or "if that observation holds".
- Do not confidently invent material microstructure, chemistry, hidden properties, economic/market value, scarcity, terrain names, landmark history, weather, atmospheric effects, or environmental causes.
- A visitor may coin a descriptive name for a feature. You may reuse it as the visitor's label, not as an officially mapped/validated place unless Simulation later validates it.
- Do not treat concept art, appearance text, imagined accessories, or UI artwork as physical equipment.
- You may propose an experiment or use for something, but a hypothesis is not a discovery and a proposed use is not a validated capability.
- You may agree conversationally to a shared activity with the visitor, but do NOT say walking, surveying, collecting, building, using a tool, or another physical action has started/completed unless Simulation has created a real action for it.
- Until a visitor-linked shared-action interface exists, shared physical activity remains an intention/proposal only.
""".strip()


AUTONOMOUS_DIALOGUE_GROUNDING_RULES = """
DIALOGUE GROUNDING:
- Do not turn a remembered/report claim into a verified fact.
- Do not invent material properties, terrain, weather/environment effects, market/economic value, site history, tools, structures, or capabilities.
- Do not coin or casually treat a named procedure, protocol, inspection method, repair method, tool, or piece of equipment as established unless that exact thing is supported by the speaker's authoritative capability/knowledge or source-backed recalled history.
- If you want to discuss a method that is not established, describe it generically as a proposal or possibility (for example, "a possible inspection") rather than inventing an official-sounding procedure name.
- A hypothesis may be discussed as a hypothesis.
- A tool/process may be proposed only if it appears in that speaker's authoritative capability surface; otherwise only the idea of investigating may be proposed.
- Legal action availability means the action can be attempted now; it does not mean the result is already known or successful.
""".strip()


def _state_citizen(state: dict[str, Any], citizen_id: str) -> dict[str, Any] | None:
    return next((c for c in state.get("citizens", []) if c.get("id") == citizen_id), None)


def citizen_capability_payload(citizen_id: str) -> dict[str, Any]:
    """
    Return an authoritative, citizen-local capability surface.

    This intentionally derives equipment/structures from Simulation's public
    validated state. It never consumes concept art or appearance metadata.
    """
    state = snapshot()
    citizen = _state_citizen(state, citizen_id)
    if not citizen:
        return {
            "citizen_id": citizen_id,
            "exists": False,
            "equipment": [],
            "structures": [],
            "learned_processes": [],
            "legal_actions": [],
        }

    location_id = str(citizen.get("location_id") or "")

    equipment: list[dict[str, Any]] = []
    for item in state.get("equipment", []):
        if not item.get("operational", float(item.get("condition") or 0) > 20):
            continue
        owner_id = item.get("owner_citizen_id")
        item_location = item.get("location_id")
        if owner_id == citizen_id or (owner_id is None and item_location == location_id):
            equipment.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "kind": item.get("kind"),
                "owner_citizen_id": owner_id,
                "location_id": item_location,
                "condition_state": item.get("condition_state"),
                "effective_cargo_bonus": item.get("effective_cargo_bonus"),
                "effective_extraction_speed_multiplier": item.get(
                    "effective_extraction_speed_multiplier"
                ),
            })

    structures: list[dict[str, Any]] = []
    for structure in state.get("structures", []):
        if str(structure.get("location_id") or "") != location_id:
            continue
        if not structure.get(
            "operational",
            float(structure.get("condition") or 0) > 20,
        ):
            continue
        structures.append({
            "id": structure.get("id"),
            "name": structure.get("name"),
            "kind": structure.get("kind"),
            "provides_charging": bool(structure.get("provides_charging")),
            "condition_state": structure.get("condition_state"),
            "efficiency_multiplier": structure.get("efficiency_multiplier"),
        })

    learned_processes = [
        {
            "id": process.get("id"),
            "name": process.get("name"),
            "process_key": process.get("process_key"),
            "process_kind": process.get("process_kind"),
            "source_discovery_id": process.get("source_discovery_id"),
        }
        for process in state.get("learned_processes", [])
        if process.get("citizen_id") == citizen_id
    ]

    # Import lazily so grounding stays a consumer of Simulation capability
    # without creating a module-import cycle at startup.
    try:
        from .simulation import possible_actions

        legal_actions = [
            {
                "action": action.get("action"),
                "target": action.get("target"),
                "material": action.get("material"),
                "label": action.get("label"),
            }
            for action in possible_actions(citizen_id)
        ]
    except Exception:
        legal_actions = []

    return {
        "citizen_id": citizen_id,
        "exists": True,
        "location_id": location_id,
        "equipment": equipment,
        "structures": structures,
        "learned_processes": learned_processes,
        "legal_actions": legal_actions,
    }


def citizen_capability_context(citizen_id: str) -> str:
    payload = citizen_capability_payload(citizen_id)
    if not payload.get("exists"):
        return "- citizen capability state unavailable"

    equipment = payload["equipment"]
    structures = payload["structures"]
    processes = payload["learned_processes"]
    actions = payload["legal_actions"]

    equipment_text = (
        "\n".join(
            f"- equipment #{item['id']}: {item['name']} ({item['kind']})"
            for item in equipment
        )
        if equipment
        else "- none"
    )
    structure_text = (
        "\n".join(
            f"- structure #{item['id']}: {item['name']} ({item['kind']})"
            + ("; charging available" if item["provides_charging"] else "")
            for item in structures
        )
        if structures
        else "- none"
    )
    process_text = (
        "\n".join(
            f"- {item['name']} ({item['process_kind']})"
            for item in processes
        )
        if processes
        else "- none"
    )
    action_text = (
        "\n".join(
            f"- {item['action']} target={item.get('target')}: {item.get('label')}"
            for item in actions
        )
        if actions
        else "- none can be started right now"
    )

    return f"""
AUTHORITATIVE CAPABILITY SURFACE:
Physically available operational equipment:
{equipment_text}

Operational structures at your current location:
{structure_text}

Validated learned processes:
{process_text}

Simulation actions you can legally START right now:
{action_text}

Capability rules:
- If a tool/equipment/process is absent above, do not claim you possess or can use it.
- Existing concept art, visual identity, or hypothetical equipment does not create runtime capability.
- A listed legal action may be attempted; its result is not guaranteed.
""".strip()


def spatial_grounding_context(
    citizen_id: str,
    *,
    visitor_id: str | None = None,
    observation_limit: int = 6,
) -> str:
    """
    Forward-compatible consumer of Simulation's v0.8 meter-scale safe read model.

    It uses only ordinary snapshot/visitor-presence state and persisted safe
    observations. It never calls hidden spatial truth/query functions.
    """
    state = snapshot()
    citizen = _state_citizen(state, citizen_id)
    if not citizen:
        return "SPATIAL GROUNDING:\n- citizen spatial state unavailable"

    frame = state.get("spatial_frame")
    observations = [
        row
        for row in state.get("spatial_observations", [])
        if row.get("observer_id") == citizen_id
    ][-max(1, min(int(observation_limit), 12)):]

    lines = ["SPATIAL GROUNDING:"]

    if frame:
        lines.append(
            "- frame: "
            f"{frame.get('id')} in {frame.get('units', 'meters')}; "
            f"+x {frame.get('x_axis', 'east')}, +y {frame.get('y_axis', 'north')}"
        )
    else:
        lines.append("- meter-scale spatial frame is not present in this runtime yet")

    x = citizen.get("position_x_m")
    y = citizen.get("position_y_m")
    if x is not None and y is not None:
        lines.append(f"- your authoritative position: x={float(x):.2f} m, y={float(y):.2f} m")

    if visitor_id:
        try:
            with connect() as conn:
                columns = {
                    row["name"]
                    for row in conn.execute("PRAGMA table_info(visitor_presence)").fetchall()
                }
                if {"x_m", "y_m"}.issubset(columns):
                    visitor = conn.execute(
                        "SELECT x_m, y_m FROM visitor_presence WHERE visitor = ?",
                        (visitor_id,),
                    ).fetchone()
                else:
                    visitor = None
            if visitor and visitor["x_m"] is not None and visitor["y_m"] is not None:
                lines.append(
                    f"- visitor authoritative position: x={float(visitor['x_m']):.2f} m, "
                    f"y={float(visitor['y_m']):.2f} m"
                )
        except Exception:
            pass

    if observations:
        lines.append("- your persisted validated spatial observations:")
        for row in observations:
            detail = (
                f"observation #{row.get('id')} at "
                f"({float(row.get('x_m') or 0):.2f}, {float(row.get('y_m') or 0):.2f}) m: "
                f"terrain={row.get('terrain_class')}, elevation={float(row.get('elevation_m') or 0):.1f} m, "
                f"geology={row.get('geology_class')}"
            )
            if row.get("material"):
                detail += f", material contact={row.get('material')} ({row.get('deposit_id')})"
            lines.append("- " + detail)
    else:
        lines.append("- no persisted validated meter-scale observations are available to you")

    lines.extend([
        "- Do not infer hidden deposit richness, extent, axes, seed, or unseen terrain from this context.",
        "- Visitor-described meter movement does not change either position unless Simulation records movement.",
        "- A persisted spatial observation is evidence only for what that observation safely exposes.",
    ])
    return "\n".join(lines)


def settlement_store_context(citizen_id: str) -> str:
    """
    Only expose live Seed Site storage quantities when the citizen is physically
    at Seed Site. Otherwise current quantities are remote live state.
    """
    state = snapshot()
    citizen = _state_citizen(state, citizen_id)
    if not citizen:
        return "Current Seed Site storage quantities are unavailable."

    if citizen.get("location_id") != "seed_site":
        return (
            "You are away from Seed Site. Do not claim current live storage "
            "quantities unless a retained/communicated record in your context says so."
        )

    resources = state.get("resources", [])
    if not resources:
        return "Seed Site storage currently has no listed resources."
    return "Seed Site current storage: " + ", ".join(
        f"{r['name']}: {float(r['amount']):g}" for r in resources
    )


def grounding_policy_text(*, visitor_facing: bool) -> str:
    parts = [EPISTEMIC_LANGUAGE_GUIDE]
    parts.append(
        VISITOR_RP_GROUNDING_RULES
        if visitor_facing
        else AUTONOMOUS_DIALOGUE_GROUNDING_RULES
    )
    return "\n\n".join(parts)
