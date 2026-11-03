"""Fachreview-Protokoll (nur Review-Rollen) und Änderungsverlauf je Karte.

Bewusste Grenze: Ein Review-Eintrag ändert NICHT den Freigabestatus der Karte. Verbindlich ist
`review_status` in den YAML-Daten im Repository (Git-Historie = Audit-Trail); nach dem Merge
übernimmt der Seed den neuen Status. So gibt es genau eine Quelle der Wahrheit.
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import Principal, require_review_role
from ..db import get_db
from ..models import CardVersion, ReviewEvent, User
from ..services import aware, get_visible_card

router = APIRouter(prefix="/api/cards", tags=["Review"])

REVIEW_TYPE = Literal["pharmacology", "toxicology", "clinical_safety", "editorial"]
REVIEW_RESULT = Literal["reviewed", "approved", "changes_requested", "clinical_review_needed",
                        "toxicology_review_needed", "update_needed"]


class ReviewIn(BaseModel):
    review_type: REVIEW_TYPE
    status: REVIEW_RESULT
    notes: str = Field("", max_length=10_000)


@router.post("/{card_id}/reviews", status_code=status.HTTP_201_CREATED)
def add_review(card_id: str, body: ReviewIn, request: Request, db: Session = Depends(get_db),
               principal: Principal = Depends(require_review_role)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    ev = ReviewEvent(card_id=card.id, reviewer_id=principal.id, review_type=body.review_type,
                     status=body.status, card_version=card.version, notes=body.notes or None)
    db.add(ev)
    db.commit()
    return {"id": ev.id, "card_id": card.card_id, "review_type": ev.review_type,
            "status": ev.status, "card_version": ev.card_version,
            "hinweis": "Protokolliert. Der verbindliche review_status wird in den Kartendaten "
                       "(Repository) gesetzt."}


@router.get("/{card_id}/reviews")
def list_reviews(card_id: str, request: Request, db: Session = Depends(get_db),
                 principal: Principal = Depends(require_review_role)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    rows = db.execute(select(ReviewEvent, User).join(User, User.id == ReviewEvent.reviewer_id)
                      .where(ReviewEvent.card_id == card.id).order_by(ReviewEvent.created_at.desc()))
    return {"card_id": card.card_id, "reviews": [
        {"id": e.id, "review_type": e.review_type, "status": e.status, "card_version": e.card_version,
         "notes": e.notes, "reviewer": u.email or u.subject, "role": u.role,
         "at": aware(e.created_at).isoformat()} for e, u in rows]}


@router.get("/{card_id}/versions")
def list_versions(card_id: str, request: Request, db: Session = Depends(get_db),
                  principal: Principal = Depends(require_review_role)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    rows = db.scalars(select(CardVersion).where(CardVersion.card_id == card.id)
                      .order_by(CardVersion.created_at.desc()))
    return {"card_id": card.card_id, "versions": [
        {"version": v.version, "content_hash": v.content_hash[:12], "changed_by": v.changed_by,
         "change_note": v.change_note, "at": aware(v.created_at).isoformat()} for v in rows]}
