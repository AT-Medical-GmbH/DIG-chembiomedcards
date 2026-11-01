"""Browser-Anmeldung: Konfiguration, Token-Tausch über die API (IdP simuliert, kein Netz)."""
from __future__ import annotations

import pytest

from app.config import Settings
from app.oidc_client import OidcClient, OidcError

ISSUER = "https://auth.example.org/application/o/pharma-cards/"
REDIRECT = "https://pharma.example.org/auth/callback"
DISCOVERY = {
    "issuer": ISSUER,
    "authorization_endpoint": "https://auth.example.org/application/o/authorize/",
    "token_endpoint": "https://auth.example.org/application/o/token/",
    "end_session_endpoint": "https://auth.example.org/application/o/pharma-cards/end-session/",
}


class FakeIdP:
    def __init__(self, discovery=DISCOVERY, token_status=200):
        self.discovery, self.token_status, self.calls = discovery, token_status, []

    def __call__(self, url, data=None):
        self.calls.append((url, data))
        if url.endswith("/.well-known/openid-configuration"):
            return 200, self.discovery
        if url == DISCOVERY["token_endpoint"]:
            if self.token_status != 200:
                return self.token_status, {"error": "invalid_grant", "error_description": "intern"}
            return 200, {"access_token": "AT", "id_token": "IT", "refresh_token": "RT",
                         "expires_in": 300, "token_type": "Bearer", "scope": "openid", "extra": "x"}
        raise AssertionError(url)


@pytest.fixture()
def idp():
    return FakeIdP()


@pytest.fixture()
def oidc_app(make_client, idp):
    return make_client(auth_mode="oidc", oidc_issuer=ISSUER, oidc_jwks_url="https://unused",
                       oidc_client_id="pharma-cards", oidc_redirect_uri=REDIRECT,
                       oidc_post_logout_uri="https://pharma.example.org/",
                       jwk=lambda _t: None, oidc=lambda s: OidcClient(s, http=idp))


def test_config_local_mode(client):
    assert client.get("/api/auth/config").json() == {"mode": "local"}
    assert client.post("/api/auth/token", json={"grant_type": "refresh_token"}).status_code == 404


def test_config_oidc_exposes_only_public_values(oidc_app):
    c = oidc_app.get("/api/auth/config").json()
    assert c["mode"] == "oidc" and c["client_id"] == "pharma-cards"
    assert c["authorization_endpoint"] == DISCOVERY["authorization_endpoint"]
    assert c["redirect_uri"] == REDIRECT and "offline_access" in c["scope"]
    assert "token_endpoint" not in c                 # Tausch läuft nur über die API


def test_code_exchange_forwards_pkce_and_filters_response(oidc_app, idp):
    r = oidc_app.post("/api/auth/token", json={"grant_type": "authorization_code", "code": "C",
                                               "code_verifier": "V" * 43, "redirect_uri": REDIRECT})
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store"
    assert set(r.json()) == {"access_token", "id_token", "refresh_token", "expires_in", "token_type"}
    url, data = idp.calls[-1]
    assert url == DISCOVERY["token_endpoint"]
    assert data == {"client_id": "pharma-cards", "grant_type": "authorization_code", "code": "C",
                    "code_verifier": "V" * 43, "redirect_uri": REDIRECT}


@pytest.mark.parametrize("body", [
    {"grant_type": "authorization_code", "code": "C", "code_verifier": "V", "redirect_uri": "https://evil.example/cb"},
    {"grant_type": "authorization_code", "code": "C", "redirect_uri": REDIRECT},          # ohne PKCE
    {"grant_type": "client_credentials"},
    {"grant_type": "refresh_token"},
])
def test_token_request_rejected_before_idp(oidc_app, idp, body):
    n = len(idp.calls)
    assert oidc_app.post("/api/auth/token", json=body).status_code == 400
    assert all(not u.endswith("/token/") for u, _ in idp.calls[n:])


def test_idp_error_is_not_leaked(make_client):
    idp = FakeIdP(token_status=400)
    c = make_client(auth_mode="oidc", oidc_issuer=ISSUER, oidc_jwks_url="https://unused",
                    oidc_client_id="pharma-cards", oidc_redirect_uri=REDIRECT,
                    jwk=lambda _t: None, oidc=lambda s: OidcClient(s, http=idp))
    r = c.post("/api/auth/token", json={"grant_type": "refresh_token", "refresh_token": "RT"})
    assert r.status_code == 400 and r.json() == {"error": "invalid_grant"}


def test_discovery_issuer_mismatch_is_refused():
    s = Settings(auth_mode="oidc", oidc_issuer=ISSUER, oidc_jwks_url="x", oidc_client_id="c",
                 oidc_redirect_uri=REDIRECT)
    bad = FakeIdP(discovery={**DISCOVERY, "issuer": "https://evil.example.org/"})
    with pytest.raises(OidcError):
        OidcClient(s, http=bad).discovery()


@pytest.mark.parametrize("kwargs,msg", [
    ({"auth_mode": "oidc", "oidc_issuer": "x", "oidc_jwks_url": "y"}, "OIDC_CLIENT_ID"),
    ({"env": "production", "auth_mode": "oidc", "oidc_issuer": "x", "oidc_jwks_url": "y",
      "oidc_client_id": "c", "oidc_redirect_uri": "http://pharma.example.org/auth/callback"}, "https"),
])
def test_login_configuration_is_enforced(kwargs, msg):
    with pytest.raises(RuntimeError, match=msg):
        Settings(**kwargs).validate()
