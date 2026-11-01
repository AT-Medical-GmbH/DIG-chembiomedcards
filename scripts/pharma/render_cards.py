#!/usr/bin/env python3
"""Render Pharma Cards (Modul PH) from structured YAML + shared template.

Quelle der Wahrheit sind die Kartendaten (cards/PH/metadata/*.yaml) und die
Scope-Konfiguration (cards/PH/scope/*.yaml). Dieses Skript erzeugt pro Karte eine
self-contained Vorder- und Rückseite als HTML (deterministisch, nur Stdlib+PyYAML).
PNG/PDF werden optional über das vorinstallierte Chromium gerendert, wenn Playwright
verfügbar ist (CI/Deployment) — ohne Playwright bleibt die HTML-Ausgabe maßgeblich.

Usage:
    python3 scripts/pharma/render_cards.py \
        --cards cards/PH/metadata --scope cards/PH/scope \
        --out exports/web/ph/html [--png] [--pdf] [--png-out exports/preview/ph]

Siehe docs/pharma-cards/05_kartenlayout.md und 06_generierung-und-print.md.
"""
from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiki_links  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

# Feste Tab-Leiste (identisch über alle Karten) — Reihenfolge ist verbindlich.
TABS = ["Allgemein", "PK/PD", "Wirkstoff", "Klinik", "Tox", "Antidot", "Interaktion"]

# card_type -> aktiver Haupttab (Default; scope card_types.yaml kann das künftig tragen)
ACTIVE_TAB = {
    "overview": "Allgemein", "substance": "Wirkstoff", "mechanism": "PK/PD",
    "toxidrome": "Tox", "antidote": "Antidot", "interaction": "Interaktion",
    "case": "Klinik",
}

# Farbrolle (einer Box) -> Nebentab, der dadurch Inhalt bekommt
ROLE_TAB = {
    "base": "Allgemein", "pkpd": "PK/PD", "clinic": "Klinik", "risk": "Tox",
    "interaction": "Interaktion", "antidote": "Antidot",
}

VALID_ROLES = {"base", "pkpd", "clinic", "risk", "interaction", "antidote"}


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_scope(scope_dir: Path):
    cats = load_yaml(scope_dir / "categories.yaml") or {}
    wls = load_yaml(scope_dir / "warning_levels.yaml") or {}
    dcs = load_yaml(scope_dir / "drug_classes.yaml") or {}
    color = {}
    for c in cats.get("categories", []):
        color[c["slug"]] = c.get("color", "#37474F")
    warn = {w["key"]: w for w in wls.get("warning_levels", [])}
    dc_name = {d["slug"]: d.get("name", d["slug"]) for d in dcs.get("drug_classes", [])}
    return {"category_color": color, "warning_levels": warn, "drug_class_name": dc_name}


def esc(x) -> str:
    return html.escape(str(x if x is not None else ""))


def render_inline(text: str) -> str:
    """Sehr leichte Markdown-light-Umsetzung: Zeilen mit '- ' werden zur Liste."""
    if text is None:
        return ""
    lines = [ln.rstrip() for ln in str(text).strip().splitlines() if ln.strip()]
    if lines and all(ln.lstrip().startswith("- ") for ln in lines):
        items = "".join(f"<li>{esc(ln.lstrip()[2:])}</li>" for ln in lines)
        return f"<ul>{items}</ul>"
    return "<br>".join(esc(ln) for ln in lines)


def compute_tabs(card: dict) -> list[tuple[str, str]]:
    active = ACTIVE_TAB.get(card.get("card_type", "overview"), "Allgemein")
    secondary = set()
    for sec in card.get("back_sections", []) or []:
        role = sec.get("color_role")
        if role in ROLE_TAB:
            secondary.add(ROLE_TAB[role])
    if card.get("substance_name"):
        secondary.add("Wirkstoff")
    if card.get("antidote"):
        secondary.add("Antidot")
    if card.get("toxidrome") or card.get("toxicology_relevance"):
        secondary.add("Tox")
    out = []
    for t in TABS:
        if t == active:
            out.append((t, "active"))
        elif t in secondary:
            out.append((t, "secondary"))
        else:
            out.append((t, ""))
    return out


def tabs_html(card: dict) -> str:
    spans = [f'<span class="tab {cls}">{esc(t)}</span>' for t, cls in compute_tabs(card)]
    return f'<div class="tabs">{"".join(spans)}</div>'


def badge_html(card: dict, scope: dict) -> str:
    wl = card.get("warning_level", "low")
    meta = scope["warning_levels"].get(wl, {})
    label = meta.get("label", wl)
    return f'<span class="badge {esc(wl)}">{esc(label)}</span>'


def head_html(card: dict, scope: dict) -> str:
    title = esc(card.get("title", card.get("card_id", "")))
    sub = card.get("subtitle")
    sub_html = f'<div class="subtitle">{esc(sub)}</div>' if sub else ""
    return (
        '<div class="head"><div><div class="title">' + title + "</div>"
        + sub_html + "</div>" + badge_html(card, scope) + "</div>"
    )


QR_COLOR = "#0b4f8a"      # Verknüpfungsstandard v0.2: Dunkelblau auf Weiß, kein Logo
QR_CODE_MM = 15.0         # Kantenlänge des Codes ohne Ruhezone (Mindestmaß)
QR_BORDER = 4             # Ruhezone in Modulen


def qr_svg(url: str) -> tuple[str, float] | None:
    """QR-Code als SVG mit Ruhezone und Gesamtkantenlänge in mm.

    Verknüpfungsstandard QR → WikiMedica v0.2: Fehlerkorrektur M, Farbe #0b4f8a auf Weiß,
    Code ≥ 15 × 15 mm zuzüglich 4 Module Ruhezone, kein Logo. Gibt None zurück, wenn die
    optionale Bibliothek `qrcode` fehlt; dann wird ein Platzhalter gerendert.
    """
    if not url:
        return None
    try:
        import qrcode
    except ImportError:
        return None
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=QR_BORDER)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()  # inkl. Ruhezone
    n = len(matrix)
    total_mm = round(QR_CODE_MM * n / (n - 2 * QR_BORDER), 2)
    rects = "".join(f"M{x} {y}h1v1h-1z" for y, row in enumerate(matrix)
                    for x, dark in enumerate(row) if dark)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" '
           f'shape-rendering="crispEdges" role="img" aria-label="QR-Code {esc(url)}">'
           f'<rect width="{n}" height="{n}" fill="#fff"/><path d="{rects}" fill="{QR_COLOR}"/></svg>')
    return svg, total_mm


def qr_label(card: dict) -> str:
    """Bezeichnung unter dem QR-Code: Zieltyp und Name."""
    kind = "Wirkstoff" if card.get("substance_name") else "Begriff"
    return f"{kind}: {card.get('substance_name') or card.get('title', '')}"


def footer_html(card: dict, with_qr: bool = True) -> str:
    """Fußzeile: ID links, © rechts; QR-Code mit Klartext nur auf der Vorderseite (with_qr)."""
    cid = esc(card.get("card_id", ""))
    url = card.get("qr_url", "")
    qr = ""
    if with_qr:
        res = qr_svg(url)
        caption = (f'<figcaption><span class="lbl">{esc(qr_label(card))}</span>'
                   f'<span class="url">{esc(wiki_links.short_url(url))}</span></figcaption>')
        if res:
            svg, mm = res
            qr = (f'<figure class="qr-block" style="--qr-size:{mm}mm">'
                  f'<div class="qr">{svg}</div>{caption}</figure>')
        else:
            qr = (f'<figure class="qr-block"><div class="qr placeholder">QR<br>{cid}</div>'
                  f'{caption}</figure>')
    return (
        '<div class="footer"><div class="cid">' + cid + "</div>"
        '<div class="right">'
        '<div class="copy">© 2026 Andreas Tremml · AT Medical GmbH</div>'
        + qr + "</div></div>"
    )


def card_div(card: dict, scope: dict, inner: str, side: str = "front",
             extra_class: str = "") -> str:
    """Eine Kartenseite als <div class="card"> (ohne HTML-Dokument drumherum)."""
    accent = scope["category_color"].get(card.get("primary_category", ""), "#37474F")
    cls = f"card {side} {extra_class}".strip()
    return (f'<div class="{cls}" data-card="{esc(card.get("card_id", ""))}" '
            f'data-side="{side}" style="--accent:{accent}">'
            + tabs_html(card) + inner + footer_html(card, with_qr=(side == "front")) + "</div>")


def shell(card: dict, scope: dict, inner: str, css: str, side: str = "front") -> str:
    return (
        "<!doctype html><html lang=de><head><meta charset=utf-8>"
        f"<title>{esc(card.get('card_id',''))}</title><style>{css}</style></head><body>"
        + card_div(card, scope, inner, side) + "</body></html>"
    )


def front_inner(card: dict, scope: dict) -> str:
    head = head_html(card, scope)
    fc = card.get("front_content") or {}
    prompt = fc.get("prompt") or fc.get("question")
    ft = card.get("front_type", "principle")
    if ft in {"substance", "structure", "drug_class"} and not prompt:
        center = f'<div class="prompt">{esc(card.get("substance_name") or card.get("title"))}</div>'
        if card.get("drug_class"):
            name = scope["drug_class_name"].get(card["drug_class"], card["drug_class"])
            center += f'<div class="hint">{esc(name)}</div>'
    else:
        text = prompt or card.get("title", "")
        center = f'<div class="prompt">{esc(text)}</div>'
        hint = fc.get("hint")
        if hint:
            center += f'<div class="hint">{esc(hint)}</div>'
    return head + f'<div class="body"><div class="front-center"><div>{center}</div></div></div>'


def box_html(title: str, content: str, role: str, extra_class: str = "") -> str:
    role = role if role in VALID_ROLES else "base"
    cls = f"box role-{role} {extra_class}".strip()
    return (
        f'<div class="{cls}"><div class="box-title">{esc(title)}</div>'
        f'<div class="box-content">{render_inline(content)}</div></div>'
    )


def back_inner(card: dict, scope: dict) -> str:
    """Rückseite: erste Box (Kern) und letzte Box (Merke) volle Breite, dazwischen
    Zweispaltenfluss. Der Fluss verteilt Boxen nach Höhe und verschenkt keinen Platz
    wie eine starre Paarzeile (siehe docs/pharma-cards/05_kartenlayout.md)."""
    head = head_html(card, scope)
    boxes = []
    for sec in card.get("back_sections") or []:
        label = sec.get("label") or sec.get("key", "")
        text = sec.get("text") or sec.get("content") or ""
        boxes.append((label, text, sec.get("color_role", "base")))
    parts = ['<div class="body"><div class="flow">']
    for i, b in enumerate(boxes):
        span = (i == 0) or (i == len(boxes) - 1 and len(boxes) > 2)
        parts.append(box_html(*b, extra_class="span" if span else ""))
    parts.append("</div></div>")
    return head + "".join(parts)


def maybe_render_binaries(html_paths, png_dir: Path, do_png, do_pdf):
    if not (do_png or do_pdf):
        return 0
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("  [i] Playwright nicht verfügbar — überspringe PNG/PDF (HTML bleibt maßgeblich).")
        return 0
    import os
    png_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=4)  # ~300+ dpi bei 148×105mm
        for hp in html_paths:
            page.goto(hp.resolve().as_uri())
            el = page.query_selector(".card")
            if do_png:
                el.screenshot(path=str(png_dir / (hp.stem + ".png")))
                n += 1
            if do_pdf:
                page.pdf(path=str(png_dir / (hp.stem + ".pdf")),
                         width="148mm", height="105mm", print_background=True)
        browser.close()
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Pharma Cards (PH) aus YAML + Template.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--scope", default="cards/PH/scope")
    ap.add_argument("--css", default="card-system/templates/pharma/card.css")
    ap.add_argument("--out", default="exports/web/ph/html")
    ap.add_argument("--png", action="store_true", help="PNG rendern (braucht Playwright+Chromium)")
    ap.add_argument("--pdf", action="store_true", help="PDF rendern (braucht Playwright+Chromium)")
    ap.add_argument("--png-out", default="exports/preview/ph")
    args = ap.parse_args()

    scope = load_scope(Path(args.scope))
    css = Path(args.css).read_text(encoding="utf-8")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    cards = sorted(Path(args.cards).glob("*.yaml"))
    if not cards:
        print(f"Keine Karten in {args.cards}")
        return 0

    html_paths = []
    for cf in cards:
        card = load_yaml(cf)
        fp = out / f"{card['card_id']}_front.html"
        bp = out / f"{card['card_id']}_back.html"
        fp.write_text(shell(card, scope, front_inner(card, scope), css), encoding="utf-8")
        bp.write_text(shell(card, scope, back_inner(card, scope), css, side="back"),
                      encoding="utf-8")
        html_paths.extend([fp, bp])
        print(f"OK  {card['card_id']}: {fp.name}, {bp.name}")

    n = maybe_render_binaries(html_paths, Path(args.png_out), args.png, args.pdf)
    print(f"\n{len(cards)} Karten, {len(html_paths)} HTML-Dateien erzeugt"
          + (f", {n} Binärdateien gerendert" if n else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
