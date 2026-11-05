import os
import tempfile
import unittest


class FreshWorldTest(unittest.TestCase):
    """Each test gets its own empty world database."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old = os.environ.get("AGENT_CITY_WORLD_DB")
        os.environ["AGENT_CITY_WORLD_DB"] = os.path.join(self._tmp.name, "world.db")

    def tearDown(self):
        if self._old is None:
            os.environ.pop("AGENT_CITY_WORLD_DB", None)
        else:
            os.environ["AGENT_CITY_WORLD_DB"] = self._old
        self._tmp.cleanup()
