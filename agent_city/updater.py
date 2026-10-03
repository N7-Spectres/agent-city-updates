
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import time
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


def _github_contents_manifest_url(manifest_url: str) -> str | None:
    parsed = urllib.parse.urlsplit(manifest_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "raw.githubusercontent.com":
        return None

    parts = [urllib.parse.unquote(part) for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 4:
        return None

    owner, repo = parts[0], parts[1]
    if len(parts) >= 6 and parts[2:4] == ["refs", "heads"]:
        ref = parts[4]
        file_parts = parts[5:]
    else:
        ref = parts[2]
        file_parts = parts[3:]

    if not owner or not repo or not ref or not file_parts:
        return None

    encoded_owner = urllib.parse.quote(owner, safe="")
    encoded_repo = urllib.parse.quote(repo, safe="")
    encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in file_parts)
    query = urllib.parse.urlencode({"ref": ref})
    return (
        f"https://api.github.com/repos/{encoded_owner}/{encoded_repo}/"
        f"contents/{encoded_path}?{query}"
    )


async def fetch_manifest(manifest_url: str) -> dict[str, Any]:
    _validate_https_url(manifest_url)

    # Prefer GitHub's repository contents API for raw.githubusercontent.com
    # branch feeds. This resolves the requested branch/file from repository
    # state instead of relying on raw-CDN freshness.
    api_url = _github_contents_manifest_url(manifest_url)
    api_headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Agent-City-Updater",
        "Cache-Control": "no-cache, no-store, max-age=0",
        "Pragma": "no-cache",
    }

    # Keep the cache-busted raw request as a fallback for non-GitHub feeds and
    # for temporary GitHub API failures/rate limits.
    parsed = urllib.parse.urlsplit(manifest_url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("_agent_city_check", str(int(time.time() * 1000))))
    fresh_url = urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        urllib.parse.urlencode(query),
        parsed.fragment,
    ))
    fallback_headers = {
        "User-Agent": "Agent-City-Updater",
        "Cache-Control": "no-cache, no-store, max-age=0",
        "Pragma": "no-cache",
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = None
        if api_url:
            try:
                response = await client.get(api_url, headers=api_headers)
                response.raise_for_status()
            except httpx.HTTPError:
                response = None

        if response is None:
            response = await client.get(fresh_url, headers=fallback_headers)
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


def list_backups(limit: int = 30) -> list[dict[str, Any]]:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, Any]] = []

    for path in sorted(
        (p for p in BACKUP_DIR.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    ):
        info_path = path / "backup_info.json"
        info: dict[str, Any] = {}
        if info_path.exists():
            try:
                parsed = json.loads(info_path.read_text(encoding="utf-8"))
                if isinstance(parsed, dict):
                    info = parsed
            except Exception:
                info = {}

        total_size = 0
        file_count = 0
        try:
            for child in path.rglob("*"):
                if child.is_file():
                    file_count += 1
                    total_size += int(child.stat().st_size)
        except OSError:
            pass

        created_at = str(info.get("created_at") or "").strip()
        if not created_at:
            created_at = datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")

        items.append(
            {
                "name": path.name,
                "created_at": created_at,
                "version": str(info.get("version") or "unknown"),
                "kind": str(info.get("kind") or ("manual" if path.name.startswith("manual_") else "before_update")),
                "size_bytes": total_size,
                "file_count": file_count,
                "has_database": (path / "data" / "agent_city.db").exists(),
                "has_program_archive": (path / "program_files.zip").exists(),
            }
        )

        if len(items) >= max(1, min(int(limit), 100)):
            break

    return items


def make_backup(*, prefix: str = "before_update") -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    safe_prefix = "".join(
        ch for ch in str(prefix or "backup")
        if ch.isalnum() or ch in {"-", "_"}
    ).strip("-_") or "backup"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"{safe_prefix}_{stamp}"
    backup.mkdir(parents=True, exist_ok=True)

    # Copy persistent local data, then replace the primary SQLite file with an
    # online SQLite backup. This produces a transactionally consistent database
    # even while Agent City is still running.
    backup_data = backup / "data"
    if DATA_DIR.exists():
        shutil.copytree(DATA_DIR, backup_data, dirs_exist_ok=True)

    source_db = DATA_DIR / "agent_city.db"
    backup_db = backup_data / "agent_city.db"
    if source_db.exists():
        backup_data.mkdir(parents=True, exist_ok=True)
        if backup_db.exists():
            backup_db.unlink()
        with sqlite3.connect(source_db) as source_conn:
            with sqlite3.connect(backup_db) as backup_conn:
                source_conn.backup(backup_conn)

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

    (backup / "backup_info.json").write_text(
        json.dumps(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "version": current_version(),
                "kind": safe_prefix,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

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
