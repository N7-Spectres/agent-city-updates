from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    index = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    lab_html = (ROOT / "static" / "world3d" / "planet_lab.html").read_text(encoding="utf-8")
    lab_js = (ROOT / "static" / "world3d" / "planet_lab.js").read_text(encoding="utf-8")

    # Local app shell + mutable world assets must be explicitly non-cacheable
    # so an in-place update cannot strand the browser on old code.
    assert '@app.middleware("http")' in main_py
    assert "prevent_stale_local_ui_cache" in main_py
    assert 'path in {"/", "/planet-lab"}' in main_py
    assert 'path.startswith("/static/world3d/")' in main_py
    assert '"Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"' in main_py
    assert '"Pragma"] = "no-cache"' in main_py
    assert '"Expires"] = "0"' in main_py

    # One-time build keys break any already-populated pre-v1.1 cache.
    assert 'href="/static/styles.css?build=' in index
    assert 'src="/static/app.js?build=' in index
    assert 'const freshWorldSrc = "/planet-lab?embed=1&mode=local&build=' in index
    assert 'frame.src = freshWorldSrc;' in index
    assert 'href="/static/world3d/planet_lab.css?build=' in lab_html
    assert 'src="/static/world3d/planet_lab.js?build=' in lab_html

    # The legacy Home iframe contract remains present for older integration
    # checks and graceful no-JS fallback.
    assert 'src="/planet-lab?embed=1&mode=local"' in index

    # The loaded world now makes terrain/fallback state visible in the banner.
    assert '"Seeded terrain mesh • "' in lab_js
    assert '" surface loaded"' in lab_js
    assert '"Seeded terrain mesh • loading surface…"' in lab_js
    assert '"Local flat fallback • seeded terrain unavailable"' in lab_js

    # v1.1 terrain implementation itself remains intact.
    assert "function rebuildLocalTerrain(payload)" in lab_js
    assert '"/api/world/local-terrain?radius_m="' in lab_js
    assert "let localTerrainBuffer = null;" in lab_js

    # v1.1.2 keeps the cache-refresh contract while polishing the loaded mesh.
    assert "let localTerrainHighlightBuffer = null;" in lab_js
    assert "let localTerrainShadowBuffer = null;" in lab_js
    assert "const minorStride = 2;" in lab_js
    assert "const majorStride = 6;" in lab_js
    assert "function rebuildLocalLocationPads()" in lab_js

    print("Agent City v1.1.1 world cache-refresh smoke passed.")


if __name__ == "__main__":
    main()
