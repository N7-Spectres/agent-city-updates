"""What the browser is sent: only what a visitor could see."""
import json
import unittest

from fastapi.testclient import TestClient

from tests.helpers import FreshWorldTest


class ApiTests(FreshWorldTest):
    def setUp(self):
        super().setUp()
        import main
        self.client_cm = TestClient(main.app)
        self.client = self.client_cm.__enter__()

    def tearDown(self):
        self.client_cm.__exit__(None, None, None)
        super().tearDown()

    def test_state_has_the_world_and_no_deposits(self):
        r = self.client.get("/api/state")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertEqual(len(body["citizens"]), 6)
        self.assertIn("seed", body["world"])
        text = json.dumps(body)
        for secret in ("deposit", "iron_ore", "copper_ore", "silica_sand", "water_ice", "amount_kg"):
            self.assertNotIn(secret, text)

    def test_terrain_has_no_materials(self):
        body = self.client.get("/api/world/terrain").json()
        self.assertEqual(len(body["heights"]), body["resolution"] ** 2)
        text = json.dumps(body["outcrops"])
        for secret in ("iron_ore", "copper_ore", "silica_sand", "water_ice", "carbon", "amount_kg"):
            self.assertNotIn(secret, text)

    def test_index_page_loads(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Seed Station", r.text)

    def test_update_status_still_answers(self):
        r = self.client.get("/api/update/status")
        self.assertEqual(r.status_code, 200)
        self.assertIn("current_version", r.json())


if __name__ == "__main__":
    unittest.main()
