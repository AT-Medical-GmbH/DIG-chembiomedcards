#!/usr/bin/env python3
"""Stellt aus den erzeugten Karten ein veröffentlichbares Paket zusammen.

Kanäle (ADR-024, deploy/README_MIGRATION.md):
  staging     – alle Karten, jede mit Prüfstatus gekennzeichnet (interne Vorschau)
  production  – nur Karten mit review_status "approved"; ohne freigegebene Karten
                bricht das Skript mit Code 3 ab, damit nichts Ungeprüftes live geht

Voraussetzung: `make build` ist gelaufen (generated/manifest.json aktuell).

    python3 scripts/release_cards.py --channel staging    --out dist/staging
    python3 scripts/release_cards.py --channel production --out dist/production

Ergebnis in --out:
  cards/<id>.pdf, cards/<id>_front.png, cards/<id>_back.png, cards/<id>_front.svg
  preview/<id>.png
  release.json   – Kanal, Git-Stand, Zeitpunkt, Karten mit SHA-256
  SHA256SUMS     – Prüfsummen aller Dateien (sha256sum -c SHA256SUMS)
  index.html     – Übersichtsseite (statisch, ohne externe Abhängigkeiten)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "generated" / "manifest.json"
EXIT_NO_APPROVED = 3

# Dateien je Karte: Schlüssel im Manifest → Zielordner im Paket
COPY = {"pdf": "cards", "front_png": "cards", "back_png": "cards", "svg": "cards", "preview": "preview"}
STATUS_LABEL = {
    "approved": "freigegeben",
    "needs_review": "Fachreview offen",
    "review_needed": "Fachreview offen",
    "draft": "Entwurf",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_revision() -> str:
    # In CI ist der Stand als Umgebungsvariable gesetzt (Forgejo/GitHub Actions).
    for var in ("GITHUB_SHA", "FORGEJO_SHA", "CI_COMMIT_SHA"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unbekannt"


def render_index(channel: str, release: dict) -> str:
    rows = []
    for c in release["cards"]:
        cid = html.escape(c["card_id"])
        status = html.escape(STATUS_LABEL.get(c["review_status"], c["review_status"]))
        cls = "ok" if c["review_status"] == "approved" else "open"
        rows.append(
            f'<figure><a href="cards/{cid}.pdf"><img loading="lazy" src="preview/{cid}.png" '
            f'alt="{cid} {html.escape(c["title"])}"></a><figcaption><b>{cid}</b> '
            f'{html.escape(c["title"])} <span class="{cls}">{status}</span></figcaption></figure>'
        )
    banner = ("" if channel == "production" else
              '<p class="banner">Interne Vorschau (Staging). Karten ohne Freigabe sind nicht zur '
              'Weitergabe bestimmt.</p>')
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>ChemBioMed Cards – {html.escape(channel)}</title>
<style>
:root {{ --navy:#03204c; --petrol:#06807d; --red:#a90411; --muted:#5b6475; }}
body {{ margin:0; font-family: Inter, system-ui, sans-serif; color:var(--navy); background:#f6f7f9; }}
header {{ padding:16px; background:var(--navy); color:#fff; }}
header small {{ display:block; opacity:.8; }}
.banner {{ margin:0; padding:8px 16px; background:#fff4d6; color:#6b4e00; }}
main {{ display:grid; gap:16px; padding:16px; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); }}
figure {{ margin:0; background:#fff; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px #0002; }}
figure img {{ width:100%; display:block; }}
figcaption {{ padding:8px 10px; font-size:14px; }}
.ok {{ color:var(--petrol); }} .open {{ color:var(--red); }}
</style></head><body>
<header><b>ChemBioMed Cards</b> · {len(release["cards"])} Karten · Kanal {html.escape(channel)}
<small>Stand {html.escape(release["git_revision"][:12])} · {html.escape(release["created_at"])}</small></header>
{banner}
<main>
{chr(10).join(rows)}
</main></body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--channel", choices=("staging", "production"), required=True)
    ap.add_argument("--out", type=Path, required=True, help="Zielordner (wird neu angelegt)")
    args = ap.parse_args()

    if not MANIFEST.exists():
        print("Abbruch: generated/manifest.json fehlt – zuerst `make build` ausführen.")
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cards = manifest["cards"]

    errors = [f"{cid}: {msg}" for cid, c in cards.items() for _, lvl, msg in c.get("findings", [])
              if lvl == "error"]
    if errors:
        print("Abbruch: Layoutfehler im Manifest:\n  " + "\n  ".join(errors))
        return 1

    selected = {cid: c for cid, c in sorted(cards.items())
                if args.channel == "staging" or c["review_status"] == "approved"}
    if not selected:
        print(f"Abbruch: keine Karte mit review_status 'approved' – Produktion bleibt unverändert "
              f"({len(cards)} Karten warten auf Freigabe).")
        return EXIT_NO_APPROVED

    out: Path = args.out
    if out.exists():
        shutil.rmtree(out)
    for sub in set(COPY.values()):
        (out / sub).mkdir(parents=True)

    release = {
        "channel": args.channel,
        "git_revision": git_revision(),
        "created_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "render_hash": manifest.get("render_hash"),
        "cards": [],
    }
    for cid, c in selected.items():
        files = {}
        for key, sub in COPY.items():
            rel = c["files"].get(key)
            if not rel:
                continue
            src = ROOT / rel
            if not src.exists():
                print(f"Abbruch: {rel} fehlt – `make build` erneut ausführen.")
                return 1
            dst = out / sub / src.name
            shutil.copy2(src, dst)
            files[key] = str(dst.relative_to(out))
        release["cards"].append({"card_id": cid, "title": c["title"],
                                 "review_status": c["review_status"], "files": files})

    (out / "release.json").write_text(json.dumps(release, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    (out / "index.html").write_text(render_index(args.channel, release), encoding="utf-8")

    sums = [f"{sha256(p)}  {p.relative_to(out)}" for p in sorted(out.rglob("*"))
            if p.is_file() and p.name != "SHA256SUMS"]
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")

    approved = sum(c["review_status"] == "approved" for c in selected.values())
    print(f"✓ {args.channel}: {len(selected)} Karten ({approved} freigegeben) → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
