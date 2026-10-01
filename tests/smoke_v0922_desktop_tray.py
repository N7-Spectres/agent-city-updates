from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

launcher_path = ROOT / "agent_city_launcher.pyw"
tray_path = ROOT / "agent_city_tray.ps1"
runner_path = ROOT / "update_runner.py"
main_path = ROOT / "main.py"
requirements_path = ROOT / "requirements.txt"

launcher = launcher_path.read_text(encoding="utf-8")
tray = tray_path.read_text(encoding="utf-8")
runner = runner_path.read_text(encoding="utf-8")
main = main_path.read_text(encoding="utf-8")
requirements = requirements_path.read_text(encoding="utf-8").lower()

compile(launcher, str(launcher_path), "exec")
compile(runner, str(runner_path), "exec")
compile(main, str(main_path), "exec")

for fragment in [
    "AgentCityDesktopLauncher",
    "launcher_status.json",
    "launcher_command.json",
    "launcher_exit_for_update.flag",
    "/api/launcher/shutdown",
    "--startup",
    "--resume-after-update",
    '"Running"',
    '"Restarting"',
    '"Updating"',
    '"Error"',
    "_monitor(",
    "AGENT_CITY_LAUNCHER_PID",
]:
    assert fragment in launcher, f"Desktop supervisor contract missing: {fragment}"

for fragment in [
    "System.Windows.Forms.NotifyIcon",
    "Open Agent City",
    "Restart Agent City",
    "Quit Agent City",
    "Start with Windows",
    "CurrentVersion\\Run",
    "agent-city.ico",
    "Status: Starting",
    "DoubleClick",
]:
    assert fragment in tray, f"Tray contract missing: {fragment}"

for fragment in [
    '@app.post("/api/launcher/shutdown")',
    "launcher_exit_for_update.flag",
    "AGENT_CITY_LAUNCHER_PID",
    '"launcher_pid": launcher_pid',
]:
    assert fragment in main, f"Runtime launcher handoff missing: {fragment}"

for fragment in [
    'launcher_pid = int(job.get("launcher_pid") or 0)',
    "waiting for desktop supervisor PID",
    "timeout=15.0",
    "launcher_exit_for_update.flag",
    "job_path.unlink(missing_ok=True)",
    "--resume-after-update",
]:
    assert fragment in runner, f"Updater supervisor handoff missing: {fragment}"

assert "pystray" not in requirements
assert "pillow" not in requirements

print("v0.9.22 desktop tray/supervisor smoke passed")
