"""The six founding directors.

Each one leads a division. Heights come from N7's concept sheets.
Memory starts empty: v2 is a fresh world.
"""
from __future__ import annotations

FOUNDERS = (
    # id, name, division, height_m
    ("aris", "Aris", "Extraction and prospecting", 1.85),
    ("bex", "Bex", "Fabrication", 1.60),
    ("cato", "Cato", "Logistics and resource planning", 2.10),
    ("iri", "Iri", "Construction", 1.78),
    ("noma", "Noma", "Research and experiments", 1.60),
    ("vale", "Vale", "Cooperation", 2.00),
)

WALK_SPEED_M_S = 1.4


def founders() -> list[dict]:
    return [
        {"id": cid, "name": name, "division": division, "height_m": height}
        for cid, name, division, height in FOUNDERS
    ]
