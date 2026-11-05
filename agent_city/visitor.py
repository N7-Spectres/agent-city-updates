"""N7 (or any visitor) walking in the world.

The browser moves the visitor smoothly with the arrow keys and reports where
they are. The simulation still decides reality: a reported step that is too
fast, goes through a wall, or leaves the map is refused, and the visitor stays
at the last real position.
"""
from __future__ import annotations

import math
import time

from .store import connect, ensure_visitor, load_structures
from .world.planet import REGION_SIZE_M

VISITOR_MAX_SPEED_M_S = 4.0     # a brisk jog
MOVE_TOLERANCE_M = 0.75         # slack for network timing
VISITOR_BODY_RADIUS_M = 0.35


def _blocked(structures: list[dict], x: float, y: float) -> bool:
    r = VISITOR_BODY_RADIUS_M
    for s in structures:
        if not s["solid"]:
            continue
        if abs(x - s["x_m"]) <= s["width_m"] / 2 + r and abs(y - s["y_m"]) <= s["depth_m"] / 2 + r:
            return True
    return False


def _path_blocked(structures: list[dict], x0: float, y0: float, x1: float, y1: float) -> bool:
    steps = max(1, int(math.hypot(x1 - x0, y1 - y0) / 0.2))
    for i in range(1, steps + 1):
        t = i / steps
        if _blocked(structures, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t):
            return True
    return False


def visitor_state(name: str) -> dict:
    with connect() as conn:
        row = ensure_visitor(conn, name)
        return {"name": row["name"], "x_m": row["x_m"], "y_m": row["y_m"], "heading": row["heading"]}


def move_visitor(name: str, x: float, y: float, heading: float, now: float | None = None) -> dict:
    """Try to move the visitor. Returns the position the world accepted."""
    now = time.time() if now is None else now
    with connect() as conn:
        row = ensure_visitor(conn, name)
        x0, y0 = row["x_m"], row["y_m"]
        elapsed = max(0.0, min(now - row["updated_at"], 2.0))
        allowed = VISITOR_MAX_SPEED_M_S * elapsed + MOVE_TOLERANCE_M
        structures = load_structures(conn)
        half = REGION_SIZE_M / 2.0 - 1.0

        accepted = True
        reason = ""
        if not all(math.isfinite(v) for v in (x, y, heading)):
            accepted, reason = False, "invalid position"
        elif abs(x) > half or abs(y) > half:
            accepted, reason = False, "edge of the mapped land"
        elif math.hypot(x - x0, y - y0) > allowed:
            accepted, reason = False, "too far in one step"
        elif _path_blocked(structures, x0, y0, x, y):
            accepted, reason = False, "something solid is in the way"

        if accepted:
            conn.execute(
                "UPDATE visitors SET x_m = ?, y_m = ?, heading = ?, updated_at = ? WHERE name = ?",
                (x, y, heading, now, name),
            )
            return {"accepted": True, "name": name, "x_m": x, "y_m": y, "heading": heading}
        conn.execute("UPDATE visitors SET updated_at = ? WHERE name = ?", (now, name))
        return {
            "accepted": False, "reason": reason, "name": name,
            "x_m": x0, "y_m": y0, "heading": row["heading"],
        }
