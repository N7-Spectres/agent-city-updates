from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    js = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")

    # Home and Citizen sheet must consume the same live energy/integrity source.
    assert "function citizenLiveVitalsMarkup" in js
    assert "citizenLiveVitalsMarkup(c, { compact: true })" in js
    assert "citizenLiveVitalsMarkup(citizen)" in js
    assert "normalizedVitalPercent(citizen?.energy)" in js
    assert "normalizedVitalPercent(citizen?.integrity)" in js

    # Long-term battery condition must stay distinct from current charge.
    assert "Long-term maintenance" in js
    assert "not current charge" in js

    # Home cards keep their existing compact geometry.
    assert ".compact-citizen-row {" in css
    compact_block = css[css.index(".compact-citizen-row {"):css.index(".compact-citizen-main {")]
    assert "padding: 10px 11px" in compact_block

    # Vitals use micro-bars, not full-size dashboard progress components.
    assert ".compact-vital {" in css
    track_block = css[css.index(".vital-meter-track {"):css.index(".vital-meter-track > i {")]
    assert "width: 30px" in track_block
    assert "height: 3px" in track_block
    assert ".sheet-live-vitals {" in css
    assert ".sheet-vital-track {" in css

    # Energy and integrity retain distinct visual channels.
    assert "background: var(--good)" in css
    assert ".vital-integrity .vital-meter-track > i" in css
    assert "background: var(--accent)" in css

    print("Agent City v0.8.2 synchronized compact vital-meter smoke passed.")


if __name__ == "__main__":
    main()
