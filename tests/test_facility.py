"""The starting facility has what N7 asked for, and nothing overlaps."""
import math
import unittest

from agent_city.world.facility import (
    VISITOR_SPAWN, blocked, meeting_seats, solid_structures, starting_facility,
)


class FacilityTests(unittest.TestCase):
    def setUp(self):
        self.structures = starting_facility()
        self.kinds = [s.kind for s in self.structures]

    def test_has_two_repair_stations_and_room_for_more(self):
        self.assertEqual(self.kinds.count("repair_station"), 2)
        self.assertGreaterEqual(self.kinds.count("expansion_bay"), 2)

    def test_has_storage_work_station_and_meeting_table(self):
        for kind in ("storage", "work_station", "meeting_table", "door"):
            self.assertIn(kind, self.kinds)

    def test_meeting_table_seats_all_six_directors_facing_it(self):
        seats = meeting_seats(6)
        self.assertEqual(len(seats), 6)
        for x, y, heading in seats:
            self.assertFalse(blocked(x, y), "a seat is inside something solid")
            table = next(s for s in self.structures if s.kind == "meeting_table")
            to_table = math.atan2(table.y_m - y, table.x_m - x)
            self.assertAlmostEqual(math.cos(heading - to_table), 1.0, places=6)

    def test_solid_things_do_not_overlap_each_other(self):
        solids = [s for s in solid_structures() if s.kind != "wall"]
        for i, a in enumerate(solids):
            for b in solids[i + 1:]:
                overlap_x = abs(a.x_m - b.x_m) < (a.width_m + b.width_m) / 2
                overlap_y = abs(a.y_m - b.y_m) < (a.depth_m + b.depth_m) / 2
                self.assertFalse(overlap_x and overlap_y, f"{a.id} overlaps {b.id}")

    def test_stations_are_standable(self):
        for s in self.structures:
            if s.kind in ("repair_station", "expansion_bay"):
                self.assertFalse(blocked(s.x_m, s.y_m), f"nobody can stand at {s.id}")

    def test_the_door_is_open_and_the_walls_are_not(self):
        self.assertFalse(blocked(0.0, -11.0))       # through the door
        self.assertTrue(blocked(6.0, -11.0))        # south wall beside it
        self.assertTrue(blocked(0.0, 11.0))         # north wall
        self.assertFalse(blocked(*VISITOR_SPAWN[:2]))


if __name__ == "__main__":
    unittest.main()
