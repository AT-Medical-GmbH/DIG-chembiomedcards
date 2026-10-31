#!/usr/bin/env python3
"""Pflegt im Masterverzeichnis den Abschnitt „Produzierte Karten“ aus data/cards/*.yaml.

Nur der Bereich zwischen den Markern wird ersetzt; der übrige, von Hand gepflegte
Planungsteil von cards/registry/MASTER_DIRECTORY.md bleibt unverändert.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbm.model import ROOT, load_project  # noqa: E402

TARGET = ROOT / "cards" / "registry" / "MASTER_DIRECTORY.md"
START, END = "<!-- PRODUZIERTE-KARTEN:START -->", "<!-- PRODUZIERTE-KARTEN:END -->"


def main() -> int:
    project = load_project()
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in project.cards:
        groups[c.get("topic_group", "sonstige")].append(c)
    lines = [START, "", "## Produzierte Karten (automatisch aus `data/cards/`)", "",
             "_Erzeugt von `scripts/update_master_directory.py` – nicht von Hand bearbeiten. "
             "Quelle der Wahrheit sind die Kartendateien._", "",
             f"Stand: **{len(project.cards)} Karten**.", ""]
    for group, cards in groups.items():
        lines += [f"### {group}", "", "| ID | Slug / Dateiname | Titel | Tab | Review |", "|---|---|---|---|---|"]
        lines += [f"| `{c['card_id']}` | `{c['slug']}` | {c['title']} | {c['primary_category']} | {c['review_status']} |"
                  for c in sorted(cards, key=lambda c: c["card_id"])]
        lines.append("")
    lines.append(END)
    block = "\n".join(lines)
    text = TARGET.read_text(encoding="utf-8")
    if START in text:
        text = text[: text.index(START)] + block + text[text.index(END) + len(END):]
    else:
        text = text.rstrip("\n") + "\n\n---\n\n" + block + "\n"
    TARGET.write_text(text, encoding="utf-8")
    print(f"{TARGET.relative_to(ROOT)}: {len(project.cards)} Karten eingetragen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
