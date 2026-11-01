#!/usr/bin/env python3
"""Build a review packet (PDF) for the Fachreview of Pharma Cards (Modul PH).

Eine A4-Seite je offener Karte: Vorder- und Rückseite exakt wie für Lernende gerendert (mit
ENTWURF-Wasserzeichen), Status, Warnlevel, erforderliche Prüfart, die Prüfschwerpunkte aus
`review_focus` als Checkliste sowie Felder für Ergebnis, Quelle und Anmerkungen. Davor ein
Deckblatt mit Anleitung und ein Inhaltsverzeichnis, sortiert nach Prüfart.

Das Paket ist ein Arbeitsmittel. Verbindlich bleibt der Status in den Kartendaten; Freigaben werden
per Pull Request umgesetzt (docs/pharma-cards/review/README.md).

Usage:
    python3 scripts/pharma/review_packet.py [--out dist/review/Pharma_Cards_Review.pdf] [--html]
"""
from __future__ import annotations

import argparse
import math
import html
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cards  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

GROUPS = [
    ("toxicology_review_needed", "Toxikologische Prüfung", "reviewer_tox",
     "checkliste_toxikologie.md + checkliste_klinische_sicherheit.md"),
    ("clinical_review_needed", "Klinisch-pharmakologische Prüfung", "reviewer_pharm",
     "checkliste_pharmakologie.md + checkliste_klinische_sicherheit.md"),
    ("needs_review", "Allgemeines Fachreview", "reviewer_pharm", "checkliste_pharmakologie.md"),
    ("draft", "Entwurf (noch nicht reviewfähig)", "–", "–"),
    ("reviewed", "Geprüft – Freigabe ausstehend", "admin", "–"),
]
CLOSED = {"approved", "deprecated", "archived"}
WL_DE = {"low": "niedrig", "moderate": "mittel", "high": "hoch", "critical": "kritisch"}
SCALE = 0.86   # Kartenmaßstab auf der Prüfseite

PACKET_CSS = """
@page { size: A4; margin: 0; }
html, body { margin: 0; padding: 0; background: #fff; }
body { font-family: "Inter", "Segoe UI", Arial, sans-serif; color: #1c2529; }
.page { position: relative; width: 210mm; height: 297mm; padding: 11mm 14mm 10mm; box-sizing: border-box;
        break-after: page; overflow: hidden; }
.page:last-child { break-after: auto; }
.top { display: flex; justify-content: space-between; font-size: 8pt; color: #5b6b73;
       border-bottom: .3mm solid #dfe5e8; padding-bottom: 2mm; margin-bottom: 3mm; }
h1 { font-size: 20pt; margin: 0 0 2mm; } h2 { font-size: 13pt; margin: 5mm 0 2mm; }
.meta { display: flex; flex-wrap: wrap; gap: 1.5mm; margin-bottom: 3mm; }
.tag { font-size: 8pt; font-weight: 700; padding: .6mm 2mm; border-radius: 1mm; background: #eef1f3; }
.tag.critical { background: #fdecea; color: #b71c1c; } .tag.high { background: #fdf0ec; color: #c43d1f; }
.tag.moderate { background: #fff6e8; color: #8a5300; } .tag.low { background: #ecf6ee; color: #2e7d32; }
.cards { display: flex; flex-direction: column; align-items: center; gap: 3mm; }
.slot { position: relative; width: calc(148mm * %(s)s); height: calc(105mm * %(s)s);
        border: .2mm solid #cfd8dc; border-radius: 1mm; overflow: hidden; }
.slot .scaler { position: absolute; top: 0; left: 0; transform: scale(%(s)s); transform-origin: top left; }
.slot .label { position: absolute; right: 1.5mm; bottom: -0.2mm; font-size: 6.5pt; color: #90a4ae; }
.wm { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; pointer-events: none; }
.wm span { transform: rotate(-18deg); font: 800 8mm/1 Arial, sans-serif; color: rgba(200,0,0,.13);
           border: .7mm solid rgba(200,0,0,.13); padding: 1mm 3mm; white-space: nowrap; }
.focus { margin-top: 3mm; font-size: 9pt; }
.focus ul { list-style: none; margin: 1mm 0 0; padding: 0; }
.focus li { margin: .8mm 0; padding-left: 5.5mm; position: relative; }
.focus li::before { content: ""; position: absolute; left: 0; top: .6mm; width: 3mm; height: 3mm;
                    border: .3mm solid #37474f; border-radius: .4mm; }
.result { display: flex; gap: 5mm; font-size: 9pt; margin-top: 2mm; }
.res::before { content: "☐ "; }
.lines { margin-top: 2mm; font-size: 8.5pt; color: #5b6b73; }
.lines div { border-bottom: .2mm solid #b0bec5; height: 5.5mm; }
table { width: 100%%; border-collapse: collapse; font-size: 8.5pt; }
th, td { text-align: left; padding: 1mm 1.5mm; border-bottom: .2mm solid #dfe5e8; vertical-align: top; }
th { font-size: 7.5pt; text-transform: uppercase; color: #5b6b73; }
.cover p, .cover li { font-size: 10pt; line-height: 1.45; }
.note { background: #fff4e5; border: .3mm solid #f0b25a; border-radius: 1.5mm; padding: 2.5mm 3.5mm; font-size: 9.5pt; }
"""


def load(cards_dir: Path) -> list[dict]:
    out = []
    for p in sorted(cards_dir.glob("*.yaml")):
        with p.open(encoding="utf-8") as fh:
            out.append(yaml.safe_load(fh))
    return out


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


def ordered(cards: list[dict]) -> list[tuple[str, str, str, str, list[dict]]]:
    open_cards = [c for c in cards if c.get("review_status") not in CLOSED]
    groups = []
    for status, title, role, checklist in GROUPS:
        members = sorted((c for c in open_cards if c.get("review_status") == status),
                         key=lambda c: c["card_id"])
        if members:
            groups.append((status, title, role, checklist, members))
    return groups


def card_slot(card: dict, scope: dict, side: str) -> str:
    inner = (render_cards.front_inner(card, scope) if side == "front"
             else render_cards.back_inner(card, scope))
    label = "Vorderseite" if side == "front" else "Rückseite"
    return (f'<div class="slot"><div class="scaler">{render_cards.card_div(card, scope, inner, side)}</div>'
            f'<div class="wm"><span>ENTWURF – Fachreview</span></div><span class="label">{label}</span></div>')


def card_page(card: dict, scope: dict, group_title: str, role: str, checklist: str, page_no: int,
              total: int) -> str:
    wl = card.get("warning_level", "low")
    focus = card.get("review_focus") or ["Inhalt allgemein gegen aktuelle Quelle prüfen"]
    items = "".join(f"<li>{esc(f)}</li>" for f in focus)
    return f"""
<section class="page">
  <div class="top"><span>Pharma Cards · Fachreview · {esc(group_title)} ({esc(role)})</span>
    <span>{esc(card['card_id'])} · Seite {page_no}/{total}</span></div>
  <h1>{esc(card.get('title'))}</h1>
  <div class="meta">
    <span class="tag">{esc(card['card_id'])}</span>
    <span class="tag">{esc(card.get('card_type'))}</span>
    <span class="tag {esc(wl)}">Warnlevel {esc(WL_DE.get(wl, wl))}</span>
    <span class="tag">Status {esc(card.get('review_status'))}</span>
    <span class="tag">v{esc(card.get('version'))}</span>
    <span class="tag">Kategorie {esc(card.get('primary_category'))}</span>
  </div>
  <div class="cards">{card_slot(card, scope, 'front')}{card_slot(card, scope, 'back')}</div>
  <div class="focus"><strong>Prüfschwerpunkte</strong> <span style="color:#5b6b73">(Checkliste: {esc(checklist)})</span>
    <ul>{items}</ul></div>
  <div class="result"><strong>Ergebnis:</strong><span class="res">fachlich korrekt (reviewed)</span>
    <span class="res">Korrektur nötig</span><span class="res">grundsätzliche Bedenken</span></div>
  <div class="lines">Quelle (Titel, Herausgeber, Jahr): <div></div>Anmerkungen / Korrekturvorschlag: <div></div><div></div></div>
</section>"""


def cover(cards: list[dict], groups, page_map: dict[str, int], total: int) -> str:
    open_cards = [c for card_list in (g[4] for g in groups) for c in card_list]
    by_status = Counter(c.get("review_status") for c in open_cards)
    by_wl = Counter(c.get("warning_level") for c in open_cards)
    rows = []
    for _, title, role, _, members in groups:
        rows.append(f'<tr><th colspan="4" style="padding-top:3mm;color:#1c2529">{esc(title)} – '
                    f'{len(members)} Karten ({esc(role)})</th></tr>')
        for c in members:
            rows.append(f"<tr><td>{esc(c['card_id'])}</td><td>{esc(c.get('title'))}</td>"
                        f"<td>{esc(WL_DE.get(c.get('warning_level'), c.get('warning_level')))}</td>"
                        f"<td>S. {page_map[c['card_id']]}</td></tr>")
    stat = ", ".join(f"{k}: {v}" for k, v in sorted(by_status.items()))
    wls = ", ".join(f"{WL_DE.get(k, k)}: {by_wl[k]}" for k in ("critical", "high", "moderate", "low") if by_wl[k])
    return f"""
<section class="page cover">
  <div class="top"><span>Pharma Cards · Modul PH · AT Medical GmbH</span><span>Stand {date.today():%d.%m.%Y}</span></div>
  <h1>Review-Paket Pharma Cards</h1>
  <p><strong>{len(open_cards)} Karten</strong> warten auf das Fachreview ({stat}).<br>Warnlevel: {wls}.</p>
  <div class="note"><strong>Entwurf – Ausbildungsmaterial, keine Therapieanweisung.</strong> Keine Karte enthält
    Zahlendosen. Wo Dosierungen nötig sind, steht ein Dosierungsprinzip; konkrete Werte kommen nur mit Quelle
    und Review auf die Karte.</div>
  <h2>So läuft das Review</h2>
  <ol>
    <li>Pro Seite die Karte so lesen, wie Lernende sie sehen (Vorder- und Rückseite).</li>
    <li>Die <strong>Prüfschwerpunkte</strong> abhaken; sie nennen die Punkte, bei denen die Redaktion unsicher ist
      oder eine Quelle fehlt.</li>
    <li>Für <strong>kritische</strong> Karten (Antidote, Katecholamine, Antikoagulanzien) ist ein zweites
      Gegenlesen empfohlen.</li>
    <li>Ergebnis ankreuzen und eine Quelle mit Jahr notieren. Korrekturen direkt als Anmerkung.</li>
    <li>Rückgabe: dieses PDF mit Anmerkungen (oder Liste „Karten-ID → Ergebnis/Korrektur“). Die Redaktion setzt
      Korrekturen und Status per Pull Request um; erst danach sehen Lernende die Karte.</li>
  </ol>
  <p>Checklisten: <code>docs/pharma-cards/review/</code> im Repository DIG-chembiomedcards.
    Gesamt: {total} Seiten.</p>
  <h2>Inhalt</h2>
  <table><thead><tr><th>Karte</th><th>Titel</th><th>Warnlevel</th><th>Seite</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table>
</section>"""


def build(cards_dir: Path, scope_dir: Path, css_path: Path, cover_pages: int = 1) -> tuple[str, int]:
    scope = render_cards.load_scope(scope_dir)
    card_css = css_path.read_text(encoding="utf-8")
    cards = load(cards_dir)
    groups = ordered(cards)
    n_cards = sum(len(g[4]) for g in groups)
    total = cover_pages + n_cards
    page_map, pages, p = {}, [], cover_pages + 1
    for _, title, role, checklist, members in groups:
        for c in members:
            page_map[c["card_id"]] = p
            pages.append(card_page(c, scope, title, role, checklist, p, total))
            p += 1
    cover_html = cover(cards, groups, page_map, total)
    doc = ("<!doctype html><html lang=de><head><meta charset=utf-8><title>Pharma Cards Review-Paket</title>"
           f"<style>{card_css}{PACKET_CSS % {'s': SCALE}}"
           ".cover{height:auto;min-height:297mm;overflow:visible}</style></head><body>"
           + cover_html + "".join(pages) + "</body></html>")
    return doc, n_cards


# Druckbarer Bereich einer A4-Seite in CSS-Pixeln (96 dpi): 297 mm
A4_PX = 297 / 25.4 * 96


def cover_page_count(page) -> int:
    """Gemessene Seitenzahl des Deckblatts (Inhaltsverzeichnis kann umbrechen)."""
    h = page.evaluate("document.querySelector('.cover').scrollHeight")
    return max(1, math.ceil(h / A4_PX - 0.01))


def main() -> int:
    ap = argparse.ArgumentParser(description="Review-Paket (PDF) für das Fachreview erzeugen.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--scope", default="cards/PH/scope")
    ap.add_argument("--css", default="card-system/templates/pharma/card.css")
    ap.add_argument("--out", default="dist/review/Pharma_Cards_Review.pdf")
    ap.add_argument("--html", action="store_true", help="zusätzlich HTML schreiben")
    args = ap.parse_args()

    doc, n = build(Path(args.cards), Path(args.scope), Path(args.css))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.html:
        out.with_suffix(".html").write_text(doc, encoding="utf-8")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        out.with_suffix(".html").write_text(doc, encoding="utf-8")
        print(f"Playwright fehlt – HTML geschrieben: {out.with_suffix('.html')}")
        return 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.emulate_media(media="print")
        page.set_content(doc, wait_until="load")
        cp = cover_page_count(page)
        if cp != 1:  # Seitenzahlen mit gemessener Deckblattlänge neu setzen
            doc, n = build(Path(args.cards), Path(args.scope), Path(args.css), cover_pages=cp)
            page.set_content(doc, wait_until="load")
        page.pdf(path=str(out), prefer_css_page_size=True, print_background=True)
        browser.close()
    print(f"Review-Paket: {out} ({n} Karten, {out.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
