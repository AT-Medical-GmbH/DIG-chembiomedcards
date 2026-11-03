#!/usr/bin/env python3
"""End-to-End-Smoke-Test der Pharma Cards Web-App im echten Browser (Chromium/Playwright).

Voraussetzung: laufende Instanz im lokalen Auth-Modus (AUTH_MODE=local) mit geseedeten Karten,
z. B.  PHARMA_FRONTEND_DIST=../frontend/build uvicorn app.main:app --port 8765

Prüft u. a.: Freigabe-Gating (Lernende sehen keine Entwürfe), Lernmodus mit Flip per Tastatur,
Bewertung und Fortschritt, Markierung, Notiz mit Autospeicherung, Suche, Review-Protokoll,
Antidot-Übersicht, Smartphone-Breite ohne horizontales Scrollen, keine Konsolenfehler.

Usage:  python3 online-platform/e2e/smoke.py [--url http://127.0.0.1:8765] [--shots DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

REVIEWER = "reviewer-tox@example.org"
results: list[tuple[str, bool, str]] = []


def api_get(base: str, path: str) -> dict:
    """Erwartungswerte aus der API statt fester Zahlen: der Test bleibt bei wiederholten Läufen
    gegen dieselbe Datenbank gültig."""
    req = urllib.request.Request(base + path, headers={"X-User": REVIEWER, "X-Role": "reviewer_tox"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)


def check(name: str, fn) -> None:
    try:
        fn()
        results.append((name, True, ""))
    except Exception as exc:  # noqa: BLE001 – Testreport sammelt alle Fehler
        results.append((name, False, str(exc).splitlines()[0][:200]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--shots", default=None, help="Verzeichnis für Screenshots")
    args = ap.parse_args()
    base = args.url.rstrip("/")
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)

    def shot(page, name):
        if shots:
            page.screenshot(path=str(shots / f"{name}.png"), full_page=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="de-DE")
        page = ctx.new_page()
        console_errors: list[str] = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        # 1) Lernende: keine Entwürfe sichtbar
        def learner_gating():
            page.goto(base + "/")
            expect(page.get_by_role("heading", name="Noch keine freigegebenen Karten")).to_be_visible()
            page.goto(base + "/karten")
            expect(page.get_by_text("0 Karte(n)")).to_be_visible()
            shot(page, "01_lernende_keine_entwuerfe")
        check("Lernende sehen keine ungeprüften Karten", learner_gating)

        # 2) Reviewerin: Übersicht mit Lernsets
        def reviewer_dashboard():
            page.evaluate(f"localStorage.setItem('pc_dev_user', '{REVIEWER}')")
            page.goto(base + "/")
            expect(page.get_by_role("heading", name="Lernen starten")).to_be_visible()
            total = api_get(base, "/api/learn/queue?set=antidote&limit=1")["total"]
            expect(page.locator("a.tile", has_text="Antidote trainieren")).to_contain_text(str(total))
            shot(page, "02_uebersicht")
        check("Übersicht mit Lernsets (Reviewer-Rolle)", reviewer_dashboard)

        # 3) Lernmodus: Flip, Bewertung, Fortschritt
        def learn_flow():
            total = api_get(base, "/api/learn/queue?set=antidote&limit=1")["total"]
            assert total >= 2, f"zu wenige offene Antidotkarten für den Test ({total})"
            n = min(total, 50)
            page.goto(base + "/lernen?set=antidote")
            expect(page.get_by_text(f"Karte 1 von {n}")).to_be_visible()
            expect(page.get_by_text("Entwurf:")).to_be_visible()
            page.wait_for_timeout(600)
            shot(page, "03_lernen_vorderseite")
            page.locator("body").press("Space")
            expect(page.get_by_role("button", name="Gelernt")).to_be_visible()
            page.wait_for_timeout(600)
            shot(page, "04_lernen_rueckseite")
            page.locator("body").press("3")
            expect(page.get_by_text(f"Karte 2 von {n}")).to_be_visible()
        check("Lernmodus: Leertaste dreht, Taste 3 bewertet, nächste Karte", learn_flow)

        # 4) Markierung + Notiz mit Autospeicherung
        def flag_and_note():
            fav = page.get_by_role("button", name="Favorit")
            fav.click()
            expect(fav).to_have_attribute("aria-pressed", "true")
            page.locator("body").press("n")
            page.get_by_label("Notiz zu dieser Karte").fill("Wirkdauer kürzer als Opioid – nachbeobachten.")
            expect(page.get_by_text("gespeichert", exact=False)).to_be_visible(timeout=5000)
        check("Markierung setzen und Notiz automatisch speichern", flag_and_note)

        # 5) Suche und Kartendetail mit Review-Protokoll
        def search_and_review():
            page.goto(base + "/karten")
            page.get_by_placeholder("Suche", exact=False).fill("naloxon")
            row = page.locator("li.row", has_text="Naloxon").first
            expect(row).to_be_visible()
            row.locator("a").click()
            expect(page.get_by_role("heading", name="Naloxon", exact=True)).to_be_visible()
            page.get_by_label("Prüfart").select_option("toxicology")
            marker = f"E2E-Test {int(time.time())}: Wirkprinzip geprüft"
            page.get_by_label("Anmerkungen / Quelle").fill(marker)
            page.get_by_role("button", name="Prüfung protokollieren").click()
            expect(page.get_by_text("Protokolliert.", exact=False)).to_be_visible()
            expect(page.get_by_text(marker)).to_be_visible()
            shot(page, "05_karte_review")
        check("Suche, Kartendetail, Review-Protokoll", search_and_review)

        # 6) Antidot-Schnellübersicht
        def antidote_table():
            page.goto(base + "/antidote")
            expect(page.locator("table").first.locator("tbody tr")).to_have_count(13)
            shot(page, "06_antidote")
        check("Antidot-Übersicht mit 13 Antidoten", antidote_table)

        # 7) Smartphone-Breite
        def mobile():
            m = browser.new_context(viewport={"width": 390, "height": 844}, locale="de-DE",
                                    is_mobile=True, has_touch=True)
            mp = m.new_page()
            mp.goto(base + "/")
            mp.evaluate(f"localStorage.setItem('pc_dev_user', '{REVIEWER}')")
            mp.goto(base + "/lernen?set=toxidrome")
            expect(mp.get_by_text("Karte 1 von", exact=False)).to_be_visible()
            mp.wait_for_timeout(600)
            overflow = mp.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            assert overflow <= 0, f"horizontales Scrollen: {overflow}px"
            shot(mp, "07_mobil_lernen")
            m.close()
        check("Smartphone 390 px: Lernmodus ohne horizontales Scrollen", mobile)

        check("Keine Konsolenfehler", lambda: (_ for _ in ()).throw(AssertionError("; ".join(console_errors)))
              if console_errors else None)
        browser.close()

    width = max(len(n) for n, _, _ in results)
    for name, ok, msg in results:
        print(f"{'OK  ' if ok else 'FAIL'} {name.ljust(width)} {msg}")
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} Prüfungen bestanden.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
