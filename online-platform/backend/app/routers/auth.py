"""Anmeldung der SPA: öffentliche Konfiguration und Token-Tausch (OIDC, PKCE).

Im lokalen Modus antworten die Endpunkte mit `mode: local` bzw. 404, damit die SPA weiß, dass sie
Test-Identitäten anbieten darf.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..oidc_client import OidcError

router = APIRouter(prefix="/api/auth", tags=["Anmeldung"])
NO_STORE = {"Cache-Control": "no-store", "Pragma": "no-cache"}


class TokenRequest(BaseModel):
    grant_type: str
    code: str | None = None
    code_verifier: str | None = None
    redirect_uri: str | None = None
    refresh_token: str | None = None


@router.get("/config")
def auth_config(request: Request):
    s = request.app.state.settings
    if s.auth_mode != "oidc":
        return {"mode": "local"}
    try:
        return {"mode": "oidc", **request.app.state.oidc.public_config()}
    except OidcError as exc:
        raise HTTPException(503, "Anmeldedienst derzeit nicht erreichbar") from exc


@router.post("/token")
def token(body: TokenRequest, request: Request):
    if request.app.state.settings.auth_mode != "oidc":
        raise HTTPException(404, "Nur im OIDC-Modus")
    try:
        status, payload = request.app.state.oidc.exchange(body.model_dump(exclude_none=True))
    except OidcError as exc:
        raise HTTPException(503, "Anmeldedienst derzeit nicht erreichbar") from exc
    if status != 200:
        # Fehlercodes des IdP durchreichen, aber nie 5xx-Details; 400 = Login neu starten
        return JSONResponse({"error": payload.get("error", "invalid_grant")},
                            status_code=400 if status < 500 else 502, headers=NO_STORE)
    return JSONResponse(payload, headers=NO_STORE)
