#!/usr/bin/env python3
"""Measure layout problems of rendered Pharma Cards in Chromium.

Die Karte hat feste Maße (148×105 mm) und `overflow: hidden`. Zu langer Inhalt würde
deshalb stillschweigend abgeschnitten – bei medizinischen Karten ein Sicherheitsrisiko
(z. B. eine halb sichtbare „Cave“-Box). Dieses Skript misst je Kartenseite:

  - Überlauf: Inhaltsbereich (.body) oder eine Box ist höher als der verfügbare Platz
  - Sicherheitszone: Tabs, Titel, Badge, Boxen, ID, ©, QR liegen mindestens 5 mm
    innerhalb der Schnittkante (print-production/specs/bleed-and-safe-zone.md)

Ergebnis: docs/pharma-cards/reports/layout_review.md. Mit --strict Exit 1 bei Befunden.
Braucht Playwright + Chromium.

Usage:
    python3 scripts/pharma/check_layout.py [--cards DIR] [--strict]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cards  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

SAFE_MM = 5.0
TOL_MM = 0.3          # Messtoleranz (Rundung, Subpixel)
PX_PER_MM = 96 / 25.4

MEASURE_JS = """
(args) => {
  const [safeMm, tolMm, pxPerMm] = args;
  const card = document.querySelector('.card');
  const c = card.getBoundingClientRect();
  const res = {overflow: [], safe: []};
  const body = card.querySelector('.body');
  if (body && body.scrollHeight - body.clientHeight > tolMm * pxPerMm) {
    res.overflow.push({what: 'Inhaltsbereich', mm: (body.scrollHeight - body.clientHeight) / pxPerMm});
  }
  card.querySelectorAll('.box').forEach((b, i) => {
    const title = (b.querySelector('.box-title') || {}).textContent || ('Box ' + (i + 1));
    if (b.scrollHeight - b.clientHeight > tolMm * pxPerMm) {
      res.overflow.push({what: 'Box „' + title.trim() + '“', mm: (b.scrollHeight - b.clientHeight) / pxPerMm});
    }
    const r = b.getBoundingClientRect();
    if (r.bottom > c.bottom - safeMm * pxPerMm + tolMm * pxPerMm) {
      res.overflow.push({what: 'Box „' + title.trim() + '“ ragt in die Fußzone',
                         mm: (r.bottom - (c.bottom - safeMm * pxPerMm)) / pxPerMm});
    }
  });
  const sel = '.tab, .head .title, .head .subtitle, .badge, .box, .footer .cid, .footer .copy, .footer .qr, .front-center';
  card.querySelectorAll(sel).forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    const d = {
      links: (r.left - c.left) / pxPerMm, rechts: (c.right - r.right) / pxPerMm,
      oben: (r.top - c.top) / pxPerMm, unten: (c.bottom - r.bottom) / pxPerMm,
    };
    for (const [side, mm] of Object.entries(d)) {
      if (mm < safeMm - tolMm) {
        res.safe.push({what: el.className.split(' ')[0] || el.tagName, side, mm});
      }
    }
  });
  return res;
}
"""


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def measure(cards: list[dict], scope: dict, css: str) -> list[dict]:
    from playwright.sync_api import sync_playwright
    findings = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for card in cards:
            for side, inner in (("front", render_cards.front_inner(card, scope)),
                                ("back", render_cards.back_inner(card, scope))):
                page.set_content(render_cards.shell(card, scope, inner, css, side=side))
                r = page.evaluate(MEASURE_JS, [SAFE_MM, TOL_MM, PX_PER_MM])
                for o in r["overflow"]:
                    findings.append({"card_id": card["card_id"], "title": card.get("title"),
                                     "side": side, "kind": "Überlauf", "what": o["what"],
                                     "mm": round(o["mm"], 1)})
                seen = set()
                for s in r["safe"]:
                    key = (s["what"], s["side"])
                    if key in seen:
                        continue
                    seen.add(key)
                    findings.append({"card_id": card["card_id"], "title": card.get("title"),
                                     "side": side, "kind": "Sicherheitszone",
                                     "what": f"{s['what']} ({s['side']})",
                                     "mm": round(s["mm"], 1)})
        browser.close()
    return findings


def report(cards: list[dict], findings: list[dict]) -> str:
    affected = sorted({f["card_id"] for f in findings})
    over = [f for f in findings if f["kind"] == "Überlauf"]
    safe = [f for f in findings if f["kind"] == "Sicherheitszone"]
    lines = [
        "# Report — Layout-Prüfung (PH / Pharma Cards)",
        "",
        "> Automatisch erzeugt durch `scripts/pharma/check_layout.py` (`make ph-layout-check`).",
        "> Gemessen in Chromium am gerenderten Layout (DIN A6 quer, Sicherheitszone 5 mm).",
        "",
        f"- Kartenseiten geprüft: **{len(cards) * 2}** ({len(cards)} Karten)",
        f"- Karten mit Befund: **{len(affected)}**",
        f"- Überlauf-Befunde: **{len(over)}** · Sicherheitszonen-Befunde: **{len(safe)}**",
        "",
    ]
    if not findings:
        lines += ["Keine Befunde: Alle Inhalte passen auf die Karte und liegen in der Sicherheitszone.", ""]
        return "\n".join(lines)
    lines += [
        "**Überlauf** heißt: Text wird abgeschnitten. Die Karte muss gekürzt oder auf weniger Boxen "
        "verteilt werden. Sie darf so nicht gedruckt werden.",
        "",
        "| Karte | Titel | Seite | Art | Element | mm |",
        "|---|---|---|---|---|---:|",
    ]
    side_de = {"front": "Vorderseite", "back": "Rückseite"}
    for f in sorted(findings, key=lambda f: (f["kind"] != "Überlauf", f["card_id"], f["side"])):
        lines.append(f"| `{f['card_id']}` | {f['title']} | {side_de[f['side']]} | {f['kind']} | "
                     f"{f['what']} | {f['mm']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Layout der PH-Karten in Chromium prüfen.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--scope", default="cards/PH/scope")
    ap.add_argument("--css", default="card-system/templates/pharma/card.css")
    ap.add_argument("--out", default="docs/pharma-cards/reports/layout_review.md")
    ap.add_argument("--strict", action="store_true", help="Exit 1 bei Befunden")
    args = ap.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Playwright nicht verfügbar – Layout-Prüfung übersprungen.")
        return 0 if not args.strict else 1

    scope = render_cards.load_scope(Path(args.scope))
    css = Path(args.css).read_text(encoding="utf-8")
    cards = [load_yaml(p) for p in sorted(Path(args.cards).glob("*.yaml"))]
    findings = measure(cards, scope, css)
    Path(args.out).write_text(report(cards, findings), encoding="utf-8")

    affected = sorted({f["card_id"] for f in findings})
    print(f"{len(cards)} Karten geprüft, {len(findings)} Befunde in {len(affected)} Karten.")
    if affected:
        print("Betroffen: " + ", ".join(affected))
    print(f"Report: {args.out}")
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
