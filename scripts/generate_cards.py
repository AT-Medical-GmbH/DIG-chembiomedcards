#!/usr/bin/env python3
"""Erzeugt alle Kartenartefakte reproduzierbar aus data/cards/*.yaml.

Ablauf (docs/concept/06-generation-pipeline.md):
  1. Laden + Validieren (bricht bei Fehlern ab)
  2. data/cards_master.json schreiben (kanonische Gesamtdatei)
  3. je Karte HTML aus der zentralen Vorlage templates/card_template.html
     rendern → Playwright (Chromium):
       generated/individual/front/<id>_front.png   (300 dpi)
       generated/individual/back/<id>_back.png     (300 dpi)
       generated/individual/pdf/<id>.pdf           (Vorder- + Rückseite, 148 × 105 mm)
       generated/individual/svg/<id>_front.svg     (Struktur, editierbar)
       generated/individual/html/<id>.html         (Render-Quelle)
       generated/preview/<id>.png                  (Vorschau Vorder|Rück)
  4. Qualitäts-Gates: Überlauf der Rückseite, Tab-Anzahl
  5. generated/manifest.json, generated/preview/contact_sheet_<topic_group>.png,
     reports/layout_review.md

Unveränderte Karten werden übersprungen. Ändert sich die Vorlage, die Tokens
oder ein Renderer, werden alle Karten neu erzeugt; ändert sich nur eine
Kartendatei, nur diese Karte.

    python3 scripts/generate_cards.py [--filter bc_1] [--force]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import sys
from pathlib import Path

import qrcode
import qrcode.image.svg
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cbm.fischer import fischer_svg  # noqa: E402
from cbm.molecule import molecule_svg  # noqa: E402
from cbm.model import ROOT, load_project  # noqa: E402

TEMPLATES = ROOT / "templates"
GEN = ROOT / "generated"
OUT = {k: GEN / "individual" / k for k in ("front", "back", "pdf", "svg", "html")}
PREVIEW = GEN / "preview"
REPORTS = ROOT / "reports"
CSS_PX_PER_MM = 96 / 25.4
TEMPLATE = "card_template.html"
RENDER_INPUTS = [
    TEMPLATES / TEMPLATE,
    ROOT / "scripts" / "cbm" / "fischer.py",
    ROOT / "scripts" / "cbm" / "molecule.py",
    ROOT / "scripts" / "generate_cards.py",
    ROOT / "brand" / "design-tokens" / "chembiomed.tokens.json",
    ROOT / "data" / "categories.yaml",
]


def css_vars(tokens: dict) -> str:
    c, f = tokens["colors"], tokens["format_mm"]
    pairs = {
        "--card-w": f"{f['width']}mm", "--card-h": f"{f['height']}mm",
        "--font": tokens["font_family"],
        "--c-surface": c["surface"], "--c-text": c["text"], "--c-muted": c["muted"],
        "--c-brand": c["brand"], "--c-tab-bg": c["tab_inactive_bg"],
        "--c-tab-text": c["tab_inactive_text"], "--c-structure": c["text"],
    }
    for name, box in tokens["boxes"].items():
        pairs[f"--b-{name}-accent"] = box["accent"]
        pairs[f"--b-{name}-bg"] = box["bg"]
    return ":root{" + ";".join(f"{k}:{v}" for k, v in pairs.items()) + "}"


def qr_svg(url: str) -> str:
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0,
                      error_correction=qrcode.constants.ERROR_CORRECT_M)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    return svg[svg.index("<svg"):]


def fix_pdf_size(path: Path, width_mm: float, height_mm: float) -> None:
    """Chromium rundet die Seitengröße auf ganze CSS-Pixel (~0,2 mm). Für den Druck
    wird das Endformat exakt gesetzt (Media-/Trim-Box, Ursprung oben links)."""
    w, h = width_mm / 25.4 * 72, height_mm / 25.4 * 72
    reader, writer = PdfReader(path), PdfWriter()
    for page in reader.pages:
        top = float(page.mediabox.top)
        box = RectangleObject([0, top - h, w, top])
        page.mediabox = page.cropbox = page.trimbox = box
        writer.add_page(page)
    writer.add_metadata({"/Title": path.stem, "/Creator": "ChemBioMed Cards generate_cards.py"})
    with path.open("wb") as fh:
        writer.write(fh)


def clean(card: dict) -> dict:
    return {k: v for k, v in card.items() if not k.startswith("_")}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_master(project, path: Path) -> None:
    by_cat: dict[str, int] = {}
    for c in project.cards:
        by_cat[c["primary_category"]] = by_cat.get(c["primary_category"], 0) + 1
    master = {
        "schema": "data/schema/card.schema.json",
        "card_count": len(project.cards),
        "cards_per_primary_category": dict(sorted(by_cat.items())),
        "cards": [clean(c) for c in project.cards],
    }
    path.write_text(json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def preview_pair(front: Path, back: Path, dest: Path, width: int = 1100) -> None:
    a, b = Image.open(front).convert("RGB"), Image.open(back).convert("RGB")
    gap = 24
    h = a.height
    sheet = Image.new("RGB", (a.width * 2 + gap * 3, h + gap * 2), "#dfe4ea")
    sheet.paste(a, (gap, gap))
    sheet.paste(b, (a.width + gap * 2, gap))
    sheet.thumbnail((width, width))
    sheet.save(dest, optimize=True)


def contact_sheets(cards: list[dict]) -> list[Path]:
    """Eine Übersicht je topic_group (Review im Pull Request)."""
    for old in PREVIEW.glob("contact_sheet*.png"):
        old.unlink()
    groups: dict[str, list[dict]] = {}
    for c in cards:
        groups.setdefault(c.get("topic_group", "sonstige"), []).append(c)
    out = []
    for group, members in groups.items():
        dest = PREVIEW / f"contact_sheet_{group}.png"
        contact_sheet(members, dest)
        out.append(dest)
    return out


def contact_sheet(cards: list[dict], dest: Path, cols: int = 2) -> None:
    tiles = [Image.open(PREVIEW / f"{c['card_id']}.png") for c in cards]
    if not tiles:
        return
    tw, th = tiles[0].size
    label_h, pad = 34, 16
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + label_h + pad) + pad), "#f5f7fa")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("Inter", 20)
    except OSError:
        font = ImageFont.load_default()
    for i, (card, tile) in enumerate(zip(cards, tiles)):
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + label_h + pad)
        draw.text((x + 4, y + 6), f"{card['card_id']} · {card['title']} · {card['review_status']}",
                  fill="#1a202c", font=font)
        sheet.paste(tile, (x, y + label_h))
    sheet.save(dest, optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--filter", help="nur card_ids mit diesem Präfix")
    ap.add_argument("--force", action="store_true", help="alle Karten neu rendern")
    args = ap.parse_args()

    project = load_project(args.filter)
    if project.errors:
        for i in project.errors:
            print(f"ERROR {i.card_id}: {i.message}")
        print(f"Abbruch: {len(project.errors)} Validierungsfehler.")
        return 1

    for d in [*OUT.values(), PREVIEW, REPORTS]:
        d.mkdir(parents=True, exist_ok=True)
    if not args.filter:
        write_master(project, ROOT / "data" / "cards_master.json")

    env = Environment(loader=FileSystemLoader(TEMPLATES), undefined=StrictUndefined, autoescape=True)
    template = env.get_template(TEMPLATE)
    style_vars = css_vars(project.tokens)
    render_hash = sha256(b"".join(p.read_bytes() for p in RENDER_INPUTS))
    year = dt.date.today().year

    manifest_path = GEN / "manifest.json"
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"cards": {}}
    manifest = {"render_hash": render_hash, "cards": dict(old.get("cards", {}))}
    findings: list[tuple[str, str, str]] = []
    fmt = project.tokens["format_mm"]
    scale = project.tokens["export_dpi"] / 96
    rendered = skipped = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(
            viewport={"width": round(fmt["width"] * CSS_PX_PER_MM) + 2,
                      "height": round(fmt["height"] * CSS_PX_PER_MM) * 2 + 4},
            device_scale_factor=scale,
        )
        for card in project.cards:
            cid = card["card_id"]
            content_hash = sha256(json.dumps(clean(card), sort_keys=True, ensure_ascii=False).encode()
                                  + render_hash.encode())
            paths = {
                "front_png": OUT["front"] / f"{cid}_front.png",
                "back_png": OUT["back"] / f"{cid}_back.png",
                "pdf": OUT["pdf"] / f"{cid}.pdf",
                "html": OUT["html"] / f"{cid}.html",
                "preview": PREVIEW / f"{cid}.png",
            }
            prev = manifest["cards"].get(cid, {})
            if (not args.force and prev.get("content_hash") == content_hash
                    and all(p.exists() for p in paths.values())):
                skipped += 1
                findings += [tuple(f) for f in prev.get("findings", [])]
                continue

            primary_color = next(t["color"] for t in project.tabs if t["key"] == card["primary_category"])
            ctx = {"card": card, "tabs": project.tabs, "primary_color": primary_color, "year": year}
            svg = ""
            render = card["front_content"].get("render")
            if render in ("fischer_projection", "molecule"):
                svg = (fischer_svg if render == "fischer_projection" else molecule_svg)(card["front_content"])
                paths["svg"] = OUT["svg"] / f"{cid}_front.svg"
                paths["svg"].write_text(svg, encoding="utf-8")
            html = template.render(**ctx, css_vars=style_vars, front_svg=svg,
                                   qr_svg=qr_svg(card["qr_url"]))
            paths["html"].write_text(html, encoding="utf-8")
            page.set_content(html, wait_until="load")
            page.evaluate("document.fonts.ready")

            card_findings = []
            checks = page.evaluate("""() => {
                const c = document.querySelector('.back .content');
                return {
                  overflow: c.scrollHeight - c.clientHeight,
                  tabs: [...document.querySelectorAll('.card')].map(s => s.querySelectorAll('.tab').length),
                  active: [...document.querySelectorAll('.card')].map(s => s.querySelectorAll('.tab.active').length),
                  font: getComputedStyle(document.querySelector('.back h1')).fontFamily,
                  labelOverlaps: (() => {
                    // Beschriftungen der RDKit-Strukturformel (Pfade class="atom-N") je Atom bündeln;
                    // gemeldet wird, wenn zwei Beschriftungen weniger als ≈ 1 mm Abstand haben
                    const boxes = {};
                    document.querySelectorAll('.front svg.molecule path[class^="atom-"]').forEach(el => {
                      const r = el.getBoundingClientRect(), k = el.getAttribute('class');
                      const b = boxes[k] || {l: r.left, t: r.top, r: r.right, b: r.bottom};
                      boxes[k] = {l: Math.min(b.l, r.left), t: Math.min(b.t, r.top),
                                  r: Math.max(b.r, r.right), b: Math.max(b.b, r.bottom)};
                    });
                    const keys = Object.keys(boxes), hits = [], pad = -3.8;  // Mindestabstand ≈ 1 mm
                    for (let i = 0; i < keys.length; i++) for (let j = i + 1; j < keys.length; j++) {
                      const a = boxes[keys[i]], c = boxes[keys[j]];
                      if (a.l + pad < c.r && c.l + pad < a.r && a.t + pad < c.b && c.t + pad < a.b)
                        hits.push(keys[i] + '/' + keys[j]);
                    }
                    return hits;
                  })(),
                };
            }""")
            if checks["overflow"] > 1:
                card_findings.append(("error", f"Rückseite läuft um {checks['overflow']} px über die Inhaltszone"))
            if checks["labelOverlaps"]:
                card_findings.append(("error", "Atombeschriftungen zu dicht (< 1 mm: "
                                      + ", ".join(checks["labelOverlaps"][:4])
                                      + ") – front_content.layout auf 'rdkit' oder 'coordgen' setzen"))
            expected_font = project.tokens["font_family"].split(",")[0].strip()
            if not checks["font"].startswith(expected_font):
                card_findings.append(("error", f"Schrift '{checks['font']}' statt '{expected_font}' – CSS-Variablen prüfen"))
            if any(n != len(project.tabs) for n in checks["tabs"]) or any(n != 1 for n in checks["active"]):
                card_findings.append(("error", f"Tab-Leiste inkonsistent: {checks}"))

            page.locator(".card.front").screenshot(path=str(paths["front_png"]))
            page.locator(".card.back").screenshot(path=str(paths["back_png"]))
            page.pdf(path=str(paths["pdf"]), width=f"{fmt['width']}mm", height=f"{fmt['height']}mm",
                     print_background=True, prefer_css_page_size=True)
            fix_pdf_size(paths["pdf"], fmt["width"], fmt["height"])
            preview_pair(paths["front_png"], paths["back_png"], paths["preview"])

            manifest["cards"][cid] = {
                "title": card["title"],
                "review_status": card["review_status"],
                "content_hash": content_hash,
                "files": {k: str(p.relative_to(ROOT)) for k, p in paths.items()},
                "sha256": {k: sha256(p.read_bytes()) for k, p in paths.items() if k != "html"},
                "png_size_px": list(Image.open(paths["front_png"]).size),
                "findings": [(cid, lvl, msg) for lvl, msg in card_findings],
            }
            findings += [(cid, lvl, msg) for lvl, msg in card_findings]
            rendered += 1
            print(f"✓ {cid} {card['title']}" + (f"  ⚠ {len(card_findings)} Befund(e)" if card_findings else ""))
        browser.close()

    current = {c["card_id"] for c in project.cards}
    if not args.filter:
        manifest["cards"] = {k: v for k, v in manifest["cards"].items() if k in current}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not args.filter:
        contact_sheets(project.cards)
    if not args.filter:
        write_layout_report(project, findings)

    errors = [f for f in findings if f[1] == "error"]
    print(f"\n{rendered} gerendert · {skipped} unverändert übersprungen · {len(errors)} Layoutfehler")
    return 1 if errors else 0


def write_layout_report(project, findings) -> None:
    lines = [
        "# Layout-Review",
        "",
        "_Automatisch erzeugt von `scripts/generate_cards.py` – nicht von Hand bearbeiten._",
        "",
        f"Karten: **{len(project.cards)}** · Layoutbefunde: **{len(findings)}**",
        "",
        "Geprüft je Karte: Überlauf der Rückseiten-Inhaltszone, Anzahl Register-Tabs "
        f"(= {len(project.tabs)}), genau ein aktiver Haupttab.",
        "",
    ]
    if findings:
        lines += ["| Karte | Stufe | Befund |", "|---|---|---|"]
        lines += [f"| `{cid}` | {lvl} | {msg} |" for cid, lvl, msg in findings]
    else:
        lines.append("Keine Befunde.")
    lines += ["", "## Validierungshinweise (Daten)", "",
              "| Karte | Stufe | Hinweis |", "|---|---|---|"]
    lines += [f"| `{i.card_id}` | {i.level} | {i.message} |" for i in project.issues]
    (REPORTS / "layout_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
