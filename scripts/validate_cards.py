#!/usr/bin/env python3
"""Validiert alle Kartendatensätze unter data/cards/ gegen Schema und Projektregeln.

Exit-Code 1 bei Fehlern. Warnungen (z. B. offener Review) brechen nicht ab.

    python3 scripts/validate_cards.py [--strict] [--filter bc_09]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbm.model import load_project  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="Warnungen als Fehler behandeln")
    ap.add_argument("--filter", help="nur card_ids mit diesem Präfix")
    args = ap.parse_args()

    project = load_project(args.filter)
    for issue in project.issues:
        print(f"{issue.level.upper():7} {issue.card_id}: {issue.message}")
    print(f"\n{len(project.cards)} Karten · {len(project.errors)} Fehler · {len(project.warnings)} Warnungen")
    failed = project.errors or (args.strict and project.warnings)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
