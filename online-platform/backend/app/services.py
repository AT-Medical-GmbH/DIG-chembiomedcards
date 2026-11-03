"""Gemeinsame Abfragen: Sichtbarkeit (Freigabe-Gating), Kartendarstellung, Rendering."""
from __future__ import annotations

import sys
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session

from .auth import Principal
from .config import Settings
from .models import Card, Category, UserProgress

DISCLAIMER = "Ausbildungs- und Lernmaterial – keine Therapieanweisung."

# Kuratierte Lernsets (Konzept 08 §2.1). Nutzerbezogene Sets (due/new/...) siehe learn-Router.
CONTENT_SETS = {
    "alle": {"name": "Alle Karten"},
    "notfall": {"name": "Notfallmedikamente trainieren", "category": "notfallmedikamente"},
    "antidote": {"name": "Antidote trainieren", "category": "antidote"},
    "toxidrome": {"name": "Toxidrome trainieren", "card_type": "toxidrome"},
}
USER_SETS = {
    "faellig": "Heute fällige Karten",
    "neu": "Neue Karten lernen",
    "unsicher": "Nur falsche/unsichere Karten",
    "favoriten": "Favoriten",
    "klinisch_wichtig": "Klinisch wichtig",
    "pruefungsrelevant": "Prüfungsrelevant",
    "schwierig": "Schwierige Karten",
}
FLAGS = ("favorit", "klinisch_wichtig", "pruefungsrelevant", "spaeter")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def aware(dt: datetime | None) -> datetime | None:
    """SQLite liefert naive Zeitstempel; alle Vergleiche laufen in UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def can_see_unreviewed(principal: Principal, settings: Settings) -> bool:
    return principal.can_review or settings.show_unreviewed


def visible_cards(principal: Principal, settings: Settings) -> Select:
    """Lernende sehen nur freigegebene Karten (`approved`). Fachreview-Rollen sehen alle aktiven
    Karten; im Entwicklungsmodus PHARMA_SHOW_UNREVIEWED ebenso (in Produktion gesperrt)."""
    stmt = select(Card).where(Card.active.is_(True))
    if not can_see_unreviewed(principal, settings):
        stmt = stmt.where(Card.review_status == "approved")
    return stmt


def in_category(slug: str):
    return or_(Card.primary_category.has(Category.slug == slug),
               Card.secondary_categories.any(Category.slug == slug))


def filter_cards(stmt: Select, *, category: str | None = None, drug_class: str | None = None,
                 tag: str | None = None, q: str | None = None, card_type: str | None = None,
                 warning_level: str | None = None) -> Select:
    from .models import DrugClass, Tag
    if category:
        stmt = stmt.where(in_category(category))
    if drug_class:
        stmt = stmt.where(Card.drug_class.has(DrugClass.slug == drug_class))
    if tag:
        stmt = stmt.where(Card.tags.any(Tag.slug == tag))
    if card_type:
        stmt = stmt.where(Card.card_type == card_type)
    if warning_level:
        stmt = stmt.where(Card.warning_level == warning_level)
    if q:
        terms = [t for t in q.lower().split() if t]
        stmt = stmt.where(and_(*[Card.search_text.contains(t) for t in terms]))
    return stmt


def get_visible_card(db: Session, card_id: str, principal: Principal, settings: Settings) -> Card:
    card = db.scalar(visible_cards(principal, settings).where(Card.card_id == card_id))
    if card is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Karte nicht gefunden oder nicht freigegeben")
    return card


def is_draft(card: Card) -> bool:
    return card.review_status != "approved"


def card_summary(card: Card, progress: UserProgress | None = None) -> dict:
    return {
        "card_id": card.card_id, "title": card.title, "subtitle": card.subtitle,
        "card_type": card.card_type, "warning_level": card.warning_level,
        "review_status": card.review_status, "draft": is_draft(card), "version": card.version,
        "primary_category": card.primary_category.slug if card.primary_category else None,
        "drug_class": card.drug_class.slug if card.drug_class else None,
        "tags": [t.slug for t in card.tags],
        "progress": progress_dict(progress),
    }


def card_detail(card: Card, progress: UserProgress | None = None) -> dict:
    d = card_summary(card, progress)
    d.update({
        "front_type": card.front_type, "front_content": card.front_content,
        "back_sections": card.back_sections,
        "secondary_categories": [c.slug for c in card.secondary_categories],
        "substance_name": card.substance_name, "qr_url": card.qr_url, "lms_url": card.lms_url,
        "antidote": card.content.get("antidote"), "toxidrome": card.content.get("toxidrome"),
        "related_cards": card.content.get("related_cards") or [],
        "learning_objectives": card.content.get("learning_objectives") or [],
        "disclaimer": DISCLAIMER,
    })
    return d


def progress_dict(p: UserProgress | None) -> dict | None:
    if p is None:
        return None
    return {"status": p.status, "flags": p.flags or [], "leitner_box": p.leitner_box,
            "ease_factor": p.ease_factor, "interval_days": p.interval_days,
            "repetitions": p.repetitions, "lapses": p.lapses,
            "next_due_at": aware(p.next_due_at).isoformat() if p.next_due_at else None,
            "last_reviewed_at": aware(p.last_reviewed_at).isoformat() if p.last_reviewed_at else None,
            "last_rating": p.last_rating}


# ---------------- Rendering (gemeinsamer Renderer der Export-Pipeline) ----------------

class Renderer:
    """Nutzt scripts/pharma/render_cards.py, damit Online, Druck und Moodle identisch aussehen."""

    def __init__(self, settings: Settings):
        if str(settings.pipeline_dir) not in sys.path:
            sys.path.insert(0, str(settings.pipeline_dir))
        import render_cards  # noqa: PLC0415
        self.rc = render_cards
        self.scope = render_cards.load_scope(settings.scope_dir)
        self.css = settings.css_path.read_text(encoding="utf-8")

    def inner(self, data: dict, side: str) -> str:
        return self.rc.front_inner(data, self.scope) if side == "front" else self.rc.back_inner(data, self.scope)

    def card_div(self, data: dict, side: str) -> str:
        return self.rc.card_div(data, self.scope, self.inner(data, side), side)
