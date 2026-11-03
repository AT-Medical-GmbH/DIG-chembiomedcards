"""LTI-1.3-Endpunkte für Moodle: Login-Init, Launch, Tool-JWKS, Deep-Linking-Antwort.

Nur aktiv mit LTI_ENABLED=true; sonst antworten alle Endpunkte mit 404.
"""
from __future__ import annotations

import html
from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth import Principal, get_principal
from ..db import get_db
from ..lti import CARD_RE, LtiError, LtiTool
from ..models import User
from ..services import CONTENT_SETS, get_visible_card

router = APIRouter(prefix="/api/lti", tags=["Moodle LTI 1.3"])
NO_STORE = {"Cache-Control": "no-store"}


def tool(request: Request) -> LtiTool:
    t = getattr(request.app.state, "lti", None)
    if t is None:
        raise HTTPException(404, "LTI ist nicht aktiviert")
    return t


def _error_page(msg: str, status: int = 400) -> HTMLResponse:
    body = ("<!doctype html><html lang=de><meta charset=utf-8><title>Pharma Cards – Start nicht möglich</title>"
            "<body style='font-family:system-ui,sans-serif;max-width:640px;margin:40px auto;padding:0 16px'>"
            f"<h1>Start aus Moodle nicht möglich</h1><p>{html.escape(msg)}</p>"
            "<p>Bitte die Aktivität in Moodle erneut öffnen. Besteht das Problem weiter, bitte die "
            "Kursleitung informieren.</p></body></html>")
    return HTMLResponse(body, status_code=status, headers=NO_STORE)


@router.get("/jwks")
def jwks(t: LtiTool = Depends(tool)):
    return t.jwks()


@router.api_route("/login", methods=["GET", "POST"])
async def login(request: Request, db: Session = Depends(get_db), t: LtiTool = Depends(tool)):
    params = dict(request.query_params)
    if request.method == "POST":
        params.update({k: str(v) for k, v in (await request.form()).items()})
    try:
        url = t.login_redirect(db, params)
    except LtiError as exc:
        return _error_page(str(exc))
    return RedirectResponse(url, status_code=302, headers=NO_STORE)


@router.post("/launch")
def launch(id_token: str = Form(...), state: str = Form(""), db: Session = Depends(get_db),
           t: LtiTool = Depends(tool)):
    try:
        claims = t.validate_launch(db, id_token, state)
        role = t.role(claims)
        if claims["https://purl.imsglobal.org/spec/lti/claim/message_type"] == "LtiDeepLinkingRequest" \
                and role != "teacher":
            raise LtiError("Inhalte auswählen dürfen nur Lehrende")
        subject = t.subject(claims)
        user = db.query(User).filter(User.subject == subject).one_or_none()
        if user is None:
            db.add(User(subject=subject, role=role))
        else:
            user.role = role
        db.commit()
        token = t.session_token(claims)
    except LtiError as exc:
        return _error_page(str(exc))
    deep = claims["https://purl.imsglobal.org/spec/lti/claim/message_type"] == "LtiDeepLinkingRequest"
    nxt = "/lti/auswahl" if deep else t.target(claims)
    # 303: Browser folgt mit GET; Token nur im Fragment (nicht in Server-Logs, nicht im Referer)
    return RedirectResponse(f"/lti/start#token={quote(token)}&next={quote(nxt, safe='')}",
                            status_code=303, headers=NO_STORE)


class DeepLinkItem(BaseModel):
    type: Literal["set", "card"]
    id: str = Field(min_length=1, max_length=80)


class DeepLinkIn(BaseModel):
    items: list[DeepLinkItem] = Field(min_length=1, max_length=20)


@router.post("/deep-link")
def deep_link(body: DeepLinkIn, request: Request, db: Session = Depends(get_db),
              principal: Principal = Depends(get_principal), t: LtiTool = Depends(tool)):
    dl = getattr(request.state, "lti_claims", {}).get("dl")
    if not dl:
        raise HTTPException(403, "Keine Deep-Linking-Sitzung (Auswahl bitte aus Moodle starten)")
    if principal.role != "teacher":
        raise HTTPException(403, "Nur Lehrende")
    if not dl.get("multiple") and len(body.items) > 1:
        raise HTTPException(400, "Moodle erlaubt hier nur einen Inhalt")
    items = []
    for it in body.items:
        if it.type == "set":
            if it.id not in CONTENT_SETS:
                raise HTTPException(404, f"Lernset unbekannt: {it.id}")
            items.append(t.content_item(f"Pharma Cards – {CONTENT_SETS[it.id]['name']}", {"set": it.id}))
        else:
            if not CARD_RE.match(it.id):
                raise HTTPException(400, "Kartennummer ungültig")
            card = get_visible_card(db, it.id, principal, request.app.state.settings)  # nur freigegebene
            items.append(t.content_item(f"Pharma Cards – {card.title}", {"card": it.id}))
    return {"return_url": dl["return_url"], "jwt": t.deep_link_response(dl, items)}
