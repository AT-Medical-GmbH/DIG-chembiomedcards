#!/usr/bin/env python3
"""Build print packages for Pharma Cards (Modul PH): sheets, single-card PDFs, PNGs.

Je Paket aus cards/PH/scope/packages.yaml entsteht ein Druckpaket (Verzeichnis + ZIP):

    Pharma_Cards_<label>_A4_2up_Schnittmarken.pdf   100 %, Beschnitt 3 mm, Schnittmarken
    Pharma_Cards_<label>_A4_2up_ohne_Marken.pdf     100 %, für Büro-/Digitaldruck
    Pharma_Cards_<label>_A4_4up_Schnittmarken.pdf   verkleinert (Maßstab im README)
    Pharma_Cards_<label>_A4_8up_kompakt.pdf         stark verkleinert, Wiederholungsdruck
    Pharma_Cards_<label>_A3_8up_Schnittmarken.pdf   A3, verkleinert
    einzelkarten/<card_id>.pdf                       Vorder- + Rückseite, 148×105 mm
    png/<card_id>_front.png, _back.png               Einzelbilder
    README_PRINT.md, manifest.json

Bögen sind duplexfähig: Auf jeden Vorderseitenbogen folgt der Rückseitenbogen mit
gespiegelter Anordnung, sodass Vorder- und Rückseite beim Wenden passen (Standard:
Wenden an der langen Kante, --flip short für kurze Kante).

Export-Gating wie generate_moodle_import.py: Standard nur freigegebene Karten;
--preview nimmt Karten im Review auf, markiert sie mit ENTWURF-Wasserzeichen und legt
sie getrennt unter exports/preview/print bzw. dist/preview/print ab.

Usage:
    python3 scripts/pharma/generate_print_sheets.py [--preview] [--packages a,b]
        [--variants A4_2up_marks,...] [--flip long|short] [--no-singles] [--no-png]
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_cards  # noqa: E402
from generate_moodle_import import (  # noqa: E402
    DISCLAIMER, in_package, load_packages, load_yaml, select_cards, sha256, write_zip)

CARD_W, CARD_H = 148.0, 105.0          # Fertigformat DIN A6 quer (mm)
PAPER = {"A4": (210.0, 297.0), "A3": (297.0, 420.0)}
BLEED = 3.0                             # Beschnitt je Seite (mm)
MARK_OFFSET, MARK_LEN = 1.5, 4.0        # Schnittmarken: Abstand zum Beschnitt, Länge
MARGIN_MARKS, MARGIN_PLAIN = 16.0, 8.0  # Papierrand mit/ohne Marken
READABLE_MIN_SCALE = 0.65               # darunter: Hinweis „kompakt, kleine Schrift“

# name: (Papier, Karten pro Bogen, Schnittmarken+Beschnitt)
VARIANTS = {
    "A4_2up_Schnittmarken": ("A4", 2, True),
    "A4_2up_ohne_Marken": ("A4", 2, False),
    "A4_4up_Schnittmarken": ("A4", 4, True),
    "A4_8up_kompakt": ("A4", 8, True),
    "A3_8up_Schnittmarken": ("A3", 8, True),
}
PREVIEW_MARK = "ENTWURF – nicht freigegeben"


@dataclass(frozen=True)
class Layout:
    paper: str
    orientation: str        # "hoch" | "quer"
    width: float            # Seitenbreite (mm)
    height: float
    cols: int
    rows: int
    scale: float
    bleed: float
    marks: bool
    x0: float               # linke obere Ecke des ersten Fertigformats (mm)
    y0: float

    @property
    def gutter(self) -> float:
        return 2 * self.bleed   # Beschnitt zweier Nachbarkarten stößt aneinander

    @property
    def card_w(self) -> float:
        return CARD_W * self.scale

    @property
    def card_h(self) -> float:
        return CARD_H * self.scale

    def trim_origin(self, slot: int) -> tuple[float, float]:
        r, c = divmod(slot, self.cols)
        return (self.x0 + c * (self.card_w + self.gutter),
                self.y0 + r * (self.card_h + self.gutter))


def compute_layout(paper: str, per_page: int, marks: bool) -> Layout:
    """Wählt Ausrichtung und Raster so, dass die Karten maximal groß (≤ 100 %) werden."""
    pw, ph = PAPER[paper]
    bleed = BLEED if marks else 0.0
    margin = MARGIN_MARKS if marks else MARGIN_PLAIN
    gutter = 2 * bleed
    best = None
    for orientation, (w, h) in (("hoch", (pw, ph)), ("quer", (ph, pw))):
        for cols in range(1, per_page + 1):
            if per_page % cols:
                continue
            rows = per_page // cols
            sx = (w - 2 * margin - (cols - 1) * gutter) / (cols * CARD_W)
            sy = (h - 2 * margin - (rows - 1) * gutter) / (rows * CARD_H)
            s = min(sx, sy, 1.0)
            if s <= 0:
                continue
            if best is None or s > best[0] + 1e-9:
                best = (s, orientation, w, h, cols, rows)
    s, orientation, w, h, cols, rows = best
    # Abrunden (nie aufrunden) und mit demselben Wert zentrieren, sonst ragt das Raster
    # um Bruchteile eines Millimeters über den Rand.
    s = math.floor(s * 10000) / 10000
    grid_w = cols * CARD_W * s + (cols - 1) * gutter
    grid_h = rows * CARD_H * s + (rows - 1) * gutter
    return Layout(paper, orientation, w, h, cols, rows, s, bleed, marks,
                  (w - grid_w) / 2, (h - grid_h) / 2)


def back_slot(layout: Layout, slot: int, flip: str) -> int:
    """Position der Rückseite für Duplex: Spiegelung je nach Wendekante."""
    r, c = divmod(slot, layout.cols)
    mirror_cols = (layout.orientation == "hoch") == (flip == "long")
    if mirror_cols:
        c = layout.cols - 1 - c
    else:
        r = layout.rows - 1 - r
    return r * layout.cols + c


SHEET_CSS = """
@page { size: %(w)smm %(h)smm; margin: 0; }
html, body { margin: 0; padding: 0; background: #fff; }
.sheet { position: relative; width: %(w)smm; height: %(h)smm; overflow: hidden;
         page-break-after: always; break-after: page; }
.sheet:last-child { page-break-after: auto; break-after: auto; }
.cell { position: absolute; background: #fff; overflow: hidden; }
.cell .bleed-top { position: absolute; left: 0; right: 0; top: 0; }
.cell .scaler { position: absolute; transform-origin: top left; }
.cell .card { box-shadow: none !important; }
.mark { position: absolute; background: #000; }
.label { position: absolute; font: 600 2mm/1 Arial, sans-serif; color: #555; white-space: nowrap; }
.wm { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
      pointer-events: none; }
.wm span { transform: rotate(-20deg); font: 800 9mm/1 Arial, sans-serif; color: rgba(200,0,0,.22);
           border: .8mm solid rgba(200,0,0,.22); padding: 1.5mm 4mm; white-space: nowrap; }
"""


def mm(v: float) -> str:
    return f"{v:.3f}mm"


def cell_html(card: dict, scope: dict, side: str, layout: Layout, slot: int, preview: bool) -> str:
    tx, ty = layout.trim_origin(slot)
    b = layout.bleed
    inner = (render_cards.front_inner(card, scope) if side == "front"
             else render_cards.back_inner(card, scope))
    accent = scope["category_color"].get(card.get("primary_category", ""), "#37474F")
    wm = f'<div class="wm"><span>{PREVIEW_MARK}</span></div>' if preview else ""
    bleed_top = (f'<div class="bleed-top" style="height:{mm(b)};background:{accent}"></div>'
                 if b > 0 else "")
    return (f'<div class="cell" style="left:{mm(tx - b)};top:{mm(ty - b)};'
            f'width:{mm(layout.card_w + 2 * b)};height:{mm(layout.card_h + 2 * b)}">'
            + bleed_top
            + f'<div class="scaler" style="left:{mm(b)};top:{mm(b)};transform:scale({layout.scale})">'
            + render_cards.card_div(card, scope, inner, side) + wm + "</div></div>")


def marks_html(layout: Layout, slots: int) -> str:
    if not layout.marks:
        return ""
    xs, ys = set(), set()
    for slot in range(slots):
        tx, ty = layout.trim_origin(slot)
        xs.update((round(tx, 3), round(tx + layout.card_w, 3)))
        ys.update((round(ty, 3), round(ty + layout.card_h, 3)))
    top = min(ys) - layout.bleed - MARK_OFFSET
    bottom = max(ys) + layout.bleed + MARK_OFFSET
    left = min(xs) - layout.bleed - MARK_OFFSET
    right = max(xs) + layout.bleed + MARK_OFFSET
    t = 0.1  # Linienstärke (mm)
    out = []
    for x in sorted(xs):
        out.append(f'<div class="mark" style="left:{mm(x - t / 2)};top:{mm(top - MARK_LEN)};'
                   f'width:{mm(t)};height:{mm(MARK_LEN)}"></div>')
        out.append(f'<div class="mark" style="left:{mm(x - t / 2)};top:{mm(bottom)};'
                   f'width:{mm(t)};height:{mm(MARK_LEN)}"></div>')
    for y in sorted(ys):
        out.append(f'<div class="mark" style="left:{mm(left - MARK_LEN)};top:{mm(y - t / 2)};'
                   f'width:{mm(MARK_LEN)};height:{mm(t)}"></div>')
        out.append(f'<div class="mark" style="left:{mm(right)};top:{mm(y - t / 2)};'
                   f'width:{mm(MARK_LEN)};height:{mm(t)}"></div>')
    return "".join(out)


def sheets_document(cards: list[dict], scope: dict, css: str, layout: Layout, flip: str,
                    title: str, preview: bool) -> str:
    n = layout.cols * layout.rows
    chunks = [cards[i:i + n] for i in range(0, len(cards), n)]
    pages = []
    for k, chunk in enumerate(chunks, 1):
        for side in ("front", "back"):
            cells = []
            for i, card in enumerate(chunk):
                slot = i if side == "front" else back_slot(layout, i, flip)
                cells.append(cell_html(card, scope, side, layout, slot, preview))
            side_de = "Vorderseiten" if side == "front" else "Rückseiten"
            label_y = layout.height - min(5.0, layout.y0 / 2)
            label = (f'<div class="label" style="left:{mm(layout.x0)};top:{mm(label_y)}">'
                     f'Pharma Cards · {title} · Bogen {k}/{len(chunks)} · {side_de} · '
                     f'{round(layout.scale * 100)} %{" · VORSCHAU" if preview else ""}</div>')
            pages.append('<section class="sheet">' + "".join(cells)
                         + marks_html(layout, len(chunk)) + label + "</section>")
    sheet_css = SHEET_CSS % {"w": layout.width, "h": layout.height}
    return ("<!doctype html><html lang=de><head><meta charset=utf-8>"
            f"<title>{title}</title><style>{css}{sheet_css}</style></head><body>"
            + "".join(pages) + "</body></html>")


def single_document(card: dict, scope: dict, css: str, preview: bool) -> str:
    wm = f'<div class="wm"><span>{PREVIEW_MARK}</span></div>' if preview else ""
    pages = []
    for side in ("front", "back"):
        inner = (render_cards.front_inner(card, scope) if side == "front"
                 else render_cards.back_inner(card, scope))
        pages.append('<section class="sheet" style="position:relative">'
                     + render_cards.card_div(card, scope, inner, side) + wm + "</section>")
    sheet_css = SHEET_CSS % {"w": CARD_W, "h": CARD_H}
    return ("<!doctype html><html lang=de><head><meta charset=utf-8>"
            f"<title>{card['card_id']}</title><style>{css}{sheet_css}</style></head><body>"
            + "".join(pages) + "</body></html>")


class Renderer:
    """Kapselt Chromium (Playwright); PDF/PNG nur, wenn verfügbar."""

    def __init__(self):
        self._pw = self._browser = self._page = None

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception:
            return self
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch()
        self._page = self._browser.new_page(device_scale_factor=3)
        return self

    def __exit__(self, *exc):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    @property
    def available(self) -> bool:
        return self._page is not None

    def pdf(self, html_doc: str, out: Path) -> None:
        self._page.set_content(html_doc, wait_until="load")
        self._page.pdf(path=str(out), prefer_css_page_size=True, print_background=True)

    def png(self, html_doc: str, out: Path) -> None:
        self._page.set_content(html_doc, wait_until="load")
        self._page.query_selector(".card").screenshot(path=str(out))


README_TMPL = """# Pharma Cards – Druckpaket: {name}{suffix}

{status_line}

**Karten:** {count} · **Stand:** {stand} · **Fertigformat:** DIN A6 quer, 148 × 105 mm

## Inhalt

| Datei | Papier | Karten/Bogen | Maßstab | Marken/Beschnitt | Zweck |
|---|---|---:|---:|---|---|
{variant_rows}
| `einzelkarten/<card_id>.pdf` | 148 × 105 mm | 1 | 100 % | nein | Einzelkarte, Seite 1 Vorder-, Seite 2 Rückseite |
| `png/<card_id>_front.png`, `_back.png` | – | – | – | – | Einzelbilder (Online, Präsentation) |

{scale_note}

## Duplexdruck

Jeder Vorderseitenbogen wird direkt vom passenden Rückseitenbogen gefolgt. Die Rückseiten sind
für das **Wenden an der {flip_de} Kante** gespiegelt angeordnet.

1. Im Druckdialog „Beidseitig“ mit Wenden an der {flip_de} Kante wählen, Skalierung **100 % /
   Tatsächliche Größe** (nicht „An Seite anpassen“).
2. Zuerst nur den ersten Bogen drucken und gegen das Licht prüfen, ob Vorder- und Rückseite passen.
3. An den Schnittmarken schneiden. Der Beschnitt (3 mm) verhindert weiße Blitzer am Rand.

## Druckvorstufe

- Die PDFs werden aus HTML über Chromium erzeugt und liegen im **RGB-Farbraum**. Für Büro- und
  Digitaldruck sind sie direkt geeignet. Für **Offsetdruck** muss die Druckerei bzw. Vorstufe in
  **PDF/X-4, CMYK, ISO Coated v2 (PSO)** wandeln (`print-production/specs/bleed-and-safe-zone.md`).
- Schriften sind eingebettet. Alle Inhalte liegen mindestens 5 mm innerhalb der Schnittkante;
  das wurde vor dem Export im Layout gemessen (`docs/pharma-cards/reports/layout_review.md`).
- **QR-Codes:** {qr_note} Vor jedem Druckauftrag mit mindestens drei Scanner-Apps testen
  (`print-production/specs/qr-print-spec.md`).

## Hinweis

{disclaimer}
"""


def variant_row(name: str, layout: Layout, file: str) -> str:
    marks = "ja, 3 mm" if layout.marks else "nein"
    purpose = ("Druckerei/Zuschnitt" if layout.marks and layout.scale >= 0.999 else
               "Büro-/Digitaldruck" if not layout.marks else
               "kompakter Wiederholungsdruck" if layout.scale < READABLE_MIN_SCALE else
               "verkleinerter Satz")
    return (f"| `{file}` | {layout.paper} {layout.orientation} | {layout.cols * layout.rows} | "
            f"{round(layout.scale * 100)} % | {marks} | {purpose} |")


def build_package(pkg: dict, cards: list[dict], scope: dict, css: str, out_root: Path,
                  dist: Path, cache: Path, rnd: Renderer, variants: list[str], flip: str,
                  preview: bool, singles: bool, pngs: bool) -> dict:
    suffix = "_VORSCHAU" if preview else ""
    pkg_dir = out_root / f"Pharma_Cards_Print_{pkg['label']}{suffix}"
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True)

    rows, made = [], []
    for name in variants:
        paper, per_page, marks = VARIANTS[name]
        layout = compute_layout(paper, per_page, marks)
        fname = f"Pharma_Cards_{pkg['label']}_{name}.pdf"
        html_doc = sheets_document(cards, scope, css, layout, flip, pkg["name"], preview)
        if rnd.available:
            rnd.pdf(html_doc, pkg_dir / fname)
        else:
            fname = fname.replace(".pdf", ".html")
            (pkg_dir / fname).write_text(html_doc, encoding="utf-8")
        rows.append(variant_row(name, layout, fname))
        made.append({"variant": name, "file": fname, "paper": paper, "orientation": layout.orientation,
                     "per_sheet": per_page, "scale": layout.scale, "marks": marks})

    if rnd.available and (singles or pngs):
        for card in cards:
            cid = card["card_id"]
            if singles:
                src = cache / "pdf" / f"{cid}.pdf"
                if not src.exists():
                    src.parent.mkdir(parents=True, exist_ok=True)
                    rnd.pdf(single_document(card, scope, css, preview), src)
                (pkg_dir / "einzelkarten").mkdir(exist_ok=True)
                shutil.copy2(src, pkg_dir / "einzelkarten" / src.name)
            if pngs:
                (pkg_dir / "png").mkdir(exist_ok=True)
                for side in ("front", "back"):
                    src = cache / "png" / f"{cid}_{side}.png"
                    if not src.exists():
                        src.parent.mkdir(parents=True, exist_ok=True)
                        inner = (render_cards.front_inner(card, scope) if side == "front"
                                 else render_cards.back_inner(card, scope))
                        rnd.png(render_cards.shell(card, scope, inner, css, side=side), src)
                    shutil.copy2(src, pkg_dir / "png" / src.name)

    stand = max((str(c.get("updated_at", "")) for c in cards), default="")
    small = [m for m in made if m["scale"] < READABLE_MIN_SCALE]
    scale_note = ("Varianten unter 100 % sind proportional verkleinert; die Schnittmarken gelten "
                  "dann für das verkleinerte Format. "
                  + (f"**{', '.join(m['variant'] for m in small)}:** sehr kleine Schrift, nur für "
                     "kompakte Wiederholungssätze geeignet." if small else ""))
    has_qr = render_cards.qr_svg("https://example.org") is not None
    qr_note = ("echte QR-Codes (Fehlerkorrektur Q, 15 × 15 mm, Vorderseite rechts unten)."
               if has_qr else "**Platzhalter** – Bibliothek `qrcode` fehlte beim Erzeugen. "
               "Nicht drucken, bevor echte QR-Codes eingebettet sind.")
    status_line = (f"> **VORSCHAU – {PREVIEW_MARK}.** Alle Karten tragen ein Wasserzeichen. "
                   "Nicht an Lernende ausgeben." if preview else
                   "> Freigegebenes Druckpaket (nur geprüfte Karten).")
    (pkg_dir / "README_PRINT.md").write_text(README_TMPL.format(
        name=pkg["name"], suffix=" (Vorschau)" if preview else "", status_line=status_line,
        count=len(cards), stand=stand, variant_rows="\n".join(rows), scale_note=scale_note,
        flip_de="langen" if flip == "long" else "kurzen", qr_note=qr_note,
        disclaimer=DISCLAIMER), encoding="utf-8")

    files = sorted(p for p in pkg_dir.rglob("*") if p.is_file())
    manifest = {
        "package": pkg["slug"], "name": pkg["name"], "label": pkg["label"], "kind": "print",
        "preview": preview, "stand": stand, "card_count": len(cards), "flip": flip,
        "variants": made,
        "cards": [{"card_id": c["card_id"], "title": c.get("title"), "version": c.get("version"),
                   "review_status": c.get("review_status"),
                   "warning_level": c.get("warning_level")} for c in cards],
        "files": {str(f.relative_to(pkg_dir)): sha256(f) for f in files},
    }
    (pkg_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zip_path = dist / f"{pkg_dir.name}.zip"
    write_zip(pkg_dir, zip_path)
    return {"package": pkg["slug"], "cards": len(cards), "variants": len(made), "zip": str(zip_path)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Druckpakete für PH erzeugen.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--scope", default="cards/PH/scope")
    ap.add_argument("--css", default="card-system/templates/pharma/card.css")
    ap.add_argument("--out", default=None, help="Default: exports/print/ph bzw. exports/preview/print")
    ap.add_argument("--dist", default=None, help="Default: dist/print bzw. dist/preview/print")
    ap.add_argument("--packages", default="", help="Kommagetrennte Paket-Slugs (Default: alle)")
    ap.add_argument("--variants", default=",".join(VARIANTS),
                    help=f"Kommagetrennt aus: {', '.join(VARIANTS)}")
    ap.add_argument("--flip", choices=["long", "short"], default="long")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--no-singles", action="store_true")
    ap.add_argument("--no-png", action="store_true")
    args = ap.parse_args()

    variants = [v for v in args.variants.split(",") if v]
    unknown = [v for v in variants if v not in VARIANTS]
    if unknown:
        ap.error(f"Unbekannte Variante(n): {', '.join(unknown)}")
    out = Path(args.out or ("exports/preview/print" if args.preview else "exports/print/ph"))
    dist = Path(args.dist or ("dist/preview/print" if args.preview else "dist/print"))
    cache = out / "_cache"
    if cache.exists():
        shutil.rmtree(cache)
    scope = render_cards.load_scope(Path(args.scope))
    css = Path(args.css).read_text(encoding="utf-8")
    all_cards = [load_yaml(p) for p in sorted(Path(args.cards).glob("*.yaml"))]
    cards = select_cards(all_cards, args.preview)
    wanted = {s for s in args.packages.split(",") if s}

    for name in variants:
        lay = compute_layout(*VARIANTS[name])
        print(f"  Variante {name}: {lay.paper} {lay.orientation}, {lay.cols}×{lay.rows}, "
              f"{round(lay.scale * 100)} %")
    print(f"{len(all_cards)} Karten gesamt, {len(cards)} für den Druck "
          f"({'VORSCHAU' if args.preview else 'nur freigegeben'}).")

    results, skipped = [], []
    with Renderer() as rnd:
        if not rnd.available:
            print("  [i] Playwright nicht verfügbar – Bögen als HTML, ohne Einzel-PDF/PNG.")
        for pkg in load_packages(Path(args.scope)):
            if wanted and pkg["slug"] not in wanted:
                continue
            pkg_cards = [c for c in cards if in_package(c, pkg)]
            if not pkg_cards:
                skipped.append(pkg["slug"])
                continue
            r = build_package(pkg, pkg_cards, scope, css, out, dist, cache, rnd, variants,
                              args.flip, args.preview, not args.no_singles, not args.no_png)
            results.append(r)
            print(f"OK  {pkg['slug']}: {r['cards']} Karten, {r['variants']} Bogenvarianten -> {r['zip']}")
    if cache.exists():
        shutil.rmtree(cache)
    if skipped:
        print(f"--  ohne druckbare Karten übersprungen: {', '.join(skipped)}")
    print(f"\n{len(results)} Druckpakete erzeugt, {len(skipped)} übersprungen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
