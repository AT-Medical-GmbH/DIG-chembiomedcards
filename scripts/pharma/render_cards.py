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


def footer_html(card: dict) -> str:
    cid = esc(card.get("card_id", ""))
    qr = esc(card.get("qr_url", ""))
    return (
        '<div class="footer"><div class="cid">' + cid + "</div>"
        '<div class="right">'
        f'<div class="qr">QR<br>{cid}</div>'
        '<div class="copy">© 2026 Andreas Tremml · AT Medical GmbH<br>'
        f'<span style="font-size:1.7mm">{qr}</span></div>'
        "</div></div>"
    )


def shell(card: dict, scope: dict, inner: str, css: str) -> str:
    accent = scope["category_color"].get(card.get("primary_category", ""), "#37474F")
    return (
        "<!doctype html><html lang=de><head><meta charset=utf-8>"
        f"<title>{esc(card.get('card_id',''))}</title><style>{css}</style></head><body>"
        f'<div class="card" style="--accent:{accent}">'
        + tabs_html(card) + inner + footer_html(card) + "</div></body></html>"
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


def box_html(title: str, content: str, role: str) -> str:
    role = role if role in VALID_ROLES else "base"
    return (
        f'<div class="box role-{role}"><div class="box-title">{esc(title)}</div>'
        f'<div class="box-content">{render_inline(content)}</div></div>'
    )


def back_inner(card: dict, scope: dict) -> str:
    head = head_html(card, scope)
    secs = card.get("back_sections") or []
    boxes = []
    for sec in secs:
        label = sec.get("label") or sec.get("key", "")
        text = sec.get("text") or sec.get("content") or ""
        boxes.append((label, text, sec.get("color_role", "base")))
    body = ['<div class="body">']
    if boxes:
        # erste Box breit (Kernaussage/Kernmechanismus)
        body.append('<div class="grid2" style="flex-direction:column">')
        body.append(box_html(*boxes[0]))
        body.append("</div>")
        mid = boxes[1:-1] if len(boxes) > 2 else boxes[1:]
        # mittlere Boxen paarweise
        for i in range(0, len(mid), 2):
            pair = mid[i:i + 2]
            body.append('<div class="grid2">')
            for b in pair:
                body.append(box_html(*b))
            body.append("</div>")
        if len(boxes) > 2:
            body.append('<div class="grid2" style="flex-direction:column">')
            body.append(box_html(*boxes[-1]))
            body.append("</div>")
    body.append("</div>")
    return head + "".join(body)


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
        bp.write_text(shell(card, scope, back_inner(card, scope), css), encoding="utf-8")
        html_paths.extend([fp, bp])
        print(f"OK  {card['card_id']}: {fp.name}, {bp.name}")

    n = maybe_render_binaries(html_paths, Path(args.png_out), args.png, args.pdf)
    print(f"\n{len(cards)} Karten, {len(html_paths)} HTML-Dateien erzeugt"
          + (f", {n} Binärdateien gerendert" if n else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
