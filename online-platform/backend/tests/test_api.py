"""API-Tests: Freigabe-Gating, Lernen, Notizen, Review-Rollen, Seed, Downloads, Startsperren."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import yaml
from sqlalchemy import select, update

from app.config import REPO_ROOT, Settings
from app.models import Card, CardVersion, UserProgress
from app.seed import run as run_seed

from .conftest import APPROVED, DRAFT, LEARNER, REVIEWER, TEACHER, as_user

# Erwartungswerte aus dem Kartenbestand ableiten, damit neue Karten die Tests nicht brechen
_CARDS = [yaml.safe_load(f.read_text(encoding="utf-8"))
          for f in sorted((REPO_ROOT / "cards/PH/metadata").glob("*.yaml"))]
N_CARDS = len(_CARDS)
N_TOXIDROME = sum(1 for c in _CARDS if c.get("card_type") == "toxidrome")


# ---------------- Startsperren ----------------

@pytest.mark.parametrize("kwargs,msg", [
    ({"env": "production", "auth_mode": "local"}, "AUTH_MODE=local"),
    ({"env": "production", "auth_mode": "oidc", "oidc_issuer": "x", "oidc_jwks_url": "y",
      "show_unreviewed": True}, "PHARMA_SHOW_UNREVIEWED"),
    ({"auth_mode": "oidc"}, "OIDC_ISSUER"),
])
def test_unsafe_configuration_refuses_to_start(kwargs, msg):
    with pytest.raises(RuntimeError, match=msg):
        Settings(**kwargs).validate()


# ---------------- Freigabe-Gating ----------------

def test_learner_sees_only_approved_cards(client):
    r = client.get("/api/cards", headers=LEARNER).json()
    assert [c["card_id"] for c in r["cards"]] == [APPROVED]
    assert client.get(f"/api/cards/{DRAFT}", headers=LEARNER).status_code == 404
    assert client.get(f"/api/cards/{DRAFT}/render", headers=LEARNER).status_code == 404
    assert client.get(f"/api/cards/{DRAFT}/download?format=html", headers=LEARNER).status_code == 404


def test_reviewer_sees_drafts_marked_as_draft(client):
    r = client.get("/api/cards", headers=REVIEWER).json()
    assert r["count"] == N_CARDS
    detail = client.get(f"/api/cards/{DRAFT}", headers=REVIEWER).json()
    assert detail["draft"] is True and detail["warning_level"] == "critical"


def test_dev_flag_shows_drafts_to_learners(make_client):
    c = make_client(show_unreviewed=True)
    assert c.get("/api/cards", headers=LEARNER).json()["count"] == N_CARDS
    assert c.get("/api/me", headers=LEARNER).json()["sees_unreviewed"] is True


def test_meta_lists_only_categories_with_visible_cards(client):
    cats = {c["slug"] for c in client.get("/api/meta", headers=LEARNER).json()["categories"]}
    assert cats == {"pharmakodynamik"}


def test_search_and_filters(client):
    hits = client.get("/api/cards", params={"q": "naloxon"}, headers=REVIEWER).json()["cards"]
    assert DRAFT in {c["card_id"] for c in hits}
    tox = client.get("/api/cards", params={"card_type": "toxidrome"}, headers=REVIEWER).json()
    assert tox["count"] == N_TOXIDROME and N_TOXIDROME > 0
    notfall = client.get("/api/cards", params={"category": "notfallmedikamente"}, headers=REVIEWER).json()
    assert DRAFT in {c["card_id"] for c in notfall["cards"]}   # über Nebenkategorie


def test_render_is_structured_html_not_image(client):
    r = client.get(f"/api/cards/{APPROVED}/render?side=back", headers=LEARNER).json()
    assert '<div class="card back' in r["html"] and "Agonist" in r["html"]
    assert r["draft"] is False
    css = client.get("/api/assets/card.css", headers=LEARNER)
    assert css.status_code == 200 and ".card" in css.text


# ---------------- Lernen ----------------

def test_rating_schedules_and_queue(client):
    q = client.get("/api/learn/queue?set=neu", headers=LEARNER).json()
    assert [c["card_id"] for c in q["cards"]] == [APPROVED]
    r = client.post(f"/api/progress/{APPROVED}", json={"rating": "good"}, headers=LEARNER).json()
    p = r["progress"]
    assert p["status"] == "learning" and p["interval_days"] == 1 and p["repetitions"] == 1
    assert client.get("/api/learn/queue?set=neu", headers=LEARNER).json()["total"] == 0
    assert client.get("/api/learn/queue?set=faellig", headers=LEARNER).json()["total"] == 0

    # Zeit vorspulen: Karte wird fällig
    app = client.app
    with app.state.sessionmaker() as db:
        db.execute(update(UserProgress).values(
            next_due_at=datetime.now(timezone.utc) - timedelta(hours=1)))
        db.commit()
    assert client.get("/api/learn/queue?set=faellig", headers=LEARNER).json()["total"] == 1
    hist = client.get(f"/api/cards/{APPROVED}/history", headers=LEARNER).json()
    assert [e["rating"] for e in hist["events"]] == ["good"]


def test_again_marks_unsure_set_and_leitner_option(client):
    client.post(f"/api/progress/{APPROVED}", json={"rating": "again"}, headers=LEARNER)
    assert client.get("/api/learn/queue?set=unsicher", headers=LEARNER).json()["total"] == 1
    r = client.post(f"/api/progress/{APPROVED}", json={"rating": "good", "algorithm": "leitner"},
                    headers=LEARNER).json()
    assert r["progress"]["leitner_box"] == 2


def test_progress_is_per_user(client):
    client.post(f"/api/progress/{APPROVED}", json={"rating": "easy"}, headers=LEARNER)
    other = as_user("andere@example.org")
    assert client.get("/api/learn/queue?set=neu", headers=other).json()["total"] == 1


def test_flags(client):
    r = client.put(f"/api/progress/{APPROVED}/flags", json={"flags": ["favorit", "pruefungsrelevant"]},
                   headers=LEARNER)
    assert r.status_code == 200 and r.json()["progress"]["flags"] == ["favorit", "pruefungsrelevant"]
    assert client.get("/api/learn/queue?set=favoriten", headers=LEARNER).json()["total"] == 1
    bad = client.put(f"/api/progress/{APPROVED}/flags", json={"flags": ["xyz"]}, headers=LEARNER)
    assert bad.status_code == 422


def test_unknown_set_and_bad_rating(client):
    assert client.get("/api/learn/queue?set=gibtsnicht", headers=LEARNER).status_code == 404
    assert client.post(f"/api/progress/{APPROVED}", json={"rating": "super"}, headers=LEARNER).status_code == 422


def test_stats(client):
    client.post(f"/api/progress/{APPROVED}", json={"rating": "easy"}, headers=LEARNER)
    s = client.get("/api/stats", headers=LEARNER).json()
    assert s["gesamt"]["gesamt"] == 1 and s["gesamt"]["beherrscht"] == 1 and s["heute_bewertet"] == 1


# ---------------- Notizen ----------------

def test_notes_crud_and_ownership(client):
    r = client.post(f"/api/cards/{APPROVED}/notes", json={
        "note_text": "Partialagonist: Buprenorphin", "annotation_data": {"shapes": [
            {"type": "arrow", "x": 0.2, "y": 0.4}]}}, headers=LEARNER)
    assert r.status_code == 201
    nid = r.json()["id"]
    assert client.put(f"/api/notes/{nid}", json={"note_text": "fremd"},
                      headers=as_user("andere@example.org")).status_code == 404
    assert client.put(f"/api/notes/{nid}", json={"note_text": "neu"}, headers=LEARNER).json()["note_text"] == "neu"
    md = client.get("/api/notes/export", headers=LEARNER)
    assert "neu" in md.text and md.headers["content-type"].startswith("text/markdown")
    assert client.delete(f"/api/notes/{nid}", headers=LEARNER).status_code == 204
    assert client.get(f"/api/cards/{APPROVED}/notes", headers=LEARNER).json()["notes"] == []


def test_course_notes_only_for_teachers(client):
    assert client.post(f"/api/cards/{APPROVED}/notes", json={"note_text": "x", "visibility": "course"},
                       headers=LEARNER).status_code == 403
    assert client.post(f"/api/cards/{APPROVED}/notes", json={"note_text": "Kurshinweis", "visibility": "course"},
                       headers=TEACHER).status_code == 201
    notes = client.get(f"/api/cards/{APPROVED}/notes", headers=LEARNER).json()["notes"]
    assert [n["note_text"] for n in notes] == ["Kurshinweis"] and notes[0]["own"] is False


# ---------------- Review ----------------

def test_review_requires_role_and_does_not_change_status(client):
    body = {"review_type": "toxicology", "status": "reviewed", "notes": "Wirkprinzip ok"}
    assert client.post(f"/api/cards/{DRAFT}/reviews", json=body, headers=LEARNER).status_code in (403, 404)
    r = client.post(f"/api/cards/{DRAFT}/reviews", json=body, headers=REVIEWER)
    assert r.status_code == 201
    assert client.get(f"/api/cards/{DRAFT}", headers=REVIEWER).json()["review_status"] == "toxicology_review_needed"
    log = client.get(f"/api/cards/{DRAFT}/reviews", headers=REVIEWER).json()["reviews"]
    assert log[0]["status"] == "reviewed" and log[0]["role"] == "reviewer_tox"
    assert client.get(f"/api/cards/{DRAFT}/versions", headers=REVIEWER).json()["versions"]


# ---------------- Seed ----------------

def test_seed_versions_and_deactivation(client, settings):
    app = client.app
    f = next(settings.cards_dir.glob(f"{APPROVED}_*.yaml"))
    data = yaml.safe_load(f.read_text(encoding="utf-8"))
    data["subtitle"] = "Geänderter Untertitel"
    data["version"] = "0.1.1"
    f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    next(settings.cards_dir.glob("ph_007_*.yaml")).unlink()
    res = run_seed(app.state.sessionmaker, settings)["cards"]
    assert (res["updated"], res["versions"], res["deactivated"]) == (1, 1, 1)
    with app.state.sessionmaker() as db:
        card = db.scalar(select(Card).where(Card.card_id == APPROVED))
        assert len(db.scalars(select(CardVersion).where(CardVersion.card_id == card.id)).all()) == 2
    assert client.get("/api/cards/ph_007", headers=REVIEWER).status_code == 404
    again = run_seed(app.state.sessionmaker, settings)["cards"]
    assert (again["updated"], again["versions"]) == (0, 0)


# ---------------- Downloads ----------------

def test_download_html_marks_drafts(client):
    ok = client.get(f"/api/cards/{APPROVED}/download?format=html", headers=LEARNER)
    assert ok.status_code == 200 and "ENTWURF" not in ok.text
    draft = client.get(f"/api/cards/{DRAFT}/download?format=html", headers=REVIEWER)
    assert "ENTWURF" in draft.text and "_ENTWURF" in draft.headers["content-disposition"]
    assert client.get(f"/api/cards/{APPROVED}/download?format=png&side=both",
                      headers=LEARNER).status_code == 422


def test_download_pdf_and_png(client):
    pytest.importorskip("playwright")
    pdf = client.get(f"/api/cards/{APPROVED}/download?format=pdf", headers=LEARNER)
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"
    png = client.get(f"/api/cards/{APPROVED}/download?format=png&side=front", headers=LEARNER)
    assert png.status_code == 200 and png.content[:8] == b"\x89PNG\r\n\x1a\n"
