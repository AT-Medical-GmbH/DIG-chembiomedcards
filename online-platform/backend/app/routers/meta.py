"""Metadaten: Gesundheit, eigenes Profil, Kategorien/Wirkstoffgruppen/Tags, Karten-CSS."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import Principal, get_principal
from ..db import get_db
from ..models import Category, DrugClass, Tag
from ..services import DISCLAIMER, can_see_unreviewed, filter_cards, visible_cards

router = APIRouter(prefix="/api", tags=["Meta"])


@router.get("/health")
def health(request: Request):
    s = request.app.state.settings
    return {"status": "ok", "env": s.env, "auth_mode": s.auth_mode}


@router.get("/me")
def me(request: Request, principal: Principal = Depends(get_principal)):
    s = request.app.state.settings
    return {"subject": principal.subject, "email": principal.email, "role": principal.role,
            "can_review": principal.can_review,
            "sees_unreviewed": can_see_unreviewed(principal, s),
            "dev_show_unreviewed": s.show_unreviewed, "disclaimer": DISCLAIMER}


@router.get("/meta")
def meta(request: Request, db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    """Nur Kategorien mit sichtbaren Karten, damit Lernende keine leeren Bereiche sehen."""
    s = request.app.state.settings
    base = visible_cards(principal, s)
    cats = []
    for c in db.scalars(select(Category).order_by(Category.sort_order, Category.name)):
        n = len(db.scalars(filter_cards(base, category=c.slug)).all())
        if n:
            cats.append({"slug": c.slug, "name": c.name, "color": c.color, "count": n})
    dcs = [{"slug": d.slug, "name": d.name} for d in db.scalars(select(DrugClass).order_by(DrugClass.name))]
    tags = [{"slug": t.slug, "name": t.name} for t in db.scalars(select(Tag).order_by(Tag.name))]
    return {"categories": cats, "drug_classes": dcs, "tags": tags,
            "warning_levels": ["low", "moderate", "high", "critical"], "disclaimer": DISCLAIMER}


@router.get("/assets/card.css")
def card_css(request: Request):
    """Dasselbe Karten-CSS wie Druck und Moodle (eine Quelle)."""
    return Response(request.app.state.renderer.css, media_type="text/css; charset=utf-8",
                    headers={"Cache-Control": "public, max-age=300"})
