#!/usr/bin/env python3
"""Erzeugt reports/cards_review_needed.md aus den Kartendaten.

Listet jede Karte, die nicht `approved` ist, mit ihren Review-Hinweisen – die
Arbeitsliste für den Fachreview (docs/concept/14-quality-assurance.md).
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbm.model import ROOT, load_project  # noqa: E402


def main() -> int:
    project = load_project()
    status = Counter(c["review_status"] for c in project.cards)
    open_cards = [c for c in project.cards if c["review_status"] != "approved"]
    lines = [
        "# Karten mit offenem Fachreview",
        "",
        "_Automatisch erzeugt von `scripts/report_review_status.py` – Änderungen bitte in "
        "`data/cards/<card_id>.yaml` vornehmen, nicht hier._",
        "",
        "Statusübersicht: " + " · ".join(f"**{k}**: {v}" for k, v in sorted(status.items())),
        "",
        "Freigabe einer Karte: Inhalte prüfen, ggf. korrigieren, `references` und `reviewer` "
        "eintragen, `review_status: approved` setzen, `version` erhöhen, `make build`.",
        "",
    ]
    for c in open_cards:
        prov = " · ID vorläufig" if c.get("id_status") == "provisional" else ""
        lines += [f"## `{c['card_id']}` {c['title']} — {c['review_status']}{prov}", ""]
        lines += [f"- {n}" for n in c.get("review_notes") or ["(keine Hinweise)"]]
        lines += [f"- Vorschau: [`generated/preview/{c['card_id']}.png`](../generated/preview/{c['card_id']}.png)", ""]
    out = ROOT / "reports" / "cards_review_needed.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(open_cards)} Karten offen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
