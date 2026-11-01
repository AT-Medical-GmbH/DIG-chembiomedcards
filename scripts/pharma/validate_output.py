#!/usr/bin/env python3
"""Validate generated Pharma Cards output + enforce export gating.

Prüft nach dem Rendern:
  - für jede Karte existieren Vorder- und Rückseiten-HTML
  - Export-Gating: Karten dürfen nur in Export-/Druckpakete, wenn der Review-Status
    zum Warnlevel passt (critical -> nur approved; moderate/high -> reviewed|approved).
    draft/needs_review/*_review_needed sind nie exportierbar.

Mit --require-exportable schlägt das Skript fehl, sobald eine Karte NICHT exportierbar
ist (für den finalen Release-Lauf). Ohne Flag ist nicht-exportierbar nur ein Hinweis
(normaler Entwicklungszustand, in dem Karten noch im Review sind).

Usage:
    python3 scripts/pharma/validate_output.py \
        --cards cards/PH/metadata --html exports/web/ph/html [--require-exportable]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

APPROVED_ONLY = {"critical"}
REVIEWED_OK = {"low", "moderate", "high"}
EXPORTABLE_STATUS = {"reviewed", "approved"}


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def is_exportable(card: dict) -> bool:
    wl = card.get("warning_level", "low")
    rs = card.get("review_status", "draft")
    if wl in APPROVED_ONLY:
        return rs == "approved"
    return rs in EXPORTABLE_STATUS


def main() -> int:
    ap = argparse.ArgumentParser(description="Generierte Ausgabe + Export-Gating prüfen.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--html", default="exports/web/ph/html")
    ap.add_argument("--require-exportable", action="store_true",
                    help="Fehler, wenn eine Karte nicht exportierbar ist (Release-Lauf).")
    args = ap.parse_args()

    html_dir = Path(args.html)
    files = sorted(Path(args.cards).glob("*.yaml"))
    if not files:
        print(f"Keine Karten in {args.cards}.")
        return 0

    errors, not_exportable = [], []
    for cf in files:
        card = load_yaml(cf)
        cid = card.get("card_id", cf.stem)
        for side in ("front", "back"):
            p = html_dir / f"{cid}_{side}.html"
            if not p.exists():
                errors.append(f"{cid}: fehlende Ausgabe {p.name} (render_cards.py ausführen)")
        if not is_exportable(card):
            not_exportable.append(
                f"{cid}: nicht exportierbar (warning_level={card.get('warning_level')}, "
                f"review_status={card.get('review_status')})")

    for m in not_exportable:
        level = "ERROR" if args.require_exportable else "INFO "
        print(f"{level} {m}")
    for e in errors:
        print(f"ERROR {e}")

    exportable = len(files) - len(not_exportable)
    print(f"\n{len(files)} Karten: {exportable} exportierbar, "
          f"{len(not_exportable)} im Review, {len(errors)} Ausgabefehler.")

    if errors or (args.require_exportable and not_exportable):
        return 1
    print("Output-Prüfung bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
