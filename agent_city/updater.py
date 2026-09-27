
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import urllib.parse
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"
STAGING_DIR = PROJECT_ROOT / "update_staging"
SETTINGS_PATH = DATA_DIR / "update_settings.json"
VERSION_PATH = PROJECT_ROOT / "VERSION"

PRESERVE_NAMES = {
    ".venv",
    "data",
    "backups",
    "update_staging",
}


def current_version() -> str:
    try:
        return VERSION_PATH.read_text(encoding="utf-8").strip() or "0.0.0"
    except FileNotFoundError:
        return "0.0.0"


def _version_tuple(value: str) -> tuple[int, ...]:
    clean = value.strip().lstrip("vV").split("-", 1)[0]
    parts = []
    for piece in clean.split("."):
        try:
            parts.append(int(piece))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:4])


def is_newer(remote: str, local: str) -> bool:
    return _version_tuple(remote) > _version_tuple(local)


def load_settings() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        return {"manifest_url": ""}
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"manifest_url": ""}
        return {"manifest_url": str(data.get("manifest_url", "")).strip()}
    except Exception:
        return {"manifest_url": ""}


def save_settings(manifest_url: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps({"manifest_url": manifest_url.strip()}, indent=2),
        encoding="utf-8",
    )


def _validate_https_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Update URLs must use HTTPS.")


async def fetch_manifest(manifest_url: str) -> dict[str, Any]:
    _validate_https_url(manifest_url)
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(manifest_url)
        response.raise_for_status()
        manifest = response.json()

    if not isinstance(manifest, dict):
        raise ValueError("Update manifest is not a JSON object.")

    version = str(manifest.get("version", "")).strip()
    package_url = str(manifest.get("package_url", "")).strip()
    sha256 = str(manifest.get("sha256", "")).strip().lower()
    notes = str(manifest.get("notes", "")).strip()

    if not version or not package_url:
        raise ValueError("Manifest must include version and package_url.")

    _validate_https_url(package_url)

    if sha256 and (len(sha256) != 64 or any(c not in "0123456789abcdef" for c in sha256)):
        raise ValueError("Manifest sha256 is invalid.")

    return {
        "version": version,
        "package_url": package_url,
        "sha256": sha256,
        "notes": notes,
    }


async def check_for_update() -> dict[str, Any]:
    settings = load_settings()
    manifest_url = settings.get("manifest_url", "")
    local = current_version()

    if not manifest_url:
        return {
            "configured": False,
            "current_version": local,
            "update_available": False,
            "manifest_url": "",
            "message": "No update feed is configured yet.",
        }

    manifest = await fetch_manifest(manifest_url)
    return {
        "configured": True,
        "current_version": local,
        "update_available": is_newer(manifest["version"], local),
        "manifest_url": manifest_url,
        "latest_version": manifest["version"],
        "notes": manifest["notes"],
        "package_url": manifest["package_url"],
        "sha256": manifest["sha256"],
    }


def _safe_extract(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    base = destination.resolve()

    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            member_path = (destination / member.filename).resolve()
            if base != member_path and base not in member_path.parents:
                raise ValueError(f"Unsafe path in update package: {member.filename}")
        archive.extractall(destination)


def _find_package_root(extracted: Path) -> Path:
    # If the ZIP contains a single wrapper directory, unwrap it.
    children = [p for p in extracted.iterdir() if p.name not in {"__MACOSX"}]
    if len(children) == 1 and children[0].is_dir():
        candidate = children[0]
        if (candidate / "main.py").exists():
            return candidate
    if (extracted / "main.py").exists():
        return extracted
    raise ValueError("Update package does not contain main.py at its root.")


def make_backup() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"before_update_{stamp}"
    backup.mkdir(parents=True, exist_ok=True)

    # Always copy persistent world data.
    if DATA_DIR.exists():
        shutil.copytree(DATA_DIR, backup / "data", dirs_exist_ok=True)

    # Create a lightweight source-code backup for rollback/debugging.
    code_zip = backup / "program_files.zip"
    with zipfile.ZipFile(code_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for path in PROJECT_ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(PROJECT_ROOT)
            if rel.parts and rel.parts[0] in {".venv", "data", "backups", "update_staging"}:
                continue
            z.write(path, rel)

    return backup


async def stage_update(manifest: dict[str, Any]) -> dict[str, str]:
    version = manifest["version"]
    package_url = manifest["package_url"]
    expected_sha = manifest.get("sha256", "")

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    work = STAGING_DIR / f"v_{version.replace('/', '_')}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    package_path = work / "update.zip"

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        async with client.stream("GET", package_url) as response:
            response.raise_for_status()
            with package_path.open("wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

    actual_sha = hashlib.sha256(package_path.read_bytes()).hexdigest()
    if expected_sha and actual_sha != expected_sha:
        raise ValueError(
            "Update checksum mismatch. Nothing was installed. "
            f"Expected {expected_sha}, received {actual_sha}."
        )

    extracted = work / "extracted"
    _safe_extract(package_path, extracted)
    package_root = _find_package_root(extracted)

    return {
        "staging_dir": str(package_root),
        "download_sha256": actual_sha,
    }
