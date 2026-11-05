"""The six founding directors.

Each one leads a division. Heights come from N7's concept sheets.
Memory starts empty: v2 is a fresh world.
"""
from __future__ import annotations

FOUNDERS = (
    # id, name, division, height_m  (divisions from N7's concept sheets)
    ("aris", "Aris", "Navigation and surveying", 1.85),
    ("bex", "Bex", "Fabrication and building", 1.60),
    ("cato", "Cato", "Infrastructure and hauling", 2.10),
    ("iri", "Iri", "Research and analysis", 1.78),
    ("noma", "Noma", "Environment and field science", 1.60),
    ("vale", "Vale", "Care and coordination", 2.00),
)

WALK_SPEED_M_S = 1.4


def founders() -> list[dict]:
    return [
        {"id": cid, "name": name, "division": division, "height_m": height}
        for cid, name, division, height in FOUNDERS
    ]
