"""The seeded planet.

One integer seed decides the whole planet: the shape of the land around the
facility and where every resource deposit lies. The same seed always gives
the same planet, so a world can be rebuilt or shared exactly.

Milestone 1 models a 2 km square of surface around the facility. The rest of
the planet (and space) comes later, built on the same seed.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

REGION_SIZE_M = 2048.0          # side of the modeled surface square
GRID_RESOLUTION = 129           # height samples per side (16 m spacing)
FACILITY_PAD_RADIUS_M = 45.0    # flat ground the facility stands on
FACILITY_BLEND_RADIUS_M = 110.0 # where the pad blends back into the land
DEPOSIT_COUNT = 36
DEPOSIT_MIN_DISTANCE_FROM_FACILITY_M = 140.0

MATERIALS = ("iron_ore", "copper_ore", "silica_sand", "water_ice", "carbon")


@dataclass(frozen=True)
class Deposit:
    id: str
    material: str
    x_m: float
    y_m: float
    amount_kg: float
    depth_m: float


def _hash01(seed: int, ix: int, iy: int, salt: int) -> float:
    """Deterministic pseudo-random number in [0, 1) for a lattice point."""
    h = (ix * 374761393 + iy * 668265263 + seed * 2147483647 + salt * 1274126177) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return (h & 0xFFFFFF) / float(0x1000000)


def _smooth(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _value_noise(seed: int, x: float, y: float, salt: int) -> float:
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = _smooth(x - ix), _smooth(y - iy)
    a = _hash01(seed, ix, iy, salt)
    b = _hash01(seed, ix + 1, iy, salt)
    c = _hash01(seed, ix, iy + 1, salt)
    d = _hash01(seed, ix + 1, iy + 1, salt)
    top = a + (b - a) * fx
    bottom = c + (d - c) * fx
    return (top + (bottom - top) * fy) * 2.0 - 1.0  # [-1, 1]


def _raw_height(seed: int, x_m: float, y_m: float) -> float:
    height = 0.0
    amplitude = 38.0
    wavelength = 700.0
    for octave in range(5):
        height += amplitude * _value_noise(seed, x_m / wavelength, y_m / wavelength, octave)
        amplitude *= 0.48
        wavelength *= 0.5
    # A slow ridge line gives each planet a recognizable backbone.
    ridge = 1.0 - abs(_value_noise(seed, x_m / 1100.0, y_m / 1100.0, 17))
    return height + 26.0 * ridge * ridge


class Planet:
    """Read-only answers about the planet surface for one seed."""

    def __init__(self, seed: int):
        self.seed = int(seed)
        self._pad_height = _raw_height(self.seed, 0.0, 0.0)
        self._deposits: list[Deposit] | None = None

    # -- surface ---------------------------------------------------------
    def height_at(self, x_m: float, y_m: float) -> float:
        raw = _raw_height(self.seed, x_m, y_m)
        distance = math.hypot(x_m, y_m)
        if distance <= FACILITY_PAD_RADIUS_M:
            return self._pad_height
        if distance >= FACILITY_BLEND_RADIUS_M:
            return raw
        t = (distance - FACILITY_PAD_RADIUS_M) / (FACILITY_BLEND_RADIUS_M - FACILITY_PAD_RADIUS_M)
        t = _smooth(t)
        return self._pad_height + (raw - self._pad_height) * t

    def slope_at(self, x_m: float, y_m: float, step_m: float = 8.0) -> float:
        dx = self.height_at(x_m + step_m, y_m) - self.height_at(x_m - step_m, y_m)
        dy = self.height_at(x_m, y_m + step_m) - self.height_at(x_m, y_m - step_m)
        return math.hypot(dx, dy) / (2.0 * step_m)  # rise over run

    def in_region(self, x_m: float, y_m: float) -> bool:
        half = REGION_SIZE_M / 2.0
        return -half <= x_m <= half and -half <= y_m <= half

    def heightfield(self) -> dict:
        """The whole surface grid, for drawing. Contains no resource data."""
        half = REGION_SIZE_M / 2.0
        step = REGION_SIZE_M / (GRID_RESOLUTION - 1)
        heights = []
        for row in range(GRID_RESOLUTION):
            y = -half + row * step
            for col in range(GRID_RESOLUTION):
                x = -half + col * step
                heights.append(round(self.height_at(x, y), 2))
        return {
            "seed": self.seed,
            "size_m": REGION_SIZE_M,
            "resolution": GRID_RESOLUTION,
            "origin_height_m": round(self._pad_height, 2),
            "heights": heights,
        }

    # -- resources -------------------------------------------------------
    def _material_for(self, x_m: float, y_m: float, rng: random.Random) -> str:
        """The land decides what can be found where."""
        h = self.height_at(x_m, y_m) - self._pad_height
        slope = self.slope_at(x_m, y_m)
        if h < -18.0:
            return "water_ice"          # cold low basins
        if slope > 0.14 or h > 28.0:
            return "iron_ore" if rng.random() < 0.65 else "copper_ore"  # exposed rock
        if slope < 0.05:
            return "silica_sand" if rng.random() < 0.7 else "carbon"    # flats
        return rng.choice(("copper_ore", "carbon", "iron_ore"))

    def deposits(self) -> list[Deposit]:
        if self._deposits is not None:
            return self._deposits
        rng = random.Random(self.seed * 7919 + 13)
        half = REGION_SIZE_M / 2.0 - 40.0
        found: list[Deposit] = []
        attempts = 0
        while len(found) < DEPOSIT_COUNT and attempts < DEPOSIT_COUNT * 40:
            attempts += 1
            x = rng.uniform(-half, half)
            y = rng.uniform(-half, half)
            if math.hypot(x, y) < DEPOSIT_MIN_DISTANCE_FROM_FACILITY_M:
                continue
            if any(math.hypot(x - d.x_m, y - d.y_m) < 60.0 for d in found):
                continue
            material = self._material_for(x, y, rng)
            found.append(
                Deposit(
                    id=f"dep-{len(found) + 1:03d}",
                    material=material,
                    x_m=round(x, 1),
                    y_m=round(y, 1),
                    amount_kg=round(rng.uniform(400.0, 6000.0), 0),
                    depth_m=round(rng.uniform(0.0, 4.0), 1),
                )
            )
        self._deposits = found
        return found

    def surface_outcrops(self) -> list[dict]:
        """What anyone standing nearby can see: a rock outcrop or a pale patch.

        Shallow deposits show on the surface, but only as a look, never as a
        named material. Knowing what it is takes a survey (a later milestone).
        """
        visible = []
        for d in self.deposits():
            if d.depth_m > 1.5:
                continue
            look = "pale_patch" if d.material in ("silica_sand", "water_ice") else "dark_rock"
            visible.append({"x_m": d.x_m, "y_m": d.y_m, "look": look})
        return visible


def new_seed() -> int:
    return random.SystemRandom().randrange(1, 2**31 - 1)
