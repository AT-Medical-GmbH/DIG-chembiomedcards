#!/usr/bin/env python3
"""Build Moodle import packages for Pharma Cards (Modul PH).

Je Paket aus cards/PH/scope/packages.yaml entsteht ein Verzeichnis + ZIP mit
mehreren robusten Importvarianten, weil Moodle-Flashcard-Plugins unterschiedliche
Formate erwarten (siehe docs/pharma-cards/07_moodle-integration.md):

    images/                           Front-/Back-PNG (wenn Playwright verfügbar)
    import.csv                        alle Metadaten, Bildverweise (UTF-8, Komma)
    import_html.csv                   wie import.csv, Front/Back als HTML-Fragment
    DIRECT_IMPORT_TAB_CRLF.txt        Front<TAB>Back, CRLF (Flashcard-/Anki-artig)
    DIRECT_IMPORT_SEMICOLON_CRLF.txt  Front;Back, CRLF, UTF-8 mit BOM (DE-Excel)
    manifest.json                     Paketbeschreibung, Kartenliste, SHA-256
    README_IMPORT.md                  Anleitung und Annahmen

Export-Gating: Standardmäßig werden NUR exportierbare Karten aufgenommen
(validate_output.is_exportable). Mit --preview werden auch Karten im Review
aufgenommen; die Ausgabe landet dann getrennt unter exports/preview/moodle/ und
trägt im Namen und auf jeder Karte den Vermerk VORSCHAU / ENTWURF.

Usage:
    python3 scripts/pharma/generate_moodle_import.py [--preview] [--no-images]
        [--packages slug1,slug2] [--out exports/moodle/ph] [--dist dist]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cards  # noqa: E402  (gemeinsames Rendering)
from validate_output import is_exportable  # noqa: E402  (eine Gating-Regel)

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

FIELDS = ["title", "category", "card_id", "front_image", "back_image", "front_html",
          "back_html", "tags", "difficulty", "primary_category", "secondary_categories",
          "warning_level", "review_status"]
DISCLAIMER = "Ausbildungs- und Lernmaterial – keine Therapieanweisung."
PREVIEW_NOTE = "ENTWURF – fachlich noch nicht freigegeben"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)  # deterministische ZIPs


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_packages(scope_dir: Path) -> list[dict]:
    return (load_yaml(scope_dir / "packages.yaml") or {}).get("packages", [])


def in_package(card: dict, pkg: dict) -> bool:
    cats = set(pkg.get("categories", []))
    if "*" in cats:
        return True
    card_cats = {card.get("primary_category")} | set(card.get("secondary_categories") or [])
    return bool(cats & card_cats)


def one_line(text: str) -> str:
    """Für TAB/Semikolon-Formate: keine Zeilenumbrüche/Tabs im Feld."""
    return re.sub(r"[\t\r\n]+", " ", text).strip()


def front_fragment(card: dict, preview: bool) -> str:
    fc = card.get("front_content") or {}
    prompt = fc.get("prompt") or fc.get("question") or card.get("title", "")
    parts = [f"<h3>{html.escape(card.get('title', ''))}</h3>"]
    if prompt and prompt != card.get("title"):
        parts.append(f"<p>{html.escape(prompt)}</p>")
    if preview:
        parts.append(f"<p><em>{PREVIEW_NOTE}</em></p>")
    return "".join(parts)


def back_fragment(card: dict, preview: bool) -> str:
    parts = [f"<h3>{html.escape(card.get('title', ''))}</h3>"]
    for sec in card.get("back_sections") or []:
        label = html.escape(sec.get("label") or sec.get("key", ""))
        body = render_cards.render_inline(sec.get("text") or sec.get("content") or "")
        parts.append(f"<h4>{label}</h4><p>{body}</p>")
    wl = card.get("warning_level")
    if wl in {"high", "critical"}:
        parts.append(f"<p><strong>Warnlevel: {html.escape(wl)}</strong></p>")
    if preview:
        parts.append(f"<p><em>{PREVIEW_NOTE}</em></p>")
    parts.append(f"<p><small>{DISCLAIMER} {html.escape(card.get('card_id', ''))}</small></p>")
    return "".join(parts)


def render_images(cards: list[dict], scope: dict, css: str, img_dir: Path) -> int:
    """Rendert Front/Back-PNG je Karte über Chromium. Gibt Anzahl Dateien zurück."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("  [i] Playwright nicht verfügbar – Pakete ohne Bilder (HTML-Varianten nutzen).")
        return 0
    img_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=3)
        for card in cards:
            for side, inner in (("front", render_cards.front_inner(card, scope)),
                                ("back", render_cards.back_inner(card, scope))):
                page.set_content(render_cards.shell(card, scope, inner, css, side=side))
                page.query_selector(".card").screenshot(
                    path=str(img_dir / f"{card['card_id']}_{side}.png"))
                n += 1
        browser.close()
    return n


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_zip(src_dir: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(p for p in src_dir.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(str(Path(src_dir.name) / f.relative_to(src_dir)), FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, f.read_bytes())


README_TMPL = """# Pharma Cards – Moodle-Import: {name}{suffix}

{status_line}

**Karten:** {count} · **Quelle:** DIG-chembiomedcards, Modul PH · **Stand:** {stand}

## Dateien

| Datei | Format | Wofür |
|---|---|---|
| `import.csv` | UTF-8, Komma, alle Felder in Anführungszeichen, CRLF | vollständige Metadaten, Bilder als Verweis |
| `import_html.csv` | wie oben | Front/Back als HTML-Fragment (ohne Bilder nutzbar) |
| `DIRECT_IMPORT_TAB_CRLF.txt` | Front⇥Back, CRLF, UTF-8 | Flashcard-/Karteikarten-Plugins mit Zwei-Spalten-Import |
| `DIRECT_IMPORT_SEMICOLON_CRLF.txt` | Front;Back, CRLF, UTF-8 mit BOM | Bearbeitung in deutschem Excel, Plugins mit Semikolon-Import |
| `images/` | PNG, Vorder- und Rückseite je Karte | Bildbasierte Karten; mit den CSV-Spalten `front_image`/`back_image` verknüpft |
| `manifest.json` | JSON | Kartenliste, Versionen, Review-Status, SHA-256 aller Dateien |

## Annahmen

- Das konkrete Moodle-Flashcard-Plugin ist noch nicht festgelegt. Deshalb liegen mehrere
  Varianten bei. Die Zwei-Spalten-Formate (TAB/Semikolon) passen zu den meisten Karteikarten-Importen.
  `import.csv` dient als vollständige Datenquelle für eigene Importskripte.
- Bilder werden je nach Plugin entweder hochgeladen und über den Dateinamen referenziert oder
  im HTML-Fragment eingebettet. Die Dateinamen sind stabil: `<card_id>_front.png`, `<card_id>_back.png`.
- Langfristig ist die Live-Integration per **LTI 1.3** vorgesehen
  (`docs/pharma-cards/07_moodle-integration.md`). Diese Pakete sind die statische Stufe A.

## Import (Kurzanleitung)

1. Im Kurs die Karteikarten-Aktivität anlegen bzw. öffnen.
2. Importfunktion wählen und `DIRECT_IMPORT_TAB_CRLF.txt` hochladen (Trennzeichen: Tabulator).
3. Bei bildbasierten Karten vorher den Ordner `images/` in die Aktivität bzw. den Kursdateibereich
   hochladen.
4. Stichprobe prüfen: Umlaute, Listen, Warnlevel-Hinweis auf der Rückseite.

## Hinweis

{disclaimer}
Jede Karte trägt einen Review-Status. Freigegebene Pakete enthalten nur geprüfte Karten
(`approved`, bzw. `reviewed` bei Warnlevel unter `critical`).
"""


def build_package(pkg: dict, cards: list[dict], scope: dict, css: str, out_root: Path,
                  dist: Path, preview: bool, images: bool) -> dict:
    suffix = "_VORSCHAU" if preview else ""
    pkg_dir = out_root / f"Pharma_Cards_Moodle_{pkg['label']}{suffix}"
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True)

    n_img = render_images(cards, scope, css, pkg_dir / "images") if images else 0
    has_img = n_img > 0

    rows, rows_html, two_col = [], [], []
    for c in cards:
        cid = c["card_id"]
        fimg = f"images/{cid}_front.png" if has_img else ""
        bimg = f"images/{cid}_back.png" if has_img else ""
        ff, bf = front_fragment(c, preview), back_fragment(c, preview)
        base = {
            "title": c.get("title", ""), "category": pkg["name"], "card_id": cid,
            "front_image": fimg, "back_image": bimg,
            "tags": ",".join(c.get("tags") or []), "difficulty": c.get("difficulty", ""),
            "primary_category": c.get("primary_category", ""),
            "secondary_categories": ",".join(c.get("secondary_categories") or []),
            "warning_level": c.get("warning_level", ""), "review_status": c.get("review_status", ""),
        }
        img_front = f'<img src="{fimg}" alt="{html.escape(c.get("title", ""))} – Vorderseite">' if has_img else ff
        img_back = f'<img src="{bimg}" alt="{html.escape(c.get("title", ""))} – Rückseite">' if has_img else bf
        rows.append({**base, "front_html": img_front, "back_html": img_back})
        rows_html.append({**base, "front_html": ff, "back_html": bf})
        two_col.append((one_line(ff), one_line(bf)))

    write_csv(pkg_dir / "import.csv", rows, FIELDS)
    write_csv(pkg_dir / "import_html.csv", rows_html, FIELDS)
    (pkg_dir / "DIRECT_IMPORT_TAB_CRLF.txt").write_bytes(
        "".join(f"{f}\t{b}\r\n" for f, b in two_col).encode("utf-8"))
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    for f, b in two_col:
        w.writerow([f, b])
    (pkg_dir / "DIRECT_IMPORT_SEMICOLON_CRLF.txt").write_bytes(
        b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8"))

    stand = max((str(c.get("updated_at", "")) for c in cards), default="")
    status_line = (f"> **VORSCHAU – {PREVIEW_NOTE}.** Nicht in Kurse für Lernende einspielen."
                   if preview else "> Freigegebenes Paket (nur geprüfte Karten).")
    (pkg_dir / "README_IMPORT.md").write_text(README_TMPL.format(
        name=pkg["name"], suffix=" (Vorschau)" if preview else "", status_line=status_line,
        count=len(cards), stand=stand, disclaimer=DISCLAIMER), encoding="utf-8")

    files = sorted(p for p in pkg_dir.rglob("*") if p.is_file())
    manifest = {
        "package": pkg["slug"], "name": pkg["name"], "label": pkg["label"],
        "kind": "moodle", "preview": preview, "stand": stand, "card_count": len(cards),
        "cards": [{"card_id": c["card_id"], "title": c.get("title"), "version": c.get("version"),
                   "review_status": c.get("review_status"),
                   "warning_level": c.get("warning_level")} for c in cards],
        "files": {str(f.relative_to(pkg_dir)): sha256(f) for f in files},
    }
    (pkg_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    zip_path = dist / f"{pkg_dir.name}.zip"
    write_zip(pkg_dir, zip_path)
    return {"package": pkg["slug"], "cards": len(cards), "images": n_img, "zip": str(zip_path)}


def select_cards(all_cards: list[dict], preview: bool) -> list[dict]:
    if preview:
        return [c for c in all_cards if c.get("review_status") not in {"deprecated", "archived"}]
    return [c for c in all_cards if is_exportable(c)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Moodle-Importpakete für PH erzeugen.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--scope", default="cards/PH/scope")
    ap.add_argument("--css", default="card-system/templates/pharma/card.css")
    ap.add_argument("--out", default=None, help="Default: exports/moodle/ph bzw. exports/preview/moodle")
    ap.add_argument("--dist", default=None, help="Default: dist/moodle bzw. dist/preview/moodle")
    ap.add_argument("--packages", default="", help="Kommagetrennte Paket-Slugs (Default: alle)")
    ap.add_argument("--preview", action="store_true",
                    help="Auch Karten im Review aufnehmen (getrennt, als VORSCHAU markiert)")
    ap.add_argument("--no-images", action="store_true", help="Keine PNG rendern")
    args = ap.parse_args()

    out = Path(args.out or ("exports/preview/moodle" if args.preview else "exports/moodle/ph"))
    dist = Path(args.dist or ("dist/preview/moodle" if args.preview else "dist/moodle"))
    scope = render_cards.load_scope(Path(args.scope))
    css = Path(args.css).read_text(encoding="utf-8")
    all_cards = [load_yaml(p) for p in sorted(Path(args.cards).glob("*.yaml"))]
    cards = select_cards(all_cards, args.preview)
    wanted = {s for s in args.packages.split(",") if s}

    print(f"{len(all_cards)} Karten gesamt, {len(cards)} für den Export "
          f"({'VORSCHAU' if args.preview else 'nur freigegeben'}).")
    results, skipped = [], []
    for pkg in load_packages(Path(args.scope)):
        if wanted and pkg["slug"] not in wanted:
            continue
        pkg_cards = [c for c in cards if in_package(c, pkg)]
        if not pkg_cards:
            skipped.append(pkg["slug"])
            continue
        r = build_package(pkg, pkg_cards, scope, css, out, dist, args.preview, not args.no_images)
        results.append(r)
        print(f"OK  {pkg['slug']}: {r['cards']} Karten, {r['images']} Bilder -> {r['zip']}")
    if skipped:
        print(f"--  ohne exportierbare Karten übersprungen: {', '.join(skipped)}")
    print(f"\n{len(results)} Pakete erzeugt, {len(skipped)} übersprungen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
