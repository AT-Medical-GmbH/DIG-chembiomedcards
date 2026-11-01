"""Authentifizierung und Rollen.

AUTH_MODE=local (nur Entwicklung, in Produktion beim Start gesperrt):
    Nutzer über Header `X-User` (E-Mail/Kennung), Rolle optional über `X-Role`.
    Ohne Header: Gastnutzer `dev-learner` mit Rolle learner.
LTI (zusätzlich, wenn LTI_ENABLED): Bearer-Token, das die API selbst nach einem geprüften
    Moodle-Start ausgestellt hat (Issuer <PHARMA_PUBLIC_URL>/lti). Rolle nur learner/teacher.
AUTH_MODE=oidc (Betrieb, Authentik):
    Bearer-JWT, Signatur über JWKS (RS256/ES256), Issuer und Audience geprüft. Die Rolle kommt aus
    einem Gruppen-Claim (OIDC_ROLE_CLAIM) über OIDC_ROLE_MAP; ohne Treffer: learner.
"""
from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import REVIEW_ROLES, ROLES, Settings
from .db import get_db
from .lti import peek_issuer
from .models import User

# Rangfolge: höchste passende Gruppe gewinnt
ROLE_RANK = {r: i for i, r in enumerate(ROLES)}
LTI_ROLES = {"learner", "teacher"}       # über Moodle nie Review-/Admin-Rechte


@dataclass(frozen=True)
class Principal:
    id: int
    subject: str
    email: str | None
    role: str

    @property
    def can_review(self) -> bool:
        return self.role in REVIEW_ROLES


def _upsert_user(db: Session, subject: str, email: str | None, name: str | None, role: str) -> User:
    user = db.scalar(select(User).where(User.subject == subject))
    if user is None:
        user = User(subject=subject, email=email, display_name=name, role=role)
        db.add(user)
    else:
        user.email, user.role = email or user.email, role
        user.display_name = name or user.display_name
    db.commit()
    return user


def _local_identity(request: Request, settings: Settings) -> tuple[str, str | None, str]:
    subject = request.headers.get("X-User", "").strip() or "dev-learner"
    role = request.headers.get("X-Role", "").strip() or "learner"
    if settings.bootstrap_admin and subject == settings.bootstrap_admin:
        role = "admin"
    if role not in ROLES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unbekannte Rolle: {role}")
    return subject, (subject if "@" in subject else None), role


def role_from_claims(claims: dict, settings: Settings) -> str:
    groups = claims.get(settings.oidc_role_claim) or []
    if isinstance(groups, str):
        groups = [groups]
    roles = [settings.oidc_role_map[g] for g in groups if g in settings.oidc_role_map]
    return max(roles, key=lambda r: ROLE_RANK[r]) if roles else "learner"


def verify_token(token: str, settings: Settings, key_resolver) -> dict:
    """Prüft Signatur, Ablauf, Issuer und (falls gesetzt) Audience eines OIDC-Tokens."""
    signing_key = key_resolver(token)
    options = {"require": ["exp", "iat", "sub"]}
    return jwt.decode(token, signing_key, algorithms=["RS256", "ES256"],
                      issuer=settings.oidc_issuer, audience=settings.oidc_audience,
                      options={**options, "verify_aud": bool(settings.oidc_audience)})


def _oidc_identity(request: Request, settings: Settings) -> tuple[str, str | None, str, str | None]:
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Anmeldung erforderlich",
                            headers={"WWW-Authenticate": "Bearer"})
    resolver = request.app.state.jwk_resolver
    try:
        claims = verify_token(header.split(" ", 1)[1], settings, resolver)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Token ungültig: {exc.__class__.__name__}",
                            headers={"WWW-Authenticate": "Bearer"}) from exc
    return (claims["sub"], claims.get("email"), role_from_claims(claims, settings),
            claims.get("name") or claims.get("preferred_username"))


def _lti_identity(request: Request, settings: Settings):
    """App-Sitzungstoken aus einem LTI-Start; None, wenn kein solches Token vorliegt."""
    lti_tool = getattr(request.app.state, "lti", None)
    header = request.headers.get("Authorization", "")
    if lti_tool is None or not header.lower().startswith("bearer "):
        return None
    token = header.split(" ", 1)[1]
    if peek_issuer(token) != settings.lti_issuer:
        return None
    try:
        claims = lti_tool.verify_session(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Moodle-Sitzung abgelaufen – bitte in Moodle neu öffnen",
                            headers={"WWW-Authenticate": "Bearer"}) from exc
    if claims["role"] not in LTI_ROLES:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Rolle unzulässig")
    request.state.lti_claims = claims
    return claims["sub"], claims["role"]


def get_principal(request: Request, db: Session = Depends(get_db)) -> Principal:
    settings: Settings = request.app.state.settings
    lti_id = _lti_identity(request, settings)
    if lti_id:
        user = _upsert_user(db, lti_id[0], None, None, lti_id[1])
        return Principal(id=user.id, subject=user.subject, email=None, role=user.role)
    if settings.auth_mode == "oidc":
        subject, email, role, name = _oidc_identity(request, settings)
    else:
        subject, email, role = _local_identity(request, settings)
        name = None
    user = _upsert_user(db, subject, email, name, role)
    return Principal(id=user.id, subject=user.subject, email=user.email, role=user.role)


def require_review_role(principal: Principal = Depends(get_principal)) -> Principal:
    if not principal.can_review:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Nur für Fachreviewer, Redaktion und Admin")
    return principal
