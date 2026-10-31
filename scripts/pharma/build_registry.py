#!/usr/bin/env python3
"""Update PH rows in cards.master.csv from cards/PH/metadata/*.yaml.

Erzeugt/aktualisiert ausschließlich die ph_*-Zeilen der Master-Registry aus den
PH-Kartendaten. Alle Nicht-PH-Zeilen (AC/OC/BC/MB/APC) bleiben unverändert erhalten.
Die CSV-Spalten entsprechen cards.master.schema.json (flache Registry-Felder).

Usage:
    python3 scripts/pharma/build_registry.py \
        --cards cards/PH/metadata --csv cards/registry/cards.master.csv [--check]

--check: schreibt nicht, sondern meldet nur, ob die CSV aktuell wäre (Exit 1 bei Drift).
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

FIELDS = ["card_id", "slug", "title", "module", "chapter", "card_type", "level",
          "front_asset", "back_asset", "qr_url", "lms_url",
          "print_status", "web_status", "review_status"]


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def row_from_card(card: dict) -> dict:
    return {
        "card_id": card.get("card_id", ""),
        "slug": card.get("slug", ""),
        "title": card.get("title", ""),
        "module": "PH",
        "chapter": card.get("chapter", ""),
        "card_type": card.get("card_type", ""),
        "level": card.get("level", ""),
        "front_asset": card.get("front_asset", ""),
        "back_asset": card.get("back_asset", ""),
        "qr_url": card.get("qr_url", ""),
        "lms_url": card.get("lms_url", ""),
        "print_status": card.get("print_status", "planned"),
        "web_status": card.get("web_status", "planned"),
        "review_status": card.get("review_status", "draft"),
    }


def build_csv_text(csv_path: Path, cards_dir: Path) -> str:
    existing = []
    if csv_path.exists():
        with csv_path.open(encoding="utf-8", newline="") as fh:
            existing = list(csv.DictReader(fh))
    non_ph = [r for r in existing if (r.get("module") or "").upper() != "PH"]

    ph_rows = [row_from_card(load_yaml(cf)) for cf in sorted(cards_dir.glob("*.yaml"))]
    ph_rows.sort(key=lambda r: r["card_id"])

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDS, quoting=csv.QUOTE_MINIMAL,
                            extrasaction="ignore")
    writer.writeheader()
    for r in non_ph:
        writer.writerow({k: r.get(k, "") for k in FIELDS})
    for r in ph_rows:
        writer.writerow(r)
    return buf.getvalue(), len(non_ph), len(ph_rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="PH-Zeilen der Master-Registry aktualisieren.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--csv", default="cards/registry/cards.master.csv")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    text, n_non_ph, n_ph = build_csv_text(csv_path, Path(args.cards))

    if args.check:
        current = csv_path.read_text(encoding="utf-8") if csv_path.exists() else ""
        if current.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
            print("DRIFT: cards.master.csv ist nicht aktuell (build_registry ausführen).")
            return 1
        print(f"OK: Registry aktuell ({n_non_ph} Nicht-PH, {n_ph} PH-Zeilen).")
        return 0

    csv_path.write_text(text, encoding="utf-8")
    print(f"Registry geschrieben: {n_non_ph} Nicht-PH-Zeilen erhalten, {n_ph} PH-Zeilen aktualisiert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
