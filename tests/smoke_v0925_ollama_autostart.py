from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
launcher_path = ROOT / "agent_city_launcher.pyw"
launcher = launcher_path.read_text(encoding="utf-8")

compile(launcher, str(launcher_path), "exec")

required = [
    'OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"',
    'OLLAMA_LOG = DATA_DIR / "ollama.log"',
    "OLLAMA_STARTUP_TIMEOUT_SECONDS = 45.0",
    "def _ollama_is_ready()",
    "def _find_ollama_executable()",
    "shutil.which",
    '"Programs" / "Ollama" / "ollama.exe"',
    "def _start_ollama()",
    '[executable, "serve"]',
    "CREATE_NO_WINDOW",
    "def _ensure_ollama(",
    "_ensure_ollama()",
    "Ollama is already running.",
    "Agent City will continue",
]
for fragment in required:
    assert fragment in launcher, f"Ollama auto-start contract missing: {fragment}"

# Existing desktop/tray/update contracts must remain present.
for fragment in [
    "AgentCityDesktopLauncher",
    "agent_city_tray.ps1",
    "--resume-after-update",
    "launcher_exit_for_update.flag",
    "_refresh_desktop_shortcut()",
]:
    assert fragment in launcher, f"Existing launcher contract regressed: {fragment}"

# Auto-start must not be implemented by shelling out through a visible cmd.exe.
assert "cmd.exe" not in launcher.lower()

print("v0.9.25 Ollama auto-start smoke passed")
