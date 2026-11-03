"""Serverseitige Hilfen für die Browser-Anmeldung (OIDC Authorization Code + PKCE).

Die SPA leitet zur Anmeldung direkt zu Authentik (Navigation, keine CSP-Ausnahme nötig). Den
Code-gegen-Token-Tausch reicht die API an den Token-Endpunkt weiter. So bleibt die CSP der SPA bei
`connect-src 'self'`, und CORS-Einstellungen von Authentik spielen keine Rolle. Es gibt kein
Client-Secret (öffentlicher Client); die Bindung an den Browser leistet PKCE (code_verifier).

Netzzugriffe laufen über `urllib` mit kurzem Timeout. In Tests ersetzt man `app.state.oidc`.
"""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from .config import Settings

TIMEOUT_S = 8
DISCOVERY_TTL_S = 3600


class OidcError(RuntimeError):
    """Fehler beim Gespräch mit dem Identity Provider (ohne Details an den Browser)."""


def _http_json(url: str, data: dict | None = None) -> tuple[int, dict]:
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={"Accept": "application/json"})
    if body is not None:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as res:  # noqa: S310 (https-URL aus Konfiguration)
            return res.status, json.loads(res.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read() or b"{}")
        except ValueError:
            return exc.code, {}
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise OidcError(f"Identity Provider nicht erreichbar: {exc.__class__.__name__}") from exc


class OidcClient:
    def __init__(self, settings: Settings, http=_http_json):
        self.s = settings
        self._http = http
        self._lock = threading.Lock()
        self._disc: dict | None = None
        self._disc_at = 0.0

    def discovery(self) -> dict:
        with self._lock:
            if self._disc and time.monotonic() - self._disc_at < DISCOVERY_TTL_S:
                return self._disc
            status, doc = self._http(self.s.discovery_url)
            if status != 200 or "authorization_endpoint" not in doc or "token_endpoint" not in doc:
                raise OidcError("Discovery-Dokument unvollständig")
            if doc.get("issuer") and doc["issuer"].rstrip("/") != (self.s.oidc_issuer or "").rstrip("/"):
                raise OidcError("Issuer im Discovery-Dokument passt nicht zur Konfiguration")
            self._disc, self._disc_at = doc, time.monotonic()
            return doc

    def public_config(self) -> dict:
        d = self.discovery()
        return {
            "client_id": self.s.oidc_client_id,
            "redirect_uri": self.s.oidc_redirect_uri,
            "post_logout_redirect_uri": self.s.oidc_post_logout_uri,
            "scope": self.s.oidc_scopes,
            "authorization_endpoint": d["authorization_endpoint"],
            "end_session_endpoint": d.get("end_session_endpoint"),
        }

    def exchange(self, form: dict) -> tuple[int, dict]:
        """Code- oder Refresh-Tausch. Nur erlaubte Felder werden weitergereicht."""
        grant = form.get("grant_type")
        data = {"client_id": self.s.oidc_client_id, "grant_type": grant}
        if grant == "authorization_code":
            if form.get("redirect_uri") != self.s.oidc_redirect_uri:
                return 400, {"error": "invalid_request", "error_description": "redirect_uri"}
            for k in ("code", "code_verifier"):
                if not form.get(k):
                    return 400, {"error": "invalid_request", "error_description": k}
            data.update(code=form["code"], code_verifier=form["code_verifier"],
                        redirect_uri=self.s.oidc_redirect_uri)
        elif grant == "refresh_token":
            if not form.get("refresh_token"):
                return 400, {"error": "invalid_request", "error_description": "refresh_token"}
            data["refresh_token"] = form["refresh_token"]
        else:
            return 400, {"error": "unsupported_grant_type"}
        status, body = self._http(self.discovery()["token_endpoint"], data)
        keep = ("access_token", "id_token", "refresh_token", "expires_in", "token_type",
                "error", "error_description")
        return status, {k: v for k, v in body.items() if k in keep}
