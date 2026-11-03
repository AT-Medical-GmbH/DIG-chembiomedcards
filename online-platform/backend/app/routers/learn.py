"""Lernen: Lernsets, Lernwarteschlange, Bewertung (SM-2/Leitner), Markierungen, Statistik."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import srs
from ..auth import Principal, get_principal
from ..db import get_db
from ..models import Card, Category, StudyEvent, UserProgress
from ..services import (CONTENT_SETS, FLAGS, USER_SETS, aware, card_summary, filter_cards,
                        get_visible_card, now_utc, progress_dict, visible_cards)

router = APIRouter(prefix="/api", tags=["Lernen"])


class RatingIn(BaseModel):
    rating: Literal["again", "hard", "good", "easy"]
    algorithm: Literal["sm2", "leitner"] = "sm2"


class FlagsIn(BaseModel):
    flags: list[str] = Field(default_factory=list, max_length=len(FLAGS))


def _progress(db: Session, user_id: int) -> dict[int, UserProgress]:
    return {p.card_id: p for p in db.scalars(select(UserProgress).where(UserProgress.user_id == user_id))}


@router.get("/sets")
def list_sets():
    return {"content_sets": [{"slug": k, **v} for k, v in CONTENT_SETS.items()],
            "user_sets": [{"slug": k, "name": v} for k, v in USER_SETS.items()],
            "flags": list(FLAGS)}


@router.get("/learn/queue")
def learn_queue(request: Request, set: str = "alle", category: str | None = None,
                limit: int = 20, include_ahead: bool = False, db: Session = Depends(get_db),
                principal: Principal = Depends(get_principal)):
    """Lernstapel: zuerst fällige, dann neue Karten. Nutzer-Sets filtern nach Fortschritt."""
    settings = request.app.state.settings
    limit = max(1, min(limit, 100))
    stmt = visible_cards(principal, settings)
    content = CONTENT_SETS.get(set)
    if content:
        stmt = filter_cards(stmt, category=content.get("category"), card_type=content.get("card_type"))
    elif set not in USER_SETS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unbekanntes Lernset: {set}")
    if category:
        stmt = filter_cards(stmt, category=category)
    cards = list(db.scalars(stmt.order_by(Card.card_id)))
    prog = _progress(db, principal.id)
    now = now_utc()

    def due(c):
        p = prog.get(c.id)
        return p is not None and p.next_due_at is not None and aware(p.next_due_at) <= now

    picks = {
        "faellig": lambda c: due(c),
        "neu": lambda c: c.id not in prog,
        "unsicher": lambda c: c.id in prog and prog[c.id].status in {"unsure", "repeat"},
        "schwierig": lambda c: c.id in prog and (prog[c.id].lapses >= 2 or prog[c.id].ease_factor < 2.0),
        "favoriten": lambda c: c.id in prog and "favorit" in (prog[c.id].flags or []),
        "klinisch_wichtig": lambda c: c.id in prog and "klinisch_wichtig" in (prog[c.id].flags or []),
        "pruefungsrelevant": lambda c: c.id in prog and "pruefungsrelevant" in (prog[c.id].flags or []),
    }
    if set in picks:
        queue = [c for c in cards if picks[set](c)]
        queue.sort(key=lambda c: aware(prog[c.id].next_due_at) or now if c.id in prog else now)
    else:
        due_cards = sorted((c for c in cards if due(c)), key=lambda c: aware(prog[c.id].next_due_at))
        new_cards = [c for c in cards if c.id not in prog]
        queue = due_cards + new_cards
        if include_ahead and not queue:
            ahead = [c for c in cards if c.id in prog and not due(c)]
            queue = sorted(ahead, key=lambda c: aware(prog[c.id].next_due_at) or now)
    total = len(queue)
    return {"set": set, "total": total, "cards": [card_summary(c, prog.get(c.id)) for c in queue[:limit]]}


@router.post("/progress/{card_id}")
def rate_card(card_id: str, body: RatingIn, request: Request, db: Session = Depends(get_db),
              principal: Principal = Depends(get_principal)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    p = db.scalar(select(UserProgress).where(UserProgress.user_id == principal.id,
                                             UserProgress.card_id == card.id))
    if p is None:
        p = UserProgress(user_id=principal.id, card_id=card.id, flags=[], leitner_box=1,
                         ease_factor=2.5, interval_days=0, repetitions=0, lapses=0)
        db.add(p)
    state = srs.apply(srs.SrsState(p.ease_factor, p.interval_days, p.repetitions, p.leitner_box,
                                   p.lapses), body.rating, body.algorithm)
    now = now_utc()
    p.ease_factor, p.interval_days, p.repetitions = state.ease_factor, state.interval_days, state.repetitions
    p.leitner_box, p.lapses = state.leitner_box, state.lapses
    p.next_due_at, p.last_reviewed_at, p.last_rating = srs.next_due(now, state), now, body.rating
    p.status = srs.STATUS_BY_RATING[body.rating]
    db.add(StudyEvent(user_id=principal.id, card_id=card.id, rating=body.rating,
                      algorithm=body.algorithm, interval_days=state.interval_days,
                      leitner_box=state.leitner_box, ease_factor=state.ease_factor, created_at=now))
    db.commit()
    return {"card_id": card.card_id, "progress": progress_dict(p)}


@router.put("/progress/{card_id}/flags")
def set_flags(card_id: str, body: FlagsIn, request: Request, db: Session = Depends(get_db),
              principal: Principal = Depends(get_principal)):
    unknown = [f for f in body.flags if f not in FLAGS]
    if unknown:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Unbekannte Markierung: {unknown}")
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    p = db.scalar(select(UserProgress).where(UserProgress.user_id == principal.id,
                                             UserProgress.card_id == card.id))
    if p is None:
        p = UserProgress(user_id=principal.id, card_id=card.id, status="new", leitner_box=1,
                         ease_factor=2.5, interval_days=0, repetitions=0, lapses=0)
        db.add(p)
    p.flags = sorted(set(body.flags))
    db.commit()
    return {"card_id": card.card_id, "progress": progress_dict(p)}


@router.get("/cards/{card_id}/history")
def card_history(card_id: str, request: Request, db: Session = Depends(get_db),
                 principal: Principal = Depends(get_principal)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    events = db.scalars(select(StudyEvent).where(StudyEvent.user_id == principal.id,
                                                 StudyEvent.card_id == card.id)
                        .order_by(StudyEvent.created_at.desc()).limit(50))
    return {"card_id": card.card_id, "events": [
        {"rating": e.rating, "algorithm": e.algorithm, "interval_days": e.interval_days,
         "leitner_box": e.leitner_box, "at": aware(e.created_at).isoformat()} for e in events]}


@router.get("/stats")
def stats(request: Request, db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    settings = request.app.state.settings
    cards = list(db.scalars(visible_cards(principal, settings)))
    prog = _progress(db, principal.id)
    now = now_utc()
    per_cat: dict[str, Counter] = defaultdict(Counter)
    totals = Counter()
    for c in cards:
        cat = c.primary_category.slug if c.primary_category else "ohne_kategorie"
        p = prog.get(c.id)
        bucket = ("neu" if p is None or p.last_reviewed_at is None else
                  "beherrscht" if p.status == "mastered" else "in_arbeit")
        due = p is not None and p.next_due_at is not None and aware(p.next_due_at) <= now
        for counter in (per_cat[cat], totals):
            counter["gesamt"] += 1
            counter[bucket] += 1
            counter["faellig"] += int(due)
    since = now - timedelta(days=1)
    today = db.scalar(select(func.count(StudyEvent.id)).where(StudyEvent.user_id == principal.id,
                                                             StudyEvent.created_at >= since)) or 0
    names = {c.slug: c.name for c in db.scalars(select(Category))}
    return {
        "gesamt": dict(totals), "heute_bewertet": today, "tagesziel": settings.daily_goal,
        "kategorien": [{"slug": k, "name": names.get(k, k), **dict(v)}
                       for k, v in sorted(per_cat.items(), key=lambda kv: names.get(kv[0], kv[0]))],
    }
