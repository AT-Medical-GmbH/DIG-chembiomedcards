#!/usr/bin/env python3
"""Leitet die Logo-Varianten aus dem freigegebenen Original ab (reproduzierbar).

Quelle:  brand/logo/source/chembiomed-cards-logo.png  (von AT Medical bereitgestellt)
Ausgabe: brand/logo/chembiomed-cards-logo-full.png     vollständiges Logo inkl. Unterzeilen
         brand/logo/chembiomed-cards-logo-compact.png  Bildmarke + Wortmarke, ohne Unterzeilen
                                                       (Kartenkopf – Unterzeilen wären auf A6 unlesbar)
         brand/logo/chembiomed-cards-mark.png          nur Bildmarke (Kartenstapel)

Alle Varianten mit transparentem Hintergrund (Weiß wird ausgefiltert, Kantenglättung bleibt
erhalten). Es wird nichts neu gezeichnet: Varianten sind reine Ausschnitte des Originals.

    python3 scripts/derive_logo_assets.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "brand" / "logo" / "source" / "chembiomed-cards-logo.png"
OUT = ROOT / "brand" / "logo"
INK = 200     # Pixel mit min(R,G,B) < INK zählen als Logo
PAD = 10      # Rand um Ausschnitte (px)


def runs(flags: list[bool], min_len: int = 4) -> list[tuple[int, int]]:
    out, start = [], None
    for i, v in enumerate(flags + [False]):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if i - start > min_len:
                out.append((start, i - 1))
            start = None
    return out


def white_to_alpha(im: Image.Image) -> Image.Image:
    rgba = Image.new("RGBA", im.size)
    src, dst = im.load(), rgba.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b = src[x, y]
            a = max(255 - r, 255 - g, 255 - b)
            if a < 10:
                dst[x, y] = (255, 255, 255, 0)
                continue
            k = 255 / a
            dst[x, y] = tuple(max(0, min(255, round(255 - (255 - c) * k))) for c in (r, g, b)) + (a,)
    return rgba


def main() -> int:
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    px = im.load()
    ink = lambda x, y: min(px[x, y]) < INK  # noqa: E731

    col_blocks = runs([any(ink(x, y) for y in range(h)) for x in range(w)])
    mark_x = col_blocks[0]                          # Bildmarke = erster Spaltenblock
    text_x = (col_blocks[1][0], col_blocks[-1][1])  # Wortmarke + Unterzeilen
    text_rows = runs([any(ink(x, y) for x in range(*text_x)) for y in range(h)])
    word_y = text_rows[0]                           # „Chem Bio Med | Cards“
    mark_rows = runs([any(ink(x, y) for x in range(mark_x[0], mark_x[1] + 1)) for y in range(h)], 0)
    mark_y = (mark_rows[0][0], mark_rows[-1][1])

    def crop(x0, y0, x1, y1):
        return im.crop((max(0, x0 - PAD), max(0, y0 - PAD), min(w, x1 + PAD + 1), min(h, y1 + PAD + 1)))

    top, bottom = min(mark_y[0], word_y[0]), max(mark_y[1], text_rows[-1][1])
    full = crop(mark_x[0], top, text_x[1], bottom)

    compact = crop(mark_x[0], top, text_x[1], max(mark_y[1], word_y[1])).copy()
    # Unterzeilen (rechts unterhalb der Wortmarke) ausblenden
    ox, oy = max(0, mark_x[0] - PAD), max(0, top - PAD)
    blank = Image.new("RGB", (compact.size[0] - (text_x[0] - PAD - ox), compact.size[1]), "white")
    gap = (word_y[1] + text_rows[1][0]) // 2 - oy
    compact.paste(blank.crop((0, 0, blank.size[0], compact.size[1] - gap)), (text_x[0] - PAD - ox, gap))

    mark = crop(mark_x[0], mark_y[0], mark_x[1], mark_y[1])

    for name, img in (("chembiomed-cards-logo-full.png", full),
                      ("chembiomed-cards-logo-compact.png", compact),
                      ("chembiomed-cards-mark.png", mark)):
        white_to_alpha(img).save(OUT / name, optimize=True)
        print(f"{name}: {img.size[0]} × {img.size[1]} px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
