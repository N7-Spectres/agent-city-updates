from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_city.db as db


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db.DB_PATH = Path(tmp) / "data" / "agent_city.db"

        from agent_city.db import connect, init_db
        import main as app_main

        init_db()

        with connect() as conn:
            conn.execute("UPDATE resources SET amount = 61 WHERE name = 'Fasteners'")
            conn.execute(
                """
                INSERT INTO resources(name, amount) VALUES ('Plant Fiber', 17)
                ON CONFLICT(name) DO UPDATE SET amount = 17
                """
            )
            conn.execute(
                """
                INSERT INTO citizen_inventory(citizen_id, material, amount)
                VALUES ('cato', 'Plant Fiber', 4)
                ON CONFLICT(citizen_id, material) DO UPDATE SET amount = 4
                """
            )
            conn.execute(
                "UPDATE structures SET condition = 89.4 WHERE name = 'Charging Station'"
            )
            conn.execute(
                """
                UPDATE citizens
                SET integrity = 97.5, joint_wear = 4.2, battery_health = 99.1
                WHERE id = 'cato'
                """
            )
            conn.commit()

        payload = app_main.troubleshooting_snapshot()
        assert payload["snapshot_type"] == "agent_city_troubleshooting"
        assert payload["privacy"]["local_only_until_copied"] is True
        assert payload["privacy"]["hidden_world_seed_included"] is False
        assert payload["privacy"]["undiscovered_world_truth_included"] is False
        assert payload["privacy"]["conversation_content_included"] is False

        storage = {row["material"]: row for row in payload["storage"]}
        assert storage["Fasteners"]["stored"] == 61
        assert storage["Fasteners"]["starter"] == 100
        assert storage["Fasteners"]["change_from_starter"] == -39
        assert storage["Plant Fiber"]["stored"] == 17
        assert storage["Plant Fiber"]["starter"] is None
        assert storage["Plant Fiber"]["starter_stock"] is False

        cargo = payload["field_cargo"]
        assert any(
            row["citizen_id"] == "cato"
            and row["material"] == "Plant Fiber"
            and row["amount"] == 4
            for row in cargo
        )

        cato = next(row for row in payload["citizens"] if row["id"] == "cato")
        assert cato["integrity"] == 97.5
        assert cato["joint_wear"] == 4.2
        assert cato["battery_health"] == 99.1

        charger = next(
            row for row in payload["structures"]
            if row["name"] == "Charging Station"
        )
        assert charger["condition"] == 89.4

        forbidden = {
            "planet_seed",
            "generated_deposits",
            "world_properties",
            "richness",
            "axis_major_m",
            "axis_minor_m",
            "citizen_conversations",
            "conversation",
            "messages",
        }
        keys = {key.lower() for key in walk_keys(payload)}
        assert not (keys & forbidden), f"Troubleshooting snapshot leaked forbidden keys: {keys & forbidden}"

        serialized = json.dumps(payload)
        assert "planet_seed" not in serialized
        assert "generated_deposits" not in serialized

        root = Path(__file__).resolve().parents[1]
        app_js = (root / "static" / "app.js").read_text(encoding="utf-8")
        index_html = (root / "static" / "index.html").read_text(encoding="utf-8")
        assert "/api/diagnostics/troubleshooting-snapshot" in app_js
        assert "Copy troubleshooting snapshot" in index_html
        assert "Nothing is uploaded automatically." in index_html
        assert "navigator.clipboard" in app_js
        assert "Current public physical state copied" in app_js

        print("v0.9.27 troubleshooting snapshot smoke passed")


if __name__ == "__main__":
    main()
