"""Minimaler OIDC-Provider NUR für lokale E2E-Tests (http://127.0.0.1:9100). Nie produktiv einsetzen.

Start: python e2e/mock_idp.py [gruppe1,gruppe2]; API mit AUTH_MODE=oidc, OIDC_ISSUER=http://127.0.0.1:9100/application/o/pharma-cards/,
OIDC_JWKS_URL=http://127.0.0.1:9100/jwks, OIDC_CLIENT_ID=OIDC_AUDIENCE=pharma-cards,
OIDC_REDIRECT_URI=http://127.0.0.1:8000/auth/callback, OIDC_ROLE_MAP=pharma-reviewer-tox:reviewer_tox
"""
import base64, hashlib, json, sys, time, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

BASE = "http://127.0.0.1:9100"
ISS = BASE + "/application/o/pharma-cards/"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
JWK = json.loads(RSAAlgorithm.to_jwk(KEY.public_key())); JWK.update(kid="k1", use="sig", alg="RS256")
CODES = {}
GROUPS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["pharma-reviewer-tox"]


def tok(nonce=None, ttl=300):
    now = int(time.time())
    c = {"iss": ISS, "aud": "pharma-cards", "sub": "andreas-e2e", "iat": now, "exp": now + ttl,
         "email": "e2e@example.org", "name": "E2E Reviewer", "groups": GROUPS}
    if nonce:
        c["nonce"] = nonce
    return jwt.encode(c, KEY, algorithm="RS256", headers={"kid": "k1"})


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = dict(urllib.parse.parse_qsl(u.query))
        if u.path == "/application/o/pharma-cards/.well-known/openid-configuration":
            return self._json(200, {"issuer": ISS, "authorization_endpoint": BASE + "/authorize",
                                    "token_endpoint": BASE + "/token", "jwks_uri": BASE + "/jwks",
                                    "end_session_endpoint": BASE + "/logout"})
        if u.path == "/jwks":
            return self._json(200, {"keys": [JWK]})
        if u.path == "/authorize":
            assert q["code_challenge_method"] == "S256" and q["response_type"] == "code"
            code = "c" + str(len(CODES))
            CODES[code] = q
            loc = q["redirect_uri"] + "?" + urllib.parse.urlencode({"code": code, "state": q["state"]})
            self.send_response(302); self.send_header("Location", loc); self.end_headers(); return
        if u.path == "/logout":
            self.send_response(302); self.send_header("Location", q.get("post_logout_redirect_uri", "/")); self.end_headers(); return
        self._json(404, {})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        f = dict(urllib.parse.parse_qsl(self.rfile.read(n).decode()))
        if self.path != "/token":
            return self._json(404, {})
        if f.get("grant_type") == "refresh_token":
            return self._json(200, {"access_token": tok(), "expires_in": 300, "token_type": "Bearer"})
        q = CODES.pop(f.get("code"), None)
        if not q:
            return self._json(400, {"error": "invalid_grant"})
        ch = base64.urlsafe_b64encode(hashlib.sha256(f["code_verifier"].encode()).digest()).rstrip(b"=").decode()
        if ch != q["code_challenge"] or f["redirect_uri"] != q["redirect_uri"]:
            return self._json(400, {"error": "invalid_grant"})
        self._json(200, {"access_token": tok(), "id_token": tok(q["nonce"]), "refresh_token": "rt",
                         "expires_in": 300, "token_type": "Bearer"})


HTTPServer(("127.0.0.1", 9100), H).serve_forever()
