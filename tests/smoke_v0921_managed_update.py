from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

runner_path = ROOT / "update_runner.py"
launcher_path = ROOT / "agent_city_launcher.pyw"
app_path = ROOT / "static" / "app.js"

runner = runner_path.read_text(encoding="utf-8")
launcher = launcher_path.read_text(encoding="utf-8")
app = app_path.read_text(encoding="utf-8")

compile(runner, str(runner_path), "exec")
compile(launcher, str(launcher_path), "exec")

for fragment in [
    "agent_city_launcher.pyw",
    "--resume-after-update",
    "update_runner.log",
    "did not exit within the safety timeout",
    "direct runtime fallback",
    "CREATE_NO_WINDOW",
]:
    assert fragment in runner, f"Phase-2 update runner contract missing: {fragment}"

assert "return True" in runner
assert "return False" in runner
assert "PRESERVE_NAMES" in runner
assert '"data"' in runner
assert '"backups"' in runner
assert '"update_staging"' in runner

assert "const UPDATE_REFRESH_MS = 300000;" in app
assert "setInterval(refreshUpdateStatus, UPDATE_REFRESH_MS);" in app
assert 'fetch("/api/update/status")' in app
assert 'fetch("/api/update/install", { method: "POST" })' in app
assert "This page will reconnect automatically." in app

print("v0.9.21 managed update/relaunch smoke passed")
