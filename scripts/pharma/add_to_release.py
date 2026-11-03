#!/usr/bin/env python3
"""Legt die Pharma-Cards-Pakete (Modul PH) einem Karten-Release bei (gemeinsamer Umzugsplan, ADR-024).

Voraussetzung: scripts/release_cards.py hat <release> erzeugt, und die PH-Ziele sind gelaufen:
  staging:     make ph-moodle ph-print ph-review-packet ph-moodle-preview ph-print-preview
  production:  make ph-moodle ph-print

Übernommen nach <release>/pharma/:
  moodle/, print/     – nur freigegebene Karten (Export-Gating der PH-Pipeline), beide Kanäle
  preview/, review/   – Vorschauen mit ENTWURF-Wasserzeichen und Review-PDF, NUR im Kanal staging

Danach werden release.json (Abschnitt "pharma") und SHA256SUMS neu geschrieben, damit
deploy/scripts/publish-release.sh die Prüfsummen weiter kontrollieren kann.

    python3 scripts/pharma/add_to_release.py --channel staging --release dist/staging
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {"moodle": ("staging", "production"), "print": ("staging", "production"),
           "preview": ("staging",), "review": ("staging",)}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--channel", choices=("staging", "production"), required=True)
    ap.add_argument("--release", type=Path, required=True)
    ap.add_argument("--dist", type=Path, default=ROOT / "dist")
    a = ap.parse_args()

    rel = a.release
    meta_p = rel / "release.json"
    if not meta_p.is_file():
        print(f"Kein Release-Paket: {meta_p} fehlt", file=sys.stderr)
        return 2
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta.get("channel") != a.channel:
        print(f"Kanal passt nicht: release.json sagt {meta.get('channel')!r}", file=sys.stderr)
        return 2

    dest = rel / "pharma"
    shutil.rmtree(dest, ignore_errors=True)
    files = []
    for name, channels in SOURCES.items():
        src = a.dist / name
        if a.channel not in channels or not src.is_dir():
            continue
        for p in sorted(src.rglob("*")):
            if p.is_file():
                target = dest / name / p.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, target)
                files.append({"path": str(target.relative_to(rel)), "sha256": sha256(target),
                              "bytes": target.stat().st_size})

    note = ("Moodle- und Druckpakete enthalten nur fachlich freigegebene Karten. "
            "Vorschauen und Review-PDF sind ENTWURF und nur im Kanal staging enthalten.")
    meta["pharma"] = {"files": files, "note": note}
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = "\n".join(f'<li><a href="{html.escape(f["path"][len("pharma/"):])}">'
                     f'{html.escape(f["path"][len("pharma/"):])}</a> · {f["bytes"] // 1024} KB</li>'
                     for f in files) or "<li>Noch keine Pakete (keine Karte freigegeben).</li>"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(
        f"<!doctype html><html lang=de><meta charset=utf-8><title>Pharma Cards – {a.channel}</title>"
        f"<body style='font-family:system-ui;max-width:900px;margin:2rem auto'>"
        f"<h1>Pharma Cards (Modul PH) · {html.escape(a.channel)}</h1><p>{html.escape(note)}</p>"
        f"<p>Ausbildungs- und Lernmaterial, keine Therapieanweisung.</p><ul>{rows}</ul></body></html>\n",
        encoding="utf-8")
    index = rel / "index.html"
    if index.is_file():
        t = index.read_text(encoding="utf-8")
        link = '<p><a href="pharma/">Pharma Cards (Modul PH): Lern- und Druckpakete</a></p>'
        if link not in t:
            index.write_text(t.replace("</main>", f"</main>\n{link}", 1), encoding="utf-8")

    sums = [f"{sha256(p)}  {p.relative_to(rel)}" for p in sorted(rel.rglob("*"))
            if p.is_file() and p.name != "SHA256SUMS"]
    (rel / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"✓ PH-Pakete im Release {a.channel}: {len(files)} Dateien → {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
