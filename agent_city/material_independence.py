from __future__ import annotations

from typing import Any


# v1.0 material independence is deliberately evidence-driven rather than a
# visible technology tree. A process becomes learnable only after the same
# citizen has validated every required material property through real discovery
# records. The process definition then becomes a Simulation-owned capability.
PRODUCTION_PROCESSES: dict[str, dict[str, Any]] = {
    "smelt_crude_metal": {
        "name": "Smelt crude metal stock",
        "structure": "Crude Smelter",
        "duration": 135,
        "energy_cost": 6.0,
        "inputs": {"Ferrite Stone": 4.0},
        "outputs": {"Crude Metal Stock": 2.0},
        "required_properties": {"prop_ferrite_smelt"},
    },
    "form_fasteners": {
        "name": "Form basic fasteners",
        "structure": "Basic Workbench",
        "duration": 70,
        "energy_cost": 3.0,
        "inputs": {"Crude Metal Stock": 1.0},
        "outputs": {"Fasteners": 4.0},
        "required_properties": {"prop_crude_metal_form"},
    },
    "form_mechanical_components": {
        "name": "Form basic mechanical components",
        "structure": "Basic Workbench",
        "duration": 105,
        "energy_cost": 5.0,
        "inputs": {"Crude Metal Stock": 3.0, "Fasteners": 2.0},
        "outputs": {"Mechanical components": 2.0},
        "required_properties": {"prop_crude_metal_form"},
    },
    "cast_structural_material": {
        "name": "Cast processed structural material",
        "structure": "Crude Smelter",
        "duration": 120,
        "energy_cost": 5.0,
        "inputs": {"Silicate": 4.0},
        "outputs": {"Processed structural material": 3.0},
        "required_properties": {"prop_silicate_phase"},
    },
    "refine_lubricant": {
        "name": "Refine lubricant fraction",
        "structure": "Crude Smelter",
        "duration": 95,
        "energy_cost": 4.0,
        "inputs": {"Native Resin": 3.0},
        "outputs": {"Lubricant": 2.0},
        "required_properties": {"prop_resin_lube"},
    },
    "draw_conductive_wire": {
        "name": "Draw conductive wire",
        "structure": "Basic Workbench",
        "duration": 90,
        "energy_cost": 4.0,
        "inputs": {"Copper-like Ore": 3.0},
        "outputs": {"Conductive wire": 6.0},
        "required_properties": {"prop_copper_draw"},
    },
    "assemble_basic_electronics": {
        "name": "Assemble basic electronics",
        "structure": "Basic Workbench",
        "duration": 125,
        "energy_cost": 6.0,
        "inputs": {
            "Conductive wire": 4.0,
            "Processed structural material": 1.0,
            "Carbonaceous Rock": 1.0,
        },
        "outputs": {"Basic electronics": 2.0},
        "required_properties": {
            "prop_copper_conduct",
            "prop_copper_draw",
            "prop_silicate_phase",
            "prop_carbon_resist",
        },
    },
    "assemble_battery_cells": {
        "name": "Assemble replacement battery cells",
        "structure": "Basic Workbench",
        "duration": 150,
        "energy_cost": 7.0,
        "inputs": {
            "Conductive wire": 3.0,
            "Carbonaceous Rock": 2.0,
            "Native Resin": 1.0,
            "Processed structural material": 1.0,
        },
        "outputs": {"Battery cells": 2.0},
        "required_properties": {
            "prop_copper_conduct",
            "prop_copper_draw",
            "prop_silicate_phase",
            "prop_carbon_charge",
            "prop_resin_ionic",
        },
    },
}


def learned_property_discoveries(conn, citizen_id: str) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT d.property_id, d.id AS discovery_id
        FROM citizen_knowledge ck
        JOIN discoveries d ON d.id = ck.discovery_id
        WHERE ck.citizen_id = ?
          AND ck.verification_state = 'verified'
          AND d.property_id IS NOT NULL
        ORDER BY d.id
        """,
        (citizen_id,),
    ).fetchall()
    return {
        str(row["property_id"]): int(row["discovery_id"])
        for row in rows
        if row["property_id"]
    }


def sync_citizen_production_processes(
    conn,
    citizen_id: str,
    *,
    learned_minute: int,
) -> list[str]:
    """Persist newly supported production processes and return their keys."""
    known = learned_property_discoveries(conn, citizen_id)
    newly_learned: list[str] = []

    for process_key, process in PRODUCTION_PROCESSES.items():
        required = set(process["required_properties"])
        if not required.issubset(known):
            continue

        source_discovery_id = max(known[property_id] for property_id in required)
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO learned_processes
            (citizen_id, process_key, name, process_kind, source_discovery_id, learned_minute)
            VALUES (?, ?, ?, 'production', ?, ?)
            """,
            (
                citizen_id,
                process_key,
                str(process["name"]),
                source_discovery_id,
                int(learned_minute),
            ),
        )
        if cur.rowcount:
            newly_learned.append(process_key)

    return newly_learned


def sync_all_production_processes(conn, *, learned_minute: int) -> None:
    rows = conn.execute("SELECT id FROM citizens ORDER BY rowid").fetchall()
    for row in rows:
        sync_citizen_production_processes(
            conn,
            str(row["id"]),
            learned_minute=learned_minute,
        )


def citizen_knows_production_process(conn, citizen_id: str, process_key: str) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM learned_processes
        WHERE citizen_id = ?
          AND process_key = ?
          AND process_kind = 'production'
        LIMIT 1
        """,
        (citizen_id, process_key),
    ).fetchone()
    return bool(row)
