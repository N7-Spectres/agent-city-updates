from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_city.updater import _github_contents_manifest_url


def main() -> None:
    updater = (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")

    normal = _github_contents_manifest_url(
        "https://raw.githubusercontent.com/N7-Spectres/agent-city-updates/main/update.json"
    )
    assert normal == (
        "https://api.github.com/repos/N7-Spectres/agent-city-updates/"
        "contents/update.json?ref=main"
    )

    explicit_ref = _github_contents_manifest_url(
        "https://raw.githubusercontent.com/N7-Spectres/agent-city-updates/"
        "refs/heads/main/update.json"
    )
    assert explicit_ref == normal

    assert _github_contents_manifest_url("https://example.com/update.json") is None

    # GitHub raw branch feeds prefer repository state via the contents API.
    assert '"Accept": "application/vnd.github.raw+json"' in updater
    assert '"X-GitHub-Api-Version": "2022-11-28"' in updater
    assert '"User-Agent": "Agent-City-Updater"' in updater
    assert "client.get(api_url, headers=api_headers)" in updater

    # A GitHub API outage/rate limit must not strand users.
    assert "except httpx.HTTPError:" in updater
    assert "client.get(fresh_url, headers=fallback_headers)" in updater

    # Feed settings remain the stable user-facing URL.
    assert 'settings.get("manifest_url", "")' in updater

    print("Agent City v0.9.11 GitHub update-feed smoke passed.")


if __name__ == "__main__":
    main()
