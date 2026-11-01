"""Simulierte Moodle-Plattform (LTI 1.3) NUR für lokale E2E-Tests – http://127.0.0.1:9200.

Start: python e2e/mock_moodle.py
API dazu (lokaler Modus reicht): LTI_ENABLED=true PHARMA_PUBLIC_URL=http://127.0.0.1:8000
  LTI_KEY_FILE=<pem> LTI_PLATFORMS='[{"issuer":"http://127.0.0.1:9200","client_id":"moodle-e2e",
  "deployment_ids":["1"],"auth_login_url":"http://127.0.0.1:9200/auth","jwks_url":"http://127.0.0.1:9200/jwks"}]'

/start?role=Learner|Instructor&msg=launch|deep&set=<slug>  -> beginnt den LTI-Start wie Moodle
/received                                               -> zuletzt empfangene Deep-Linking-Antwort (JSON)
"""
import html
import json
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

BASE = "http://127.0.0.1:9200"
TOOL = "http://127.0.0.1:8000"
CLIENT = "moodle-e2e"
C = "https://purl.imsglobal.org/spec/lti/claim/"
DL = "https://purl.imsglobal.org/spec/lti-dl/claim/"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
JWK = json.loads(RSAAlgorithm.to_jwk(KEY.public_key()))
JWK.update(kid="moodle-1", use="sig", alg="RS256")
PENDING = {}       # login_hint -> Startparameter
RECEIVED = {}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8", headers=None):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        if u.path == "/jwks":
            return self._send(200, json.dumps({"keys": [JWK]}), "application/json")
        if u.path == "/received":
            return self._send(200, json.dumps(RECEIVED), "application/json")
        if u.path == "/start":
            hint = str(len(PENDING) + 1)
            PENDING[hint] = q
            loc = TOOL + "/api/lti/login?" + urllib.parse.urlencode({
                "iss": BASE, "client_id": CLIENT, "login_hint": hint, "lti_message_hint": "mh",
                "target_link_uri": TOOL + "/api/lti/launch"})
            return self._send(302, "", headers={"Location": loc})
        if u.path == "/auth":
            p = PENDING[q["login_hint"]]
            now = int(time.time())
            deep = p.get("msg") == "deep"
            claims = {"iss": BASE, "aud": CLIENT, "sub": "moodle-user-" + q["login_hint"], "iat": now,
                      "exp": now + 300, "nonce": q["nonce"], C + "version": "1.3.0", C + "deployment_id": "1",
                      C + "message_type": "LtiDeepLinkingRequest" if deep else "LtiResourceLinkRequest",
                      C + "roles": ["http://purl.imsglobal.org/vocab/lis/v2/membership#" + p.get("role", "Learner")],
                      C + "context": {"title": "Kurs Pharmakologie"},
                      C + "custom": {"set": p["set"]} if p.get("set") else {}}
            if deep:
                claims[DL + "deep_linking_settings"] = {"deep_link_return_url": BASE + "/dl-return",
                                                        "data": "ctx-77", "accept_multiple": True}
            tok = jwt.encode(claims, KEY, algorithm="RS256", headers={"kid": "moodle-1"})
            form = (f"<form id=f method=post action='{html.escape(q['redirect_uri'])}'>"
                    f"<input type=hidden name=id_token value='{tok}'>"
                    f"<input type=hidden name=state value='{html.escape(q['state'])}'></form>"
                    "<script>document.getElementById('f').submit()</script>")
            return self._send(200, form)
        self._send(404, "nicht gefunden")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        f = dict(urllib.parse.parse_qsl(self.rfile.read(n).decode()))
        if self.path == "/dl-return":
            keys = json.load(urllib.request.urlopen(TOOL + "/api/lti/jwks"))["keys"]
            pub = jwt.PyJWK(keys[0]).key
            RECEIVED.clear()
            RECEIVED.update(jwt.decode(f["JWT"], pub, algorithms=["RS256"], audience=BASE))
            return self._send(200, "<h1>Moodle: Inhalt übernommen</h1>")
        self._send(404, "")


HTTPServer(("127.0.0.1", 9200), H).serve_forever()
