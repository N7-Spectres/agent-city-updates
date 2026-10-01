from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

launcher_path = ROOT / "agent_city_launcher.pyw"
installer_path = ROOT / "install_desktop_shortcut.ps1"
cmd_path = ROOT / "install_agent_city_shortcut.cmd"

assert launcher_path.exists(), "Desktop launcher is missing"
assert installer_path.exists(), "Desktop shortcut installer is missing"
assert cmd_path.exists(), "Desktop shortcut helper is missing"

launcher = launcher_path.read_text(encoding="utf-8")
compile(launcher, str(launcher_path), "exec")

required_launcher_fragments = [
    "pythonw.exe",
    "CREATE_NO_WINDOW",
    "CREATE_NEW_PROCESS_GROUP",
    "webbrowser.open",
    "http://127.0.0.1:8000/api/state",
    "Agent City was already running",
    "server.log",
]
for fragment in required_launcher_fragments:
    assert fragment in launcher, f"Launcher contract missing: {fragment}"

installer = installer_path.read_text(encoding="utf-8")
required_installer_fragments = [
    "WScript.Shell",
    "Agent City.lnk",
    "agent_city_launcher.pyw",
    "static\\assets\\app\\agent-city.ico",
    ".venv\\Scripts\\pythonw.exe",
]
for fragment in required_installer_fragments:
    assert fragment in installer, f"Shortcut installer contract missing: {fragment}"

cmd = cmd_path.read_text(encoding="utf-8").lower()
assert "powershell.exe" in cmd
assert "install_desktop_shortcut.ps1" in cmd

print("v0.9.20 desktop launcher phase-1 smoke passed")
