"""The planet comes from its seed, and the land decides where resources are."""
import math
import unittest

from agent_city.world.planet import (
    DEPOSIT_MIN_DISTANCE_FROM_FACILITY_M, FACILITY_PAD_RADIUS_M, MATERIALS, REGION_SIZE_M, Planet,
)


class PlanetTests(unittest.TestCase):
    def test_same_seed_gives_the_same_planet(self):
        a, b = Planet(4242), Planet(4242)
        self.assertEqual(a.heightfield()["heights"], b.heightfield()["heights"])
        self.assertEqual(a.deposits(), b.deposits())

    def test_different_seeds_give_different_planets(self):
        self.assertNotEqual(Planet(1).deposits(), Planet(2).deposits())
        self.assertNotEqual(Planet(1).height_at(300, 300), Planet(2).height_at(300, 300))

    def test_facility_stands_on_flat_ground(self):
        p = Planet(77)
        center = p.height_at(0, 0)
        for angle in range(0, 360, 30):
            r = FACILITY_PAD_RADIUS_M - 1
            x, y = r * math.cos(math.radians(angle)), r * math.sin(math.radians(angle))
            self.assertAlmostEqual(p.height_at(x, y), center, places=6)

    def test_deposits_are_real_and_away_from_the_facility(self):
        for seed in (3, 99, 123456):
            deposits = Planet(seed).deposits()
            self.assertGreaterEqual(len(deposits), 20)
            for d in deposits:
                self.assertIn(d.material, MATERIALS)
                self.assertGreater(d.amount_kg, 0)
                self.assertGreaterEqual(math.hypot(d.x_m, d.y_m), DEPOSIT_MIN_DISTANCE_FROM_FACILITY_M)
                self.assertLessEqual(abs(d.x_m), REGION_SIZE_M / 2)
                self.assertLessEqual(abs(d.y_m), REGION_SIZE_M / 2)

    def test_ice_only_forms_in_low_basins(self):
        for seed in (5, 6, 7, 8):
            p = Planet(seed)
            for d in p.deposits():
                if d.material == "water_ice":
                    self.assertLess(p.height_at(d.x_m, d.y_m) - p.height_at(0, 0), -18.0)

    def test_heightfield_holds_no_resource_secrets(self):
        field = Planet(10).heightfield()
        self.assertEqual(set(field), {"seed", "size_m", "resolution", "origin_height_m", "heights"})

    def test_outcrops_show_a_look_never_a_material(self):
        for o in Planet(11).surface_outcrops():
            self.assertEqual(set(o), {"x_m", "y_m", "look"})
            self.assertNotIn(o["look"], MATERIALS)


if __name__ == "__main__":
    unittest.main()
