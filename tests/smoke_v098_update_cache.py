from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    updater = (ROOT / "agent_city" / "updater.py").read_text(encoding="utf-8")

    assert "import time" in updater
    assert 'query.append(("_agent_city_check", str(int(time.time() * 1000))))' in updater
    assert "urllib.parse.urlsplit(manifest_url)" in updater
    assert "urllib.parse.urlunsplit" in updater
    assert '"Cache-Control": "no-cache, no-store, max-age=0"' in updater
    assert '"Pragma": "no-cache"' in updater
    assert "client.get(fresh_url, headers=headers)" in updater

    # The saved manifest URL remains the stable user setting; cache-busting is
    # applied only to the outbound request.
    assert 'settings.get("manifest_url", "")' in updater

    print("Agent City v0.9.8 update-cache smoke passed.")


if __name__ == "__main__":
    main()
