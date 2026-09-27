import asyncio
import time
from .db import connect, get_meta, set_meta
from .simulation import complete_due_jobs

class WorldClock:
    def __init__(self) -> None:
        self._running = False
        self._last_real = time.monotonic()
        self._fractional_sim_minutes = 0.0

    async def run(self) -> None:
        self._running = True
        self._last_real = time.monotonic()

        while self._running:
            await asyncio.sleep(1.0)
            now = time.monotonic()
            elapsed_real_seconds = now - self._last_real
            self._last_real = now

            with connect() as conn:
                paused = (get_meta(conn, "paused") or "false") == "true"
                ratio = float(get_meta(conn, "time_ratio") or "4.0")
                if paused:
                    continue

                sim_minutes_added = (elapsed_real_seconds * ratio) / 60.0
                self._fractional_sim_minutes += sim_minutes_added

                whole_minutes = int(self._fractional_sim_minutes)
                if whole_minutes > 0:
                    current = int(get_meta(conn, "sim_minute") or "360")
                    new_minute = current + whole_minutes
                    set_meta(conn, "sim_minute", new_minute)
                    conn.commit()
                    self._fractional_sim_minutes -= whole_minutes

            if whole_minutes > 0:
                complete_due_jobs(new_minute)

    def stop(self) -> None:
        self._running = False


def format_sim_time(sim_minute: int) -> str:
    day = sim_minute // 1440 + 1
    minute_of_day = sim_minute % 1440
    hour = minute_of_day // 60
    minute = minute_of_day % 60
    return f"Day {day} • {hour:02d}:{minute:02d}"
