from __future__ import annotations

import os
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_PACKAGE = ROOT / "releases" / "Agent_City_v0.2.3_Built_In_Updater.zip"
PATCH_ROOT = ROOT / "patch"


def main() -> None:
    if not BASE_PACKAGE.exists():
        raise SystemExit("Agent City update bootstrap could not find the v0.2.3 base package.")

    # Restore the complete, known-good v0.2.3 application first.
    with zipfile.ZipFile(BASE_PACKAGE, "r") as archive:
        archive.extractall(ROOT)

    # Apply the v0.2.4 interface files and version marker.
    static_patch = PATCH_ROOT / "static"
    static_target = ROOT / "static"
    static_target.mkdir(parents=True, exist_ok=True)

    for source in static_patch.iterdir():
        if source.is_file():
            shutil.copy2(source, static_target / source.name)

    shutil.copy2(PATCH_ROOT / "VERSION", ROOT / "VERSION")

    # Remove release-only scaffolding after the update has been assembled.
    for extra in (PATCH_ROOT, ROOT / "releases"):
        if extra.exists():
            shutil.rmtree(extra, ignore_errors=True)

    for extra_file in (ROOT / "update.json",):
        try:
            extra_file.unlink()
        except FileNotFoundError:
            pass

    # The extraction replaced this bootstrap on disk with the real application.
    os.execv(sys.executable, [sys.executable, str(ROOT / "main.py")])


if __name__ == "__main__":
    main()
