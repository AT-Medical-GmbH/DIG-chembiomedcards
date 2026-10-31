#!/usr/bin/env python3
"""Vektorisiert das Raster-Logo als Zwischenlösung (Entscheidung 2026-10-31, ADR-021).

Vorgehen: Original 3-fach hochskalieren → jede Fläche auf die gemessene Logofarbe abbilden
(Navy, Petrol, Rot, Grau, Weiß) → mit vtracer in Spline-Pfade umwandeln → Weiß entfernen.
Ergebnis: brand/logo/chembiomed-cards-logo-full.svg (Nachzeichnung, keine Originaldatei des
Logo-Erstellers – vor Verwendung im Druck abnehmen). Qualitätsvergleich gegen das Original:
`--check` rendert die SVG und meldet die Flächenübereinstimmung je Farbe.

    python3 scripts/vectorize_logo.py [--check]
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

import vtracer
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "brand" / "logo" / "source" / "chembiomed-cards-logo.png"
OUT = ROOT / "brand" / "logo" / "chembiomed-cards-logo-full.svg"
PALETTE = {"navy": (3, 32, 76), "teal": (6, 128, 125), "red": (169, 4, 17), "grey": (113, 116, 121),
           "white": (255, 255, 255)}
SCALE = 3


def nearest(p):
    return min(PALETTE.values(), key=lambda c: sum((a - b) ** 2 for a, b in zip(p, c)))


def quantize(im: Image.Image) -> Image.Image:
    big = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    pal = Image.new("P", (1, 1))
    flat = [v for c in PALETTE.values() for v in c]
    pal.putpalette(flat + [0] * (768 - len(flat)))
    q = big.quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB")
    # Grau kommt nur in der Unterzeile „by AT Medical GmbH®“ vor. Darüber sind graue Pixel
    # Kantenglättung farbiger Flächen → je nach Helligkeit Navy oder Weiß.
    grey_from = _grey_line_top(im) * SCALE
    qp, bp = q.load(), big.load()
    for y in range(grey_from):
        for x in range(q.width):
            if qp[x, y] == PALETTE["grey"]:
                r, g, b = bp[x, y]
                qp[x, y] = PALETTE["navy"] if 0.299 * r + 0.587 * g + 0.114 * b < 150 else PALETTE["white"]
    return q


def _grey_line_top(im: Image.Image) -> int:
    """Oberkante der letzten Textzeile (graue Unterzeile) im zugeschnittenen Logo."""
    px = im.load()
    rows = [any(min(px[x, y]) < 200 for x in range(im.width // 2, im.width)) for y in range(im.height)]
    y = im.height - 1
    while y > 0 and not rows[y]:
        y -= 1
    while y > 0 and rows[y]:
        y -= 1
    return max(0, y - 2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    im = Image.open(SRC).convert("RGB")
    # auf den Logo-Bereich zuschneiden (wie logo-full.png)
    bbox = Image.eval(im.convert("L"), lambda v: 255 if v < 200 else 0).getbbox()
    pad = 10
    im = im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))
    q = quantize(im)
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "q.png", Path(tmp) / "o.svg"
        q.save(src)
        vtracer.convert_image_to_svg_py(str(src), str(dst), colormode="color", hierarchical="cutout",
                                        mode="spline", filter_speckle=12, color_precision=8,
                                        layer_difference=24, corner_threshold=60, length_threshold=4.0,
                                        max_iterations=10, splice_threshold=45, path_precision=2)
        svg = dst.read_text()
    # weiße Flächen entfernen, Größe auf Original-Pixel normieren
    svg = re.sub(r'<path[^>]*fill="#(?:FFFFFF|FEFEFE|FDFDFD)"[^>]*/>\s*', "", svg, flags=re.I)
    w, h = im.width * SCALE, im.height * SCALE
    svg = re.sub(r'<svg[^>]*>', f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
                 f'width="{im.width}" height="{im.height}">', svg, count=1)
    svg = svg.replace("<svg", "<!-- ChemBioMed Cards Logo – automatische Nachzeichnung des Rasteroriginals "
                      "(scripts/vectorize_logo.py). Keine Originalvektordatei. -->\n<svg", 1)
    OUT.write_text(svg, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB, {svg.count('<path')} Pfade")
    if args.check:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": im.width, "height": im.height})
            pg.set_content(f"<body style='margin:0;background:#fff'>{svg}</body>")
            png = Path(tempfile.mkstemp(suffix=".png")[1]); pg.screenshot(path=str(png)); b.close()
        r = Image.open(png).convert("RGB").resize(im.size)
        ref = quantize(im).resize(im.size, Image.NEAREST)
        rp, qp = r.load(), ref.load()
        for name, col in PALETTE.items():
            if name == "white":
                continue
            a = b_ = inter = 0
            for y in range(im.height):
                for x in range(im.width):
                    ia = qp[x, y] == col
                    ib = nearest(rp[x, y]) == col
                    a += ia; b_ += ib; inter += ia and ib
            union = a + b_ - inter
            print(f"  {name:5}: Übereinstimmung (IoU) {inter / union:.1%}" if union else f"  {name}: –")
        r.save(ROOT / "generated" / "preview" / "logo_vector_check.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
