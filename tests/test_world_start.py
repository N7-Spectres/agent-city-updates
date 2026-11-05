"""A fresh world: memory wiped, six directors at the meeting table."""
import unittest

from agent_city.store import connect, get_meta, init_world
from tests.helpers import FreshWorldTest


class WorldStartTests(FreshWorldTest):
    def test_first_start_creates_the_world_once(self):
        seed = init_world(seed=31337)
        self.assertEqual(seed, 31337)
        self.assertEqual(init_world(seed=999), 31337, "a second start must not replace the world")

    def test_six_directors_one_per_division(self):
        init_world(seed=1)
        with connect() as conn:
            rows = conn.execute("SELECT id, role, division FROM citizens").fetchall()
        self.assertEqual(sorted(r["id"] for r in rows), ["aris", "bex", "cato", "iri", "noma", "vale"])
        self.assertTrue(all(r["role"] == "director" for r in rows))
        self.assertEqual(len({r["division"] for r in rows}), 6)

    def test_world_starts_in_the_morning(self):
        init_world(seed=1)
        with connect() as conn:
            self.assertEqual(float(get_meta(conn, "sim_seconds")), 8 * 3600)

    def test_deposits_are_stored_as_world_truth(self):
        init_world(seed=1)
        with connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM deposits").fetchone()[0]
        self.assertGreater(count, 0)


if __name__ == "__main__":
    unittest.main()
