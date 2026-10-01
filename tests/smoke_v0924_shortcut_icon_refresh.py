from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
launcher_path = ROOT / "agent_city_launcher.pyw"
installer_path = ROOT / "install_desktop_shortcut.ps1"

launcher = launcher_path.read_text(encoding="utf-8")
installer = installer_path.read_text(encoding="utf-8")

compile(launcher, str(launcher_path), "exec")

# Existing canonical icon contract remains intact.
assert 'APP_ICON = PROJECT_ROOT / "static" / "assets" / "app" / "agent-city.ico"' in launcher
assert 'static\\assets\\app\\agent-city.ico' in installer
assert '$shortcut.IconLocation = $customIconPath + ",0"' in installer

# The shortcut installer can now run silently during an update resume.
assert "[switch]$Quiet" in installer
assert "if (-not $Quiet)" in installer

# Re-saving the .lnk is followed by a shell icon metadata notification so
# Explorer does not keep the generic white-paper icon cached indefinitely.
assert "$shortcut.Save()" in installer
assert "AgentCityShellRefresh" in installer
assert "SHChangeNotify" in installer
assert "0x08000000" in installer

# A freshly installed update invokes the quiet shortcut rebuild from the NEW
# launcher code, which is important because the old update_runner performs the
# v0.9.23 -> v0.9.24 file replacement.
assert 'SHORTCUT_INSTALLER = PROJECT_ROOT / "install_desktop_shortcut.ps1"' in launcher
assert "def _refresh_desktop_shortcut() -> None:" in launcher
assert '"-Quiet",' in launcher
assert "if resume_after_update:" in launcher
assert "_refresh_desktop_shortcut()" in launcher
assert 'timeout=15.0' in launcher

# This remains presentation/launcher polish, not Simulation authority.
for forbidden in [
    "position_x_m =",
    "position_y_m =",
    "energy =",
    "health =",
]:
    assert forbidden not in launcher

print("v0.9.24 desktop shortcut icon-refresh smoke passed.")
