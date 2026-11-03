#!/usr/bin/env python3
"""Validate Pharma Cards (Modul PH) metadata YAML.

Prüft jede Karte in cards/PH/metadata/*.yaml gegen:
  - Pflichtfelder des erweiterten PH-Content-Schemas
  - card_id-Muster ^ph_[0-9]{3}$ und Konsistenz zu slug
  - Scope-Enums aus cards/PH/scope/ (Kategorie, Wirkstoffgruppe, Tags, Warnlevel,
    Review-Status, Kartentyp, Front-Typ, Toxidrom, Antidot)
  - Governance-Regeln (Dosierung erfordert Quelle + Review; critical erfordert approved
    für Export; Antidot/Katecholamin -> warning_level >= high; Rückseitenlänge)
  - eindeutige card_id / slug
  - Verknüpfungsstandard QR → WikiMedica v0.2 (wirkstoff_slug/begriff_slug, qr_url daraus)

Exit 0 = alles gültig; Exit 1 = Fehler gefunden. Warnungen brechen nicht ab.

Usage:
    python3 scripts/pharma/validate_ph_cards.py [--cards DIR] [--scope DIR] [--strict]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML fehlt: pip install pyyaml")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiki_links  # noqa: E402  Verknüpfungsstandard QR → WikiMedica v0.2

CARD_ID = re.compile(r"^ph_[0-9]{3}$")

REQUIRED = [
    "card_id", "slug", "title", "module", "primary_category", "chapter",
    "card_type", "front_type", "level", "warning_level", "review_status",
    "version", "source_status", "created_at", "updated_at",
    "front_asset", "back_asset", "qr_url",
]

# Warnlevel, deren Export nur mit approved zulässig ist
GATE_APPROVED_ONLY = {"critical"}
GATE_REVIEWED_OK = {"moderate", "high"}
EXPORTABLE_STATUS = {"reviewed", "approved"}

# Wirkstoffgruppen, die mindestens high verlangen (Sicherheits-Heuristik)
HIGH_RISK_CLASSES = {"antidote", "katecholamine", "vasopressoren", "antikoagulanzien",
                     "herzglykoside", "opioide", "muskelrelaxanzien"}

MAX_BACK_CHARS = 1100  # Rückseite nicht überlang (Layout-Tauglichkeit)


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_scope(scope_dir: Path) -> dict:
    def keys(doc, listkey, field="slug"):
        return {item[field] for item in (doc or {}).get(listkey, []) if field in item}

    cats_doc = load_yaml(scope_dir / "categories.yaml") or {}
    categories = keys(cats_doc, "categories")
    categories |= {c["slug"] for c in cats_doc.get("future_categories", []) if "slug" in c}
    dc = load_yaml(scope_dir / "drug_classes.yaml") or {}
    tags = load_yaml(scope_dir / "tags.yaml") or {}
    wl = load_yaml(scope_dir / "warning_levels.yaml") or {}
    rs = load_yaml(scope_dir / "review_status.yaml") or {}
    ct = load_yaml(scope_dir / "card_types.yaml") or {}
    tox = load_yaml(scope_dir / "toxidromes.yaml") or {}
    anti = load_yaml(scope_dir / "antidotes.yaml") or {}
    return {
        "categories": categories,
        "drug_classes": keys(dc, "drug_classes"),
        "tags": keys(tags, "tags"),
        "warning_levels": {w["key"] for w in wl.get("warning_levels", [])},
        "review_status": {r["key"] for r in rs.get("review_status", [])},
        "card_types": {c["key"] for c in ct.get("card_types", [])},
        "front_types": {f["key"] for f in ct.get("front_types", [])},
        "toxidromes": keys(tox, "toxidromes") | {i["slug"] for i in tox.get("intoxications", [])},
        "antidotes": keys(anti, "antidotes"),
    }


def back_text_len(card: dict) -> int:
    total = 0
    for sec in card.get("back_sections", []) or []:
        total += len(str(sec.get("text") or sec.get("content") or ""))
    return total


def validate_card(card: dict, scope: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    cid = card.get("card_id", "<?>")

    for f in REQUIRED:
        if card.get(f) in (None, "", []):
            errors.append(f"{cid}: Pflichtfeld fehlt/leer: {f}")

    if card.get("module") != "PH":
        errors.append(f"{cid}: module muss 'PH' sein")
    if not CARD_ID.match(str(card.get("card_id", ""))):
        errors.append(f"{cid}: card_id-Muster ^ph_[0-9]{{3}}$ verletzt")
    slug = str(card.get("slug", ""))
    if slug and not slug.startswith(str(card.get("card_id", "")) + "_"):
        warnings.append(f"{cid}: slug beginnt nicht mit card_id (empfohlen)")

    def chk(field, allowed, label):
        v = card.get(field)
        if v and v not in allowed:
            errors.append(f"{cid}: {label} '{v}' nicht in Scope-Konfig")

    chk("primary_category", scope["categories"], "primary_category")
    for sc in card.get("secondary_categories", []) or []:
        if sc not in scope["categories"]:
            errors.append(f"{cid}: secondary_category '{sc}' nicht in Scope-Konfig")
    if card.get("drug_class"):
        chk("drug_class", scope["drug_classes"], "drug_class")
    chk("card_type", scope["card_types"], "card_type")
    chk("front_type", scope["front_types"], "front_type")
    chk("warning_level", scope["warning_levels"], "warning_level")
    chk("review_status", scope["review_status"], "review_status")
    if card.get("toxidrome"):
        chk("toxidrome", scope["toxidromes"], "toxidrome")
    if card.get("antidote"):
        chk("antidote", scope["antidotes"], "antidote")
    for t in card.get("tags", []) or []:
        if t not in scope["tags"]:
            errors.append(f"{cid}: tag '{t}' nicht im kontrollierten Vokabular")

    # Governance: Dosierung erfordert Quelle + Review
    if card.get("dose_contains_numeric") is True:
        if not card.get("references"):
            errors.append(f"{cid}: dose_contains_numeric=true ohne references")
        if card.get("review_status") == "draft":
            errors.append(f"{cid}: konkrete Dosis darf nicht als 'draft' final sein")

    # Sicherheits-Heuristik Warnlevel
    wl = card.get("warning_level")
    if (card.get("drug_class") in HIGH_RISK_CLASSES or card.get("antidote")) and wl == "low":
        warnings.append(f"{cid}: Hochrisiko-Kontext, warning_level 'low' erscheint zu niedrig")

    # Rückseitenlänge
    bl = back_text_len(card)
    if bl > MAX_BACK_CHARS:
        warnings.append(f"{cid}: Rückseite lang ({bl} Zeichen > {MAX_BACK_CHARS}) — Layout prüfen")

    # Export-Gating-Vorbedingung (nur Hinweis hier; hart in validate_output.py)
    if wl in GATE_APPROVED_ONLY and card.get("review_status") != "approved":
        warnings.append(f"{cid}: warning_level '{wl}' -> Export erst nach review_status=approved")

    # QR-Ziel nach Verknüpfungsstandard v0.2
    e, w = wiki_links.check(card)
    errors += e
    warnings += w

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="PH-Kartenmetadaten validieren.")
    ap.add_argument("--cards", default="cards/PH/metadata")
    ap.add_argument("--scope", default="cards/PH/scope")
    ap.add_argument("--strict", action="store_true", help="Warnungen als Fehler werten")
    args = ap.parse_args()

    scope = load_scope(Path(args.scope))
    files = sorted(Path(args.cards).glob("*.yaml"))
    if not files:
        print(f"Keine Karten in {args.cards} — nichts zu prüfen.")
        return 0

    all_err, all_warn = [], []
    seen_id, seen_slug = {}, {}
    for cf in files:
        try:
            card = load_yaml(cf)
        except Exception as e:
            all_err.append(f"{cf.name}: YAML-Fehler: {e}")
            continue
        cid, slug = card.get("card_id"), card.get("slug")
        if cid in seen_id:
            all_err.append(f"{cid}: doppelte card_id (auch in {seen_id[cid]})")
        seen_id[cid] = cf.name
        if slug in seen_slug:
            all_err.append(f"{slug}: doppelter slug (auch in {seen_slug[slug]})")
        seen_slug[slug] = cf.name
        e, w = validate_card(card, scope)
        all_err += e
        all_warn += w

    for w in all_warn:
        print(f"WARN  {w}")
    for e in all_err:
        print(f"ERROR {e}")

    print(f"\n{len(files)} Karten geprüft: {len(all_err)} Fehler, {len(all_warn)} Warnungen.")
    if all_err or (args.strict and all_warn):
        return 1
    print("Validierung bestanden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
