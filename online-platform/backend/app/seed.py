"""Seed: Scope-Konfiguration und Kartendaten (YAML) idempotent in die Datenbank übernehmen.

- Kategorien, Wirkstoffgruppen und Tags kommen aus cards/PH/scope/ (eine Definition, zwei
  Konsumenten: Export-Pipeline und Online-DB).
- Karten werden über `card_id` abgeglichen. Ändert sich der Inhalt (SHA-256 des Datensatzes),
  entsteht ein Snapshot in `card_versions` (Änderungsverlauf).
- Karten, die aus dem Repository verschwinden, werden deaktiviert, nicht gelöscht: Lernfortschritt
  und Notizen bleiben erhalten.

Aufruf:  python -m app.seed
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Card, CardVersion, Category, DrugClass, Tag


def _load(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def content_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False,
                                     default=str).encode("utf-8")).hexdigest()


def search_text(data: dict) -> str:
    parts = [data.get(k) for k in ("title", "subtitle", "substance_name", "generic_name",
                                    "drug_class", "antidote", "toxidrome", "mechanism_of_action",
                                    "indications", "adverse_effects", "contraindications",
                                    "interactions")]
    parts += [s.get("text", "") for s in data.get("back_sections") or []]
    parts += data.get("tags") or []
    return " ".join(str(p) for p in parts if p).lower()


def _upsert(db: Session, model, slug: str, **fields):
    obj = db.scalar(select(model).where(model.slug == slug))
    if obj is None:
        obj = model(slug=slug, **fields)
        db.add(obj)
    else:
        for k, v in fields.items():
            setattr(obj, k, v)
    return obj


def seed_scope(db: Session, scope_dir: Path) -> dict:
    cats = _load(scope_dir / "categories.yaml")
    n_cat = 0
    for c in cats.get("categories", []):
        _upsert(db, Category, c["slug"], name=c["name"], color=c.get("color"), icon=c.get("icon"),
                sort_order=c.get("sort", 1000), release=c.get("release"))
        n_cat += 1
    for i, c in enumerate(cats.get("future_categories", [])):
        _upsert(db, Category, c["slug"], name=c["name"], color=c.get("color"), icon=c.get("icon"),
                sort_order=2000 + i, release=c.get("release"))
        n_cat += 1
    db.flush()

    dcs = _load(scope_dir / "drug_classes.yaml").get("drug_classes", [])
    by_slug = {}
    for d in dcs:
        by_slug[d["slug"]] = _upsert(db, DrugClass, d["slug"], name=d["name"], color=d.get("color"),
                                     icon=d.get("icon"))
    db.flush()
    for d in dcs:
        parent = by_slug.get(d.get("parent")) if d.get("parent") else None
        by_slug[d["slug"]].parent_id = parent.id if parent else None

    tags = _load(scope_dir / "tags.yaml").get("tags", [])
    for t in tags:
        _upsert(db, Tag, t["slug"], name=t["name"])
    db.flush()
    return {"categories": n_cat, "drug_classes": len(dcs), "tags": len(tags)}


def seed_cards(db: Session, cards_dir: Path, changed_by: str = "seed") -> dict:
    cats = {c.slug: c for c in db.scalars(select(Category))}
    dcs = {d.slug: d for d in db.scalars(select(DrugClass))}
    tags = {t.slug: t for t in db.scalars(select(Tag))}
    existing = {c.card_id: c for c in db.scalars(select(Card))}
    seen, created, updated, versions = set(), 0, 0, 0

    for path in sorted(cards_dir.glob("*.yaml")):
        data = _load(path)
        cid = data["card_id"]
        seen.add(cid)
        h = content_hash(data)
        card = existing.get(cid)
        if card is None:
            card = Card(card_id=cid)
            db.add(card)
            created += 1
        elif card.content_hash == h and card.active:
            continue
        else:
            updated += 1
        card.slug = data.get("slug", cid)
        card.title = data.get("title", cid)
        card.subtitle = data.get("subtitle")
        card.substance_name = data.get("substance_name")
        card.card_type = data.get("card_type", "overview")
        card.front_type = data.get("front_type", "principle")
        card.level = data.get("level")
        card.difficulty = data.get("difficulty")
        card.warning_level = data.get("warning_level", "low")
        card.review_status = data.get("review_status", "draft")
        card.version = str(data.get("version", "0.0.0"))
        card.primary_category = cats.get(data.get("primary_category"))
        card.drug_class = dcs.get(data.get("drug_class"))
        card.secondary_categories = [cats[s] for s in data.get("secondary_categories") or [] if s in cats]
        card.tags = [tags[t] for t in data.get("tags") or [] if t in tags]
        card.front_content = data.get("front_content") or {}
        card.back_sections = data.get("back_sections") or []
        card.content = json.loads(json.dumps(data, default=str))
        card.search_text = search_text(data)
        card.content_hash = h
        card.qr_url = data.get("qr_url")
        card.lms_url = data.get("lms_url")
        card.active = True
        db.flush()
        db.add(CardVersion(card_id=card.id, version=card.version, content_hash=h,
                           content_snapshot=card.content, changed_by=changed_by,
                           change_note=f"Import aus {path.name}"))
        versions += 1

    deactivated = 0
    for cid, card in existing.items():
        if cid not in seen and card.active:
            card.active = False
            deactivated += 1
    return {"created": created, "updated": updated, "versions": versions,
            "deactivated": deactivated, "total": len(seen)}


def run(sessionmaker, settings) -> dict:
    with sessionmaker() as db:
        scope = seed_scope(db, settings.scope_dir)
        cards = seed_cards(db, settings.cards_dir)
        db.commit()
    return {"scope": scope, "cards": cards}


if __name__ == "__main__":  # pragma: no cover
    from .config import load_settings
    from .db import make_engine, make_sessionmaker
    s = load_settings()
    print(json.dumps(run(make_sessionmaker(make_engine(s.database_url)), s), indent=2))
