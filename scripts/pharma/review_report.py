#!/usr/bin/env python3
"""Generate docs/pharma-cards/reports/cards_review_needed.md from PH card data.

Listet alle PH-Karten, die noch nicht freigegeben sind, gruppiert nach benötigter
Prüfung (Pharmakologie / Toxikologie / allgemein), jeweils mit Warnlevel und den
konkreten Prüfschwerpunkten aus `review_focus`. Grundlage für die Fachreviewer.

Usage:
    python3 scripts/pharma/review_report.py \
        --cards cards/PH/metadata --out docs/pharma-cards/reports/cards_review_needed.md
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

GROUPS = [
    ("toxicology_review_needed", "Toxikologische Prüfung nötig (`reviewer_tox`)"),
    ("clinical_review_needed", "Klinisch-pharmakologische Prüfung nötig (`reviewer_pharm`)"),
    ("needs_review", "Allgemeines Fachreview nötig (`reviewer_pharm`)"),
    ("draft", "Entwurf (noch nicht reviewfähig)"),
    ("reviewed", "Geprüft, Freigabe ausstehend (`admin`)"),
]
WL_ORDER = {"critical": 0, "high": 1, "moderate": 2, "low": 3}


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def build(cards: list[dict]) -> str:
    open_cards = [c for c in cards if c.get("review_status") not in {"approved", "deprecated", "archived"}]
    status_count = Counter(c.get("review_status") for c in cards)
    wl_count = Counter(c.get("warning_level") for c in open_cards)

    lines = [
        "# Report — Karten mit offenem Review (PH / Pharma Cards)",
        "",
        "> Automatisch erzeugt durch `scripts/pharma/review_report.py` (`make ph-review-report`).",
        "> Nicht von Hand bearbeiten; Änderungen in den Kartendaten vornehmen.",
        "",
        "## Übersicht",
        "",
        f"- Karten gesamt: **{len(cards)}**",
        f"- davon offen (nicht `approved`): **{len(open_cards)}**",
        "- nach Review-Status: " + ", ".join(f"`{k}` {v}" for k, v in sorted(status_count.items())),
        "- offene nach Warnlevel: " + ", ".join(
            f"`{k}` {wl_count[k]}" for k in sorted(wl_count, key=lambda k: WL_ORDER.get(k, 9))),
        "",
        "Prüfablauf und Checklisten: `docs/pharma-cards/review/`.",
        "",
    ]

    for status, heading in GROUPS:
        group = [c for c in open_cards if c.get("review_status") == status]
        if not group:
            continue
        group.sort(key=lambda c: (WL_ORDER.get(c.get("warning_level"), 9), c.get("card_id", "")))
        lines += [f"## {heading} — {len(group)}", "",
                  "| Karte | Titel | Typ | Warnlevel | Prüfschwerpunkte |",
                  "|---|---|---|---|---|"]
        for c in group:
            focus = c.get("review_focus") or []
            focus_txt = "<br>".join(f"• {f}" for f in focus) if focus else "–"
            lines.append(
                f"| `{c.get('card_id')}` | {c.get('title')} | {c.get('card_type')} | "
                f"{c.get('warning_level')} | {focus_txt} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Review-Report für PH-Karten erzeugen.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--out", default="docs/pharma-cards/reports/cards_review_needed.md")
    args = ap.parse_args()

    cards = [load_yaml(p) for p in sorted(Path(args.cards).glob("*.yaml"))]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(cards), encoding="utf-8")
    print(f"Review-Report geschrieben: {out} ({len(cards)} Karten)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
