"""The visitor walks; the simulation decides whether the step was real."""
import unittest

from agent_city.store import init_world
from agent_city.visitor import move_visitor, visitor_state
from tests.helpers import FreshWorldTest


class VisitorTests(FreshWorldTest):
    def setUp(self):
        super().setUp()
        init_world(seed=5)
        self.start = visitor_state("N7")
        self.t = 1_000_000.0
        move_visitor("N7", self.start["x_m"], self.start["y_m"], self.start["heading"], now=self.t)

    def step(self, x, y, dt=0.5):
        self.t += dt
        return move_visitor("N7", x, y, 1.57, now=self.t)

    def test_normal_walking_is_accepted(self):
        r = self.step(0.0, -20.5)
        self.assertTrue(r["accepted"])
        self.assertEqual(visitor_state("N7")["y_m"], -20.5)

    def test_no_teleporting(self):
        r = self.step(0.0, 0.0)
        self.assertFalse(r["accepted"])
        self.assertEqual(r["reason"], "too far in one step")
        self.assertEqual(visitor_state("N7")["y_m"], -21.0)

    def test_cannot_walk_through_a_wall(self):
        # Walk to just outside the south wall, beside the door.
        y = -21.0
        x = 0.0
        for _ in range(8):
            x += 0.75
            self.assertTrue(self.step(x, y)["accepted"])
        while y < -13.5:
            y += 1.0
            self.assertTrue(self.step(x, y)["accepted"])
        r = self.step(x, y + 1.5)
        self.assertFalse(r["accepted"])
        self.assertEqual(r["reason"], "something solid is in the way")

    def test_can_walk_in_through_the_door(self):
        y = -21.0
        while y < -5.0:
            y += 1.0
            self.assertTrue(self.step(0.0, y)["accepted"], f"blocked at y={y}")

    def test_cannot_leave_the_mapped_land(self):
        r = move_visitor("N7", 5000.0, 0.0, 0.0, now=self.t + 1)
        self.assertFalse(r["accepted"])


if __name__ == "__main__":
    unittest.main()
