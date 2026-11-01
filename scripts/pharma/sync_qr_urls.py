#!/usr/bin/env python3
"""Setzt wirkstoff_slug/begriff_slug (falls fehlend) und erzeugt qr_url daraus.

Ein vorhandenes Slug-Feld wird nie überschrieben (das Linkregister kann abweichen).
Zeilenbasiert, damit Kommentare und Reihenfolge in den YAML-Dateien erhalten bleiben.

Usage:
    python3 scripts/pharma/sync_qr_urls.py [--cards DIR] [--check]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiki_links  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def sync_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    card = yaml.safe_load(text)
    field = wiki_links.slug_field(card)
    new = text
    if not card.get(field):
        card[field] = wiki_links.expected_slug(card)
        new = re.sub(r"^(slug: .*)$", rf"\1\n{field}: {card[field]}", new, count=1, flags=re.M)
    url = wiki_links.wiki_url(card)
    new = re.sub(r"^qr_url: .*$", f"qr_url: {url}", new, count=1, flags=re.M)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cards", type=Path, default=ROOT / "cards/PH/metadata")
    ap.add_argument("--check", action="store_true", help="nur prüfen, nichts schreiben")
    args = ap.parse_args()
    files = sorted(args.cards.glob("*.yaml"))
    if args.check:
        bad = []
        for f in files:
            card = yaml.safe_load(f.read_text(encoding="utf-8"))
            bad += wiki_links.check(card)[0]
        print("\n".join(bad) or f"{len(files)} Karten: qr_url konsistent.")
        return 1 if bad else 0
    changed = [f.name for f in files if sync_file(f)]
    print(f"{len(changed)} von {len(files)} Karten aktualisiert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
