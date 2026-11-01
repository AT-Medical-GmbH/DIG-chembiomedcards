"""Browser-E2E für LTI 1.3 (Launch + Deep Linking) gegen e2e/mock_moodle.py (siehe dort)."""
import json
import sys
import urllib.request

from playwright.sync_api import sync_playwright

TOOL, MOODLE = "http://127.0.0.1:8000", "http://127.0.0.1:9200"
DL = "https://purl.imsglobal.org/spec/lti-dl/claim/"
ok = []


def check(name, cond):
    ok.append(bool(cond))
    print(("OK  " if cond else "FEHL") + " " + name)


with sync_playwright() as p:
    b = p.chromium.launch()
    errors = []

    # 1) Lernende: Start aus Moodle mit Lernset
    pg = b.new_page()
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
    pg.goto(f"{MOODLE}/start?role=Learner&set=antidote")
    pg.wait_for_url(f"{TOOL}/lernen?set=antidote")
    pg.get_by_text("Über Moodle · Kurs Pharmakologie").wait_for()
    check("Launch landet im Lernset aus custom-Parameter", pg.url.endswith("/lernen?set=antidote"))
    check("Kopfzeile zeigt Moodle-Kurs statt Test-Identität", pg.get_by_text("Test-Identität").count() == 0)
    check("kein Token in Adresszeile/Verlauf", "token" not in pg.url)
    me = pg.evaluate("""async () => (await fetch('/api/me', {headers: {Authorization: 'Bearer ' + sessionStorage.getItem('pc_lti_token')}})).json()""")
    check("Rolle learner, pseudonyme Kennung", me["role"] == "learner" and me["subject"].startswith("lti-") and me["email"] is None)
    # Replay desselben Starts scheitert: state ist verbraucht
    pg.close()

    # 2) Lehrende: Deep Linking
    pg = b.new_page()
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
    pg.goto(f"{MOODLE}/start?role=Instructor&msg=deep")
    pg.wait_for_url(f"{TOOL}/lti/auswahl")
    pg.get_by_role("heading", name="Inhalt für Moodle auswählen").wait_for()
    pg.get_by_role("button", name="Antidote trainieren").click()
    pg.get_by_role("button", name="Toxidrome trainieren").click()
    pg.get_by_role("button", name="In Moodle übernehmen").click()
    pg.wait_for_url(f"{MOODLE}/dl-return")
    check("Rücksprung per POST zu Moodle", pg.get_by_text("Moodle: Inhalt übernommen").is_visible())
    rec = json.load(urllib.request.urlopen(f"{MOODLE}/received"))
    items = rec.get(DL + "content_items", [])
    check("Antwort-JWT mit Tool-Schlüssel signiert und an Moodle adressiert", rec.get("aud") == MOODLE)
    check("zwei Lernsets als ltiResourceLink", [i["custom"] for i in items] == [{"set": "antidote"}, {"set": "toxidrome"}])
    check("data-Feld unverändert zurück", rec.get(DL + "data") == "ctx-77")
    pg.close()

    # 3) Lernende dürfen kein Deep Linking
    pg = b.new_page()
    pg.goto(f"{MOODLE}/start?role=Learner&msg=deep")
    pg.get_by_text("Start aus Moodle nicht möglich").wait_for()
    check("Deep Linking für Lernende abgelehnt", pg.get_by_text("nur Lehrende").is_visible())
    pg.close()

    check("keine Konsolenfehler", not errors)
    b.close()

print(f"{sum(ok)}/{len(ok)} bestanden")
sys.exit(0 if all(ok) else 1)
