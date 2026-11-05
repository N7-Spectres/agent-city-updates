"""The starting facility: one building where the city begins.

Coordinates are meters on the planet surface, with the facility centered on
(0, 0). +x is east, +y is north. The only door is in the middle of the south
wall.

Inside:
  - Repair bay (west): 4 bays, 2 with repair stations, 2 left empty so the
    crew can add more stations when they decide they need them.
  - Storage center (east)
  - Work station (south-east)
  - Meeting table (middle) with a seat for each of the six directors
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

BUILDING_WIDTH_M = 32.0   # east-west
BUILDING_DEPTH_M = 22.0   # north-south
WALL_THICKNESS_M = 0.4
WALL_HEIGHT_M = 4.5
DOOR_WIDTH_M = 3.2

MEETING_TABLE_CENTER = (0.0, 2.5)
MEETING_TABLE_RADIUS_M = 2.0
MEETING_SEAT_RADIUS_M = 3.1


@dataclass(frozen=True)
class Structure:
    id: str
    kind: str
    name: str
    x_m: float
    y_m: float
    width_m: float
    depth_m: float
    height_m: float
    solid: bool          # True = nobody can walk through it
    status: str = "working"
    shape: str = "box"   # "box" or "round" (drawing only; collision uses the box)
    meta: dict = field(default_factory=dict)

    def contains(self, x: float, y: float, margin: float = 0.0) -> bool:
        return (
            abs(x - self.x_m) <= self.width_m / 2.0 + margin
            and abs(y - self.y_m) <= self.depth_m / 2.0 + margin
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "x_m": self.x_m,
            "y_m": self.y_m,
            "width_m": self.width_m,
            "depth_m": self.depth_m,
            "height_m": self.height_m,
            "solid": self.solid,
            "status": self.status,
            "shape": self.shape,
            **({"meta": self.meta} if self.meta else {}),
        }


def _walls() -> list[Structure]:
    w, d, t, h = BUILDING_WIDTH_M, BUILDING_DEPTH_M, WALL_THICKNESS_M, WALL_HEIGHT_M
    half_w, half_d = w / 2.0, d / 2.0
    side_len = (w - DOOR_WIDTH_M) / 2.0
    return [
        Structure("wall-north", "wall", "North wall", 0.0, half_d, w, t, h, True),
        Structure("wall-west", "wall", "West wall", -half_w, 0.0, t, d, h, True),
        Structure("wall-east", "wall", "East wall", half_w, 0.0, t, d, h, True),
        Structure("wall-south-west", "wall", "South wall", -(DOOR_WIDTH_M / 2.0 + side_len / 2.0), -half_d, side_len, t, h, True),
        Structure("wall-south-east", "wall", "South wall", DOOR_WIDTH_M / 2.0 + side_len / 2.0, -half_d, side_len, t, h, True),
    ]


def starting_facility() -> list[Structure]:
    s: list[Structure] = [
        Structure("floor", "floor", "Seed Station floor", 0.0, 0.0, BUILDING_WIDTH_M, BUILDING_DEPTH_M, 0.15, False),
        *_walls(),
        Structure("door-south", "door", "Main door", 0.0, -BUILDING_DEPTH_M / 2.0, DOOR_WIDTH_M, WALL_THICKNESS_M, 3.4, False),
        # Repair bay: four bays down the west side, two of them equipped.
        Structure("repair-1", "repair_station", "Repair station 1", -12.5, 7.0, 3.0, 3.0, 2.6, False),
        Structure("repair-2", "repair_station", "Repair station 2", -12.5, 2.5, 3.0, 3.0, 2.6, False),
        Structure("repair-bay-3", "expansion_bay", "Empty repair bay", -12.5, -2.0, 3.0, 3.0, 0.05, False, status="empty"),
        Structure("repair-bay-4", "expansion_bay", "Empty repair bay", -12.5, -6.5, 3.0, 3.0, 0.05, False, status="empty"),
        # Storage center: racks along the east wall with a counter in front.
        Structure("storage-racks", "storage", "Storage center", 13.4, 4.5, 3.6, 9.0, 3.2, True),
        Structure("storage-counter", "storage_counter", "Storage counter", 10.2, 4.5, 1.0, 5.0, 1.05, True),
        # Work station: a fabrication bench.
        Structure("work-station", "work_station", "Work station", 10.5, -6.5, 5.0, 2.0, 1.0, True),
        # Meeting table in the middle of the hall.
        Structure(
            "meeting-table", "meeting_table", "Meeting table",
            MEETING_TABLE_CENTER[0], MEETING_TABLE_CENTER[1],
            MEETING_TABLE_RADIUS_M * 2.0, MEETING_TABLE_RADIUS_M * 2.0, 0.95, True, shape="round",
            meta={"seats": 6},
        ),
    ]
    return s


def meeting_seats(count: int = 6) -> list[tuple[float, float, float]]:
    """(x, y, heading) for each seat, facing the table center."""
    cx, cy = MEETING_TABLE_CENTER
    seats = []
    for i in range(count):
        angle = math.pi / 2.0 + i * (2.0 * math.pi / count)
        x = cx + MEETING_SEAT_RADIUS_M * math.cos(angle)
        y = cy + MEETING_SEAT_RADIUS_M * math.sin(angle)
        heading = math.atan2(cy - y, cx - x)
        seats.append((round(x, 3), round(y, 3), round(heading, 4)))
    return seats


VISITOR_SPAWN = (0.0, -20.0, math.pi / 2.0)  # outside the door, facing it


def solid_structures(structures: list[Structure] | None = None) -> list[Structure]:
    return [s for s in (structures or starting_facility()) if s.solid]


def blocked(x: float, y: float, body_radius_m: float = 0.35, structures: list[Structure] | None = None) -> bool:
    """True if a body of this radius standing at (x, y) would overlap something solid."""
    return any(s.contains(x, y, margin=body_radius_m) for s in solid_structures(structures))
