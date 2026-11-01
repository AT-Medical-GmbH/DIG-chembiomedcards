"""Notizen unter Karten (privat oder für den Kurs) inkl. Annotationen als JSON-Overlay."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..auth import Principal, get_principal
from ..db import get_db
from ..models import Card, ExportLog, UserNote
from ..services import aware, get_visible_card

router = APIRouter(prefix="/api", tags=["Notizen"])
MAX_NOTE = 20_000


class NoteIn(BaseModel):
    note_text: str = Field("", max_length=MAX_NOTE)
    annotation_data: dict | None = None   # z. B. {"shapes": [{"type": "arrow", "x": .., "y": ..}]}
    visibility: Literal["private", "course"] = "private"


def note_dict(n: UserNote, card_id: str, own: bool) -> dict:
    return {"id": n.id, "card_id": card_id, "note_text": n.note_text,
            "annotation_data": n.annotation_data, "visibility": n.visibility, "own": own,
            "created_at": aware(n.created_at).isoformat(), "updated_at": aware(n.updated_at).isoformat()}


def _own_note(db: Session, note_id: int, principal: Principal) -> UserNote:
    note = db.get(UserNote, note_id)
    if note is None or note.user_id != principal.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notiz nicht gefunden")
    return note


@router.get("/cards/{card_id}/notes")
def list_notes(card_id: str, request: Request, db: Session = Depends(get_db),
               principal: Principal = Depends(get_principal)):
    """Eigene Notizen plus Kursnotizen anderer (Dozierende) zu dieser Karte."""
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    rows = db.scalars(select(UserNote).where(UserNote.card_id == card.id, or_(
        UserNote.user_id == principal.id, UserNote.visibility == "course"))
        .order_by(UserNote.updated_at.desc()))
    return {"card_id": card.card_id,
            "notes": [note_dict(n, card.card_id, n.user_id == principal.id) for n in rows]}


@router.post("/cards/{card_id}/notes", status_code=status.HTTP_201_CREATED)
def create_note(card_id: str, body: NoteIn, request: Request, db: Session = Depends(get_db),
                principal: Principal = Depends(get_principal)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    if body.visibility == "course" and principal.role not in {"teacher", "editor", "admin"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Kursnotizen nur für Dozierende")
    note = UserNote(user_id=principal.id, card_id=card.id, note_text=body.note_text,
                    annotation_data=body.annotation_data, visibility=body.visibility)
    db.add(note)
    db.commit()
    return note_dict(note, card.card_id, True)


@router.put("/notes/{note_id}")
def update_note(note_id: int, body: NoteIn, db: Session = Depends(get_db),
                principal: Principal = Depends(get_principal)):
    note = _own_note(db, note_id, principal)
    if body.visibility == "course" and principal.role not in {"teacher", "editor", "admin"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Kursnotizen nur für Dozierende")
    note.note_text, note.annotation_data, note.visibility = body.note_text, body.annotation_data, body.visibility
    db.commit()
    card = db.get(Card, note.card_id)
    return note_dict(note, card.card_id, True)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db),
                principal: Principal = Depends(get_principal)):
    db.delete(_own_note(db, note_id, principal))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/notes")
def my_notes(db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    rows = db.execute(select(UserNote, Card).join(Card, Card.id == UserNote.card_id)
                      .where(UserNote.user_id == principal.id).order_by(UserNote.updated_at.desc()))
    return {"notes": [{**note_dict(n, c.card_id, True), "title": c.title} for n, c in rows]}


@router.get("/notes/export")
def export_notes(db: Session = Depends(get_db), principal: Principal = Depends(get_principal)):
    """Eigene Notizen als Markdown-Datei."""
    rows = db.execute(select(UserNote, Card).join(Card, Card.id == UserNote.card_id)
                      .where(UserNote.user_id == principal.id).order_by(Card.card_id, UserNote.created_at))
    lines = ["# Meine Notizen – Pharma Cards", ""]
    for n, c in rows:
        lines += [f"## {c.title} (`{c.card_id}`)", "",
                  f"*Stand: {aware(n.updated_at):%d.%m.%Y %H:%M} UTC*", "", n.note_text or "_(leer)_", ""]
    db.add(ExportLog(user_id=principal.id, type="notes_export", format="md"))
    db.commit()
    return Response("\n".join(lines), media_type="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": 'attachment; filename="pharma-cards-notizen.md"'})
