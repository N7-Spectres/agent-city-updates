"""World time. Runs at time_scale sim seconds per real second (default 4x)."""
from __future__ import annotations

import asyncio

from .store import connect, get_meta, set_meta

TICK_REAL_SECONDS = 1.0


def sim_seconds() -> float:
    with connect() as conn:
        return float(get_meta(conn, "sim_seconds", "0"))


def advance(real_seconds: float) -> float:
    with connect() as conn:
        if get_meta(conn, "paused", "0") == "1":
            return float(get_meta(conn, "sim_seconds", "0"))
        scale = float(get_meta(conn, "time_scale", "4"))
        now = float(get_meta(conn, "sim_seconds", "0")) + real_seconds * scale
        set_meta(conn, "sim_seconds", round(now, 3))
        return now


def set_paused(paused: bool) -> None:
    with connect() as conn:
        set_meta(conn, "paused", 1 if paused else 0)


def describe(seconds: float) -> dict:
    total_minutes = int(seconds // 60)
    day = total_minutes // (24 * 60) + 1
    minute_of_day = total_minutes % (24 * 60)
    return {
        "sim_seconds": seconds,
        "day": day,
        "hour": minute_of_day // 60,
        "minute": minute_of_day % 60,
        "label": f"Day {day}, {minute_of_day // 60:02d}:{minute_of_day % 60:02d}",
    }


async def run_clock(stop: asyncio.Event) -> None:
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=TICK_REAL_SECONDS)
        except asyncio.TimeoutError:
            advance(TICK_REAL_SECONDS)
