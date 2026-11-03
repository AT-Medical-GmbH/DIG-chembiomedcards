"""Downloads einzelner Karten (HTML, PDF, PNG) über den gemeinsamen Renderer.

Nicht freigegebene Karten (nur für Review-Rollen bzw. im Entwicklungsmodus sichtbar) erhalten
ein ENTWURF-Wasserzeichen. PDF/PNG brauchen Playwright + Chromium; fehlt das auf dem Server,
antwortet die API mit 503 und HTML bleibt verfügbar.
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from ..auth import Principal, get_principal
from ..db import get_db
from ..models import ExportLog
from ..services import get_visible_card, is_draft

router = APIRouter(prefix="/api/cards", tags=["Downloads"])

WATERMARK_CSS = """
.wm{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none}
.wm span{transform:rotate(-20deg);font:800 9mm/1 Arial,sans-serif;color:rgba(200,0,0,.22);
border:.8mm solid rgba(200,0,0,.22);padding:1.5mm 4mm;white-space:nowrap}
.page{position:relative;width:148mm;height:105mm;break-after:page}
.page:last-child{break-after:auto}
@page{size:148mm 105mm;margin:0}
@media screen{body{display:block}.page{margin:6mm auto}}
"""
WM = '<div class="wm"><span>ENTWURF – nicht freigegeben</span></div>'


def build_document(renderer, data: dict, sides: list[str], draft: bool) -> str:
    pages = "".join(f'<section class="page">{renderer.card_div(data, s)}{WM if draft else ""}</section>'
                    for s in sides)
    return ("<!doctype html><html lang=de><head><meta charset=utf-8>"
            f"<title>{data['card_id']}</title><style>{renderer.css}{WATERMARK_CSS}</style></head>"
            f"<body>{pages}</body></html>")


def _render_binary(doc: str, fmt: str) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "PDF/PNG-Export auf diesem Server nicht verfügbar (Playwright fehlt). "
                            "HTML-Download nutzen.") from exc
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(device_scale_factor=3)
            page.set_content(doc, wait_until="load")
            if fmt == "pdf":
                return page.pdf(prefer_css_page_size=True, print_background=True)
            return page.query_selector(".card").screenshot()
        finally:
            browser.close()


@router.get("/{card_id}/download")
def download(card_id: str, request: Request, side: Literal["front", "back", "both"] = "both",
             format: Literal["html", "pdf", "png"] = "pdf", db: Session = Depends(get_db),
             principal: Principal = Depends(get_principal)):
    card = get_visible_card(db, card_id, principal, request.app.state.settings)
    if format == "png" and side == "both":
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "PNG nur für eine Seite (front/back)")
    sides = ["front", "back"] if side == "both" else [side]
    draft = is_draft(card)
    doc = build_document(request.app.state.renderer, card.content, sides, draft)
    suffix = "_ENTWURF" if draft else ""
    name = f"{card.card_id}_{side}{suffix}.{format}"
    if format == "html":
        body, media = doc.encode("utf-8"), "text/html; charset=utf-8"
    else:
        body = _render_binary(doc, format)
        media = "application/pdf" if format == "pdf" else "image/png"
    db.add(ExportLog(user_id=principal.id, card_id=card.id, type="card_download", format=format))
    db.commit()
    return Response(body, media_type=media,
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})
