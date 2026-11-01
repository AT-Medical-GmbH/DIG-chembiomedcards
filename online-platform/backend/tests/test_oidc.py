"""OIDC-Prüfung mit selbst erzeugtem RSA-Schlüssel (kein Netzzugriff)."""
from __future__ import annotations

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from .conftest import APPROVED

ISSUER = "https://auth.example.org/application/o/pharma-cards/"
AUD = "pharma-cards"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def token(key=KEY, **claims):
    now = int(time.time())
    payload = {"iss": ISSUER, "aud": AUD, "sub": "u-123", "email": "a@example.org",
               "iat": now, "exp": now + 300, "groups": ["pharma-learner"], **claims}
    return jwt.encode(payload, key, algorithm="RS256")


@pytest.fixture()
def oidc_client(make_client):
    return make_client(
        auth_mode="oidc", oidc_issuer=ISSUER, oidc_audience=AUD, oidc_jwks_url="https://unused",
        oidc_role_map={"pharma-learner": "learner", "pharma-reviewer-tox": "reviewer_tox",
                       "pharma-admin": "admin"},
        jwk=lambda _t: KEY.public_key())


def bearer(t):
    return {"Authorization": f"Bearer {t}"}


def test_valid_token_and_role_mapping(oidc_client):
    me = oidc_client.get("/api/me", headers=bearer(token())).json()
    assert me["role"] == "learner" and me["subject"] == "u-123"
    me = oidc_client.get("/api/me", headers=bearer(token(groups=["pharma-learner", "pharma-admin"]))).json()
    assert me["role"] == "admin"                      # höchste Rolle gewinnt
    me = oidc_client.get("/api/me", headers=bearer(token(groups=["fremd"]))).json()
    assert me["role"] == "learner"


@pytest.mark.parametrize("bad", [
    lambda: token(exp=int(time.time()) - 10),
    lambda: token(iss="https://evil.example.org/"),
    lambda: token(aud="anderes-tool"),
    lambda: token(key=OTHER_KEY),
    lambda: "kein.jwt.token",
])
def test_invalid_tokens_are_rejected(oidc_client, bad):
    assert oidc_client.get("/api/me", headers=bearer(bad())).status_code == 401


def test_header_login_is_ignored_in_oidc_mode(oidc_client):
    r = oidc_client.get("/api/cards", headers={"X-User": "admin@example.org", "X-Role": "admin"})
    assert r.status_code == 401
    assert oidc_client.get(f"/api/cards/{APPROVED}", headers=bearer(token())).status_code == 200
