"""LTI 1.3 (IMS LTI Core 1.3 + Deep Linking 2.0) – Werkzeugseite für Moodle.

Ablauf
1. Moodle ruft `/api/lti/login` (Third-Party-Initiated Login). Wir legen state + nonce einmalig in
   der Datenbank ab (keine Cookies, damit es auch im Moodle-iframe funktioniert) und leiten zur
   Autorisierung der Plattform (`response_mode=form_post`, `prompt=none`).
2. Moodle postet das signierte `id_token` an `/api/lti/launch`. Wir prüfen Signatur (JWKS der
   Plattform), Issuer, Audience (= unsere client_id), Ablauf, nonce, Deployment, Version und
   Nachrichtentyp. Der state wird dabei verbraucht (Replay-Schutz).
3. Wir stellen ein kurzlebiges App-Sitzungstoken (RS256, eigener Tool-Schlüssel) aus und leiten in die
   SPA (`/lti/start#token=…`). Das Fragment erreicht keinen Server und kein Log.

Rollen: Moodle-Lehrende (Instructor, ContentDeveloper, Administrator) -> `teacher`, sonst `learner`.
Über LTI werden nie Review-, Redaktions- oder Admin-Rechte vergeben.

Datensparsamkeit: Vom Launch speichern wir nur eine pseudonyme Kennung (Plattform + sub), keine
Namen oder E-Mail-Adressen.
"""
from __future__ import annotations

import hashlib
import re
import secrets
import time
from datetime import timedelta
from functools import cached_property
from pathlib import Path
from urllib.parse import urlencode

import jwt
from cryptography.hazmat.primitives import serialization
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .config import Settings
from .models import LtiLaunchState, utcnow

C = "https://purl.imsglobal.org/spec/lti/claim/"
DL = "https://purl.imsglobal.org/spec/lti-dl/claim/"
MSG_LAUNCH = "LtiResourceLinkRequest"
MSG_DEEP = "LtiDeepLinkingRequest"
STATE_TTL = timedelta(minutes=10)
TEACHER_ROLES = ("#Instructor", "#ContentDeveloper", "#Administrator", "#TeachingAssistant")
SET_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
CARD_RE = re.compile(r"^[a-z]{2}_\d{3}$")
APP_AUDIENCE = "pharma-cards-app"


class LtiError(Exception):
    """Launch abgelehnt; die Meldung ist für Lehrende/Admins verständlich und enthält keine Tokens."""


class LtiTool:
    def __init__(self, settings: Settings, platform_key_resolver=None):
        self.s = settings
        self._resolver = platform_key_resolver
        self._jwk_clients: dict[str, jwt.PyJWKClient] = {}

    # ---------- Schlüssel ----------
    @cached_property
    def private_key(self):
        return serialization.load_pem_private_key(Path(self.s.lti_key_file).read_bytes(), password=None)

    def jwks(self) -> dict:
        jwk = RSAAlgorithm.to_jwk(self.private_key.public_key(), as_dict=True)
        jwk.update(kid=self.s.lti_kid, use="sig", alg="RS256")
        return {"keys": [jwk]}

    def _platform_key(self, platform: dict, token: str):
        if self._resolver:
            return self._resolver(platform, token)
        client = self._jwk_clients.setdefault(
            platform["jwks_url"], jwt.PyJWKClient(platform["jwks_url"], cache_keys=True, lifespan=3600))
        return client.get_signing_key_from_jwt(token).key

    # ---------- Plattformen ----------
    def platform(self, issuer: str | None, client_id: str | None = None) -> dict:
        for p in self.s.lti_platforms:
            if p["issuer"] == issuer and (client_id is None or p["client_id"] == client_id):
                return p
        raise LtiError("Unbekannte LTI-Plattform (issuer/client_id nicht registriert)")

    @property
    def launch_url(self) -> str:
        return f"{self.s.public_url}/api/lti/launch"

    # ---------- 1. Login-Init ----------
    def login_redirect(self, db: Session, params: dict) -> str:
        platform = self.platform(params.get("iss"), params.get("client_id"))
        if not params.get("login_hint"):
            raise LtiError("login_hint fehlt")
        target = params.get("target_link_uri") or ""
        if target and not target.startswith(f"{self.s.public_url}/"):
            raise LtiError("target_link_uri gehört nicht zu diesem Tool")
        db.execute(delete(LtiLaunchState).where(LtiLaunchState.created_at < utcnow() - STATE_TTL))
        st = LtiLaunchState(state=secrets.token_urlsafe(32), nonce=secrets.token_urlsafe(32),
                            issuer=platform["issuer"], client_id=platform["client_id"])
        db.add(st)
        db.commit()
        q = {"scope": "openid", "response_type": "id_token", "response_mode": "form_post",
             "prompt": "none", "client_id": platform["client_id"], "redirect_uri": self.launch_url,
             "login_hint": params["login_hint"], "state": st.state, "nonce": st.nonce}
        if params.get("lti_message_hint"):
            q["lti_message_hint"] = params["lti_message_hint"]
        return f"{platform['auth_login_url']}?{urlencode(q)}"

    # ---------- 2. Launch ----------
    def validate_launch(self, db: Session, id_token: str, state: str) -> dict:
        st = db.get(LtiLaunchState, state or "")
        if st is None:
            raise LtiError("Start ungültig oder bereits verwendet (state). Bitte in Moodle erneut öffnen.")
        db.delete(st)                      # einmalig, auch wenn die Prüfung danach scheitert
        db.commit()
        created = st.created_at if st.created_at.tzinfo else st.created_at.replace(tzinfo=utcnow().tzinfo)
        if utcnow() - created > STATE_TTL:
            raise LtiError("Start abgelaufen. Bitte in Moodle erneut öffnen.")
        platform = self.platform(st.issuer, st.client_id)
        try:
            claims = jwt.decode(id_token, self._platform_key(platform, id_token), algorithms=["RS256"],
                                audience=platform["client_id"], issuer=platform["issuer"],
                                options={"require": ["exp", "iat", "sub", "nonce"]}, leeway=30)
        except jwt.PyJWTError as exc:
            raise LtiError(f"id_token ungültig ({exc.__class__.__name__})") from exc
        if claims["nonce"] != st.nonce:
            raise LtiError("nonce passt nicht")
        azp = claims.get("azp")
        if isinstance(claims.get("aud"), list) and len(claims["aud"]) > 1 and azp != platform["client_id"]:
            raise LtiError("azp passt nicht")
        if claims.get(C + "version") != "1.3.0":
            raise LtiError("Nur LTI 1.3.0 wird unterstützt")
        if claims.get(C + "deployment_id") not in platform["deployment_ids"]:
            raise LtiError("Deployment ist nicht freigeschaltet")
        if claims.get(C + "message_type") not in (MSG_LAUNCH, MSG_DEEP):
            raise LtiError("Nachrichtentyp wird nicht unterstützt")
        claims["_platform"] = platform
        return claims

    @staticmethod
    def role(claims: dict) -> str:
        roles = claims.get(C + "roles") or []
        return "teacher" if any(r.endswith(TEACHER_ROLES) for r in roles) else "learner"

    @staticmethod
    def subject(claims: dict) -> str:
        """Pseudonyme, stabile Kennung je Plattform-Nutzer (keine personenbezogenen Klartexte)."""
        digest = hashlib.sha256(f"{claims['iss']}|{claims['sub']}".encode()).hexdigest()[:32]
        return f"lti-{digest}"

    @staticmethod
    def target(claims: dict) -> str:
        custom = claims.get(C + "custom") or {}
        card, set_ = str(custom.get("card", "")).strip(), str(custom.get("set", "")).strip()
        if CARD_RE.match(card):
            return f"/karten/{card}"
        if SET_RE.match(set_):
            return f"/lernen?set={set_}"
        return "/"

    # ---------- 3. App-Sitzung ----------
    def session_token(self, claims: dict) -> str:
        now = int(time.time())
        payload = {"iss": self.s.lti_issuer, "aud": APP_AUDIENCE, "sub": self.subject(claims),
                   "role": self.role(claims), "iat": now, "exp": now + self.s.lti_session_hours * 3600,
                   "ctx": (claims.get(C + "context") or {}).get("title")}
        if claims.get(C + "message_type") == MSG_DEEP:
            dls = claims.get(DL + "deep_linking_settings") or {}
            if not dls.get("deep_link_return_url"):
                raise LtiError("deep_link_return_url fehlt")
            payload["exp"] = now + 1800
            payload["dl"] = {"return_url": dls["deep_link_return_url"], "data": dls.get("data"),
                             "deployment_id": claims[C + "deployment_id"],
                             "platform": claims["_platform"]["issuer"],
                             "client_id": claims["_platform"]["client_id"],
                             "multiple": bool(dls.get("accept_multiple", True))}
        return jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": self.s.lti_kid})

    def verify_session(self, token: str) -> dict:
        return jwt.decode(token, self.private_key.public_key(), algorithms=["RS256"],
                          audience=APP_AUDIENCE, issuer=self.s.lti_issuer,
                          options={"require": ["exp", "iat", "sub", "role"]})

    # ---------- Deep Linking ----------
    def deep_link_response(self, dl: dict, items: list[dict]) -> str:
        now = int(time.time())
        payload = {"iss": dl["client_id"], "aud": dl["platform"], "iat": now, "exp": now + 300,
                   "nonce": secrets.token_urlsafe(16),
                   C + "message_type": "LtiDeepLinkingResponse", C + "version": "1.3.0",
                   C + "deployment_id": dl["deployment_id"],
                   DL + "content_items": items}
        if dl.get("data") is not None:
            payload[DL + "data"] = dl["data"]
        return jwt.encode(payload, self.private_key, algorithm="RS256", headers={"kid": self.s.lti_kid})

    def content_item(self, title: str, custom: dict) -> dict:
        return {"type": "ltiResourceLink", "title": title[:200], "url": self.launch_url, "custom": custom}


def peek_issuer(token: str) -> str | None:
    """Issuer ohne Prüfung lesen – nur um die passende Prüfung auszuwählen."""
    try:
        return jwt.decode(token, options={"verify_signature": False}).get("iss")
    except jwt.PyJWTError:
        return None
