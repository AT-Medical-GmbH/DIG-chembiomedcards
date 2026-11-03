"""Browser-E2E der OIDC/PKCE-Anmeldung gegen e2e/mock_idp.py (API auf :8000 im OIDC-Modus, siehe dort)."""
import sys
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8000"
ok = []


def check(name, cond):
    ok.append(bool(cond))
    print(("OK  " if cond else "FEHL") + " " + name)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
    pg.goto(URL + "/karten?q=nalox")
    pg.get_by_role("button", name="Mit AT-Medical-Konto anmelden").wait_for()
    check("ohne Token: Anmeldeseite statt Daten", pg.get_by_role("heading", name="Anmeldung").is_visible())
    pg.get_by_role("button", name="Mit AT-Medical-Konto anmelden").click()
    pg.wait_for_url(URL + "/karten?q=nalox")
    pg.get_by_text("E2E Reviewer").wait_for()
    check("Rücksprung auf ursprüngliche Seite inkl. Query", pg.url == URL + "/karten?q=nalox")
    check("Name aus id_token im Kopf", pg.get_by_text("E2E Reviewer").is_visible())
    check("kein Code/State in der Adresszeile", "code=" not in pg.url)
    stored = pg.evaluate("() => [sessionStorage.getItem('pc_oidc_tokens') !== null, localStorage.getItem('pc_oidc_tokens')]")
    check("Tokens nur in sessionStorage", stored == [True, None])
    me = pg.evaluate("""async () => { const t = JSON.parse(sessionStorage.getItem('pc_oidc_tokens'));
        const r = await fetch('/api/me', {headers: {Authorization: 'Bearer ' + t.access_token}}); return r.json(); }""")
    check("API erkennt Rolle aus Gruppen-Claim (reviewer_tox)", me.get("role") == "reviewer_tox")
    # abgelaufenes Access-Token -> Refresh über /api/auth/token
    pg.evaluate("""() => { const t = JSON.parse(sessionStorage.getItem('pc_oidc_tokens')); t.expires_at = Date.now() - 1000;
        sessionStorage.setItem('pc_oidc_tokens', JSON.stringify(t)); }""")
    pg.goto(URL + "/")
    pg.get_by_role("heading", name="Übersicht").wait_for()
    exp = pg.evaluate("() => JSON.parse(sessionStorage.getItem('pc_oidc_tokens')).expires_at > Date.now()")
    check("Refresh-Token erneuert abgelaufenes Access-Token", exp)
    # manipulierter state wird abgewiesen
    pg2 = b.new_page()
    pg2.goto(URL + "/auth/callback?code=x&state=falsch")
    pg2.get_by_text("Anmeldung nicht abgeschlossen").wait_for()
    check("Callback mit fremdem state abgewiesen", pg2.get_by_text("state").is_visible())
    pg2.close()
    # Abmelden
    pg.get_by_role("button", name="Abmelden").click()
    pg.get_by_role("button", name="Mit AT-Medical-Konto anmelden").wait_for()
    check("Abmelden löscht Tokens", pg.evaluate("() => sessionStorage.getItem('pc_oidc_tokens')") is None)
    check("keine Konsolenfehler außer erwarteten 401", all("401" in e for e in errors))
    b.close()

print(f"{sum(ok)}/{len(ok)} bestanden")
sys.exit(0 if all(ok) else 1)
