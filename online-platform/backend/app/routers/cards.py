"""Karten: Liste/Suche, Detail, serverseitig gerenderte Kartenseite (für die Online-Ansicht)."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import Principal, get_principal
from ..db import get_db
from ..models import Card, UserProgress
from ..services import card_detail, card_summary, filter_cards, get_visible_card, is_draft, visible_cards

router = APIRouter(prefix="/api/cards", tags=["Karten"])


def _progress_map(db: Session, user_id: int, ids: list[int]) -> dict[int, UserProgress]:
    if not ids:
        return {}
    rows = db.scalars(select(UserProgress).where(UserProgress.user_id == user_id,
                                                 UserProgress.card_id.in_(ids)))
    return {p.card_id: p for p in rows}


@router.get("")
def list_cards(request: Request, category: str | None = None, drug_class: str | None = None,
               tag: str | None = None, q: str | None = Query(None, max_length=200),
               card_type: str | None = None, warning_level: str | None = None,
               db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    stmt = filter_cards(visible_cards(principal, request.app.state.settings), category=category,
                        drug_class=drug_class, tag=tag, q=q, card_type=card_type,
                        warning_level=warning_level).order_by(Card.card_id)
    cards = list(db.scalars(stmt))
    prog = _progress_map(db, principal.id, [c.id for c in cards])
    return {"count": len(cards), "cards": [card_summary(c, prog.get(c.id)) for c in cards]}


@router.get("/{card_id}")
def get_card(card_id: str, request: Request, db: Session = Depends(get_db),
             principal: Principal = Depends(get_principal)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    prog = _progress_map(db, principal.id, [card.id]).get(card.id)
    return card_detail(card, prog)


@router.get("/{card_id}/render")
def render_card(card_id: str, request: Request, side: Literal["front", "back"] = "front",
                db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    """HTML einer Kartenseite aus den strukturierten Daten (kein Bild). Inhalte sind durch den
    Renderer escaped; das CSS liefert /api/assets/card.css."""
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    return {"card_id": card.card_id, "side": side, "draft": is_draft(card),
            "html": request.app.state.renderer.card_div(card.content, side)}
