"""LTI 1.3: Moodle als Plattform simuliert (eigener RSA-Schlüssel, kein Netz)."""
from __future__ import annotations

import time
from urllib.parse import parse_qs, unquote, urlparse

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.config import Settings

from .conftest import APPROVED, DRAFT

C = "https://purl.imsglobal.org/spec/lti/claim/"
DL = "https://purl.imsglobal.org/spec/lti-dl/claim/"
PUBLIC = "https://pharma.example.org"
MOODLE = {"issuer": "https://moodle.example.org", "client_id": "moodle-client-1",
          "deployment_ids": ["1"], "auth_login_url": "https://moodle.example.org/mod/lti/auth.php",
          "jwks_url": "https://moodle.example.org/mod/lti/certs.php"}
PLATFORM_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
INSTRUCTOR = "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor"
LEARNER = "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner"


@pytest.fixture()
def tool_key(tmp_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    f = tmp_path / "lti.pem"
    f.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                    serialization.NoEncryption()))
    return f


@pytest.fixture()
def lti(make_client, tool_key):
    return make_client(public_url=PUBLIC, lti_enabled=True, lti_platforms=(MOODLE,), lti_key_file=tool_key,
                       lti_keys=lambda _p, _t: PLATFORM_KEY.public_key())


def start(client, **extra):
    r = client.get("/api/lti/login", params={"iss": MOODLE["issuer"], "client_id": MOODLE["client_id"],
                                             "login_hint": "42", "lti_message_hint": "m",
                                             "target_link_uri": f"{PUBLIC}/api/lti/launch", **extra},
                   follow_redirects=False)
    assert r.status_code == 302, r.text
    q = {k: v[0] for k, v in parse_qs(urlparse(r.headers["location"]).query).items()}
    return q


def id_token(q, key=PLATFORM_KEY, roles=(LEARNER,), msg="LtiResourceLinkRequest", custom=None, **over):
    now = int(time.time())
    c = {"iss": MOODLE["issuer"], "aud": MOODLE["client_id"], "sub": "moodle-user-7", "iat": now,
         "exp": now + 300, "nonce": q["nonce"], C + "version": "1.3.0", C + "deployment_id": "1",
         C + "message_type": msg, C + "roles": list(roles), C + "context": {"title": "Pharmakologie Kurs"},
         C + "custom": custom or {}, "name": "Klarname Darf Nicht Gespeichert Werden"}
    if msg == "LtiDeepLinkingRequest":
        c[DL + "deep_linking_settings"] = {"deep_link_return_url": "https://moodle.example.org/mod/lti/contentitem_return.php",
                                           "data": "opaque-123", "accept_multiple": True}
    c.update(over)
    return jwt.encode(c, key, algorithm="RS256")


def launch(client, q, token):
    return client.post("/api/lti/launch", data={"id_token": token, "state": q["state"]}, follow_redirects=False)


def session_from(resp):
    frag = dict(p.split("=", 1) for p in urlparse(resp.headers["location"]).fragment.split("&"))
    return unquote(frag["token"]), unquote(frag["next"])


def test_disabled_by_default(client):
    assert client.get("/api/lti/jwks").status_code == 404


def test_login_redirect_parameters(lti):
    q = start(lti)
    assert q["response_type"] == "id_token" and q["response_mode"] == "form_post" and q["prompt"] == "none"
    assert q["redirect_uri"] == f"{PUBLIC}/api/lti/launch" and q["client_id"] == MOODLE["client_id"]
    assert q["login_hint"] == "42" and q["lti_message_hint"] == "m" and q["state"] and q["nonce"]


@pytest.mark.parametrize("extra", [{"iss": "https://evil.example.org"}, {"target_link_uri": "https://evil.example.org/x"},
                                   {"client_id": "fremd"}])
def test_login_rejects_unknown_platform_or_target(lti, extra):
    r = lti.get("/api/lti/login", params={"iss": MOODLE["issuer"], "login_hint": "1", **extra}, follow_redirects=False)
    assert r.status_code == 400


def test_learner_launch_sets_session_and_target(lti):
    q = start(lti)
    r = launch(lti, q, id_token(q, custom={"set": "antidote"}))
    assert r.status_code == 303 and r.headers["location"].startswith("/lti/start#token=")
    tok, nxt = session_from(r)
    assert nxt == "/lernen?set=antidote"
    me = lti.get("/api/me", headers={"Authorization": f"Bearer {tok}"}).json()
    assert me["role"] == "learner" and me["subject"].startswith("lti-") and me["email"] is None
    # Lernende über LTI sehen nur Freigegebenes
    h = {"Authorization": f"Bearer {tok}"}
    assert lti.get(f"/api/cards/{APPROVED}", headers=h).status_code == 200
    assert lti.get(f"/api/cards/{DRAFT}", headers=h).status_code == 404


def test_no_personal_data_stored(lti):
    q = start(lti)
    launch(lti, q, id_token(q))
    from app.models import User
    with lti.app.state.sessionmaker() as db:
        users = db.query(User).all()
    assert all(u.display_name is None and u.email is None for u in users)
    assert not any("moodle-user-7" in u.subject for u in users)


def test_instructor_is_teacher_never_admin(lti):
    q = start(lti)
    roles = (INSTRUCTOR, "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator")
    tok, _ = session_from(launch(lti, q, id_token(q, roles=roles)))
    me = lti.get("/api/me", headers={"Authorization": f"Bearer {tok}"}).json()
    assert me["role"] == "teacher" and me["can_review"] is False


@pytest.mark.parametrize("bad", [
    {"key": OTHER_KEY},
    {"aud": "anderer-client"},
    {"iss": "https://evil.example.org"},
    {"nonce": "falsch"},
    {C + "deployment_id": "99"},
    {C + "version": "1.1"},
    {"msg": "LtiSubmissionReviewRequest"},
    {"exp": int(time.time()) - 120},
])
def test_launch_rejections(lti, bad):
    q = start(lti)
    bad = dict(bad)
    key = bad.pop("key", PLATFORM_KEY)
    msg = bad.pop("msg", "LtiResourceLinkRequest")
    r = launch(lti, q, id_token(q, key=key, msg=msg, **bad))
    assert r.status_code == 400 and "Start aus Moodle nicht möglich" in r.text


def test_state_is_single_use(lti):
    q = start(lti)
    t = id_token(q)
    assert launch(lti, q, t).status_code == 303
    assert launch(lti, q, t).status_code == 400          # Replay


def test_custom_target_is_sanitised(lti):
    q = start(lti)
    _, nxt = session_from(launch(lti, q, id_token(q, custom={"set": "../../admin", "card": "javascript:x"})))
    assert nxt == "/"
    q = start(lti)
    _, nxt = session_from(launch(lti, q, id_token(q, custom={"card": APPROVED})))
    assert nxt == f"/karten/{APPROVED}"


def test_deep_linking_flow(lti):
    q = start(lti)
    r = launch(lti, q, id_token(q, roles=(INSTRUCTOR,), msg="LtiDeepLinkingRequest"))
    tok, nxt = session_from(r)
    assert nxt == "/lti/auswahl"
    h = {"Authorization": f"Bearer {tok}"}
    res = lti.post("/api/lti/deep-link", headers=h,
                   json={"items": [{"type": "set", "id": "antidote"}, {"type": "card", "id": APPROVED}]})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["return_url"].startswith("https://moodle.example.org/")
    tool_pub = jwt.PyJWK(lti.get("/api/lti/jwks").json()["keys"][0]).key
    c = jwt.decode(body["jwt"], tool_pub, algorithms=["RS256"], audience=MOODLE["issuer"])
    assert c["iss"] == MOODLE["client_id"] and c[C + "message_type"] == "LtiDeepLinkingResponse"
    assert c[C + "deployment_id"] == "1" and c[DL + "data"] == "opaque-123"
    items = c[DL + "content_items"]
    assert [i["custom"] for i in items] == [{"set": "antidote"}, {"card": APPROVED}]
    assert all(i["type"] == "ltiResourceLink" and i["url"] == f"{PUBLIC}/api/lti/launch" for i in items)


def test_deep_linking_restrictions(lti):
    q = start(lti)
    assert launch(lti, q, id_token(q, roles=(LEARNER,), msg="LtiDeepLinkingRequest")).status_code == 400
    q = start(lti)
    tok, _ = session_from(launch(lti, q, id_token(q, roles=(INSTRUCTOR,), msg="LtiDeepLinkingRequest")))
    h = {"Authorization": f"Bearer {tok}"}
    # Entwürfe sind auch für Lehrende nicht verlinkbar
    assert lti.post("/api/lti/deep-link", headers=h, json={"items": [{"type": "card", "id": DRAFT}]}).status_code == 404
    assert lti.post("/api/lti/deep-link", headers=h, json={"items": [{"type": "set", "id": "gibtsnicht"}]}).status_code == 404
    # normale Lernsitzung darf keine Deep-Link-Antwort erzeugen
    q = start(lti)
    tok2, _ = session_from(launch(lti, q, id_token(q, roles=(INSTRUCTOR,))))
    r = lti.post("/api/lti/deep-link", headers={"Authorization": f"Bearer {tok2}"},
                 json={"items": [{"type": "set", "id": "antidote"}]})
    assert r.status_code == 403


def test_forged_session_token_rejected(lti):
    now = int(time.time())
    forged = jwt.encode({"iss": f"{PUBLIC}/lti", "aud": "pharma-cards-app", "sub": "x", "role": "teacher",
                         "iat": now, "exp": now + 60}, OTHER_KEY, algorithm="RS256")
    assert lti.get("/api/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


def test_lti_configuration_is_enforced(tool_key):
    base = {"lti_enabled": True, "public_url": PUBLIC, "lti_key_file": tool_key, "lti_platforms": (MOODLE,)}
    Settings(**base).validate()
    for over, msg in [({"public_url": None}, "PHARMA_PUBLIC_URL"), ({"lti_key_file": None}, "LTI_KEY_FILE"),
                      ({"lti_platforms": ()}, "LTI_PLATFORMS"),
                      ({"lti_platforms": ({"issuer": "x"},)}, "unvollständig"),
                      ({"env": "production", "auth_mode": "oidc", "oidc_issuer": "i", "oidc_jwks_url": "j",
                        "oidc_client_id": "c", "oidc_redirect_uri": "https://p/auth/callback",
                        "public_url": "http://pharma.example.org"}, "https")]:
        with pytest.raises(RuntimeError, match=msg):
            Settings(**{**base, **over}).validate()
