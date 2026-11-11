"""Gleichzeitige Erstanfragen desselben Benutzers dürfen nicht zu HTTP 500 führen.

Vorfall 11.11.2026 (Staging): Nach der ersten Anmeldung schickt die Oberfläche mehrere API-Aufrufe
parallel. Alle sehen "Benutzer unbekannt" und legen ihn an -> UniqueViolation auf ix_users_subject.
"""
from __future__ import annotations

import threading

from sqlalchemy import func, select

from app.auth import _upsert_user
from app.models import User


def _count(sessionmaker, subject: str) -> int:
    with sessionmaker() as db:
        return db.scalar(select(func.count()).select_from(User).where(User.subject == subject))


def test_two_simultaneous_first_requests_create_one_user(make_client):
    app = make_client().app
    sm = app.state.sessionmaker
    barrier = threading.Barrier(2, timeout=10)
    results, errors = [], []

    def first_request(role: str) -> None:
        db = sm()
        real_scalar = db.scalar
        calls = {"n": 0}

        def scalar_after_barrier(*args, **kwargs):
            value = real_scalar(*args, **kwargs)
            calls["n"] += 1
            if calls["n"] == 1:          # beide Anfragen haben "nicht vorhanden" gesehen, erst dann anlegen
                barrier.wait()
            return value

        db.scalar = scalar_after_barrier
        try:
            user = _upsert_user(db, "race-sub", "race@example.org", "Race", role)
            results.append((user.id, user.subject))
        except Exception as exc:  # noqa: BLE001 - Test soll jeden Fehler sichtbar machen
            errors.append(exc)
        finally:
            db.close()

    threads = [threading.Thread(target=first_request, args=(r,)) for r in ("learner", "admin")]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert not errors, errors
    assert len(results) == 2 and results[0][0] == results[1][0]
    assert _count(sm, "race-sub") == 1


def test_conflict_keeps_existing_user_and_updates_fields(make_client):
    """Konflikt-Zweig deterministisch: erste Abfrage sieht den Benutzer nicht, er existiert aber schon."""
    app = make_client().app
    sm = app.state.sessionmaker
    with sm() as other:
        other.add(User(subject="late-sub", email="alt@example.org", display_name="Alt", role="learner"))
        other.commit()

    db = sm()
    real_scalar = db.scalar
    seen = {"n": 0}

    def scalar(*args, **kwargs):
        seen["n"] += 1
        return None if seen["n"] == 1 else real_scalar(*args, **kwargs)

    db.scalar = scalar
    try:
        user = _upsert_user(db, "late-sub", "neu@example.org", "Neu", "teacher")
        assert (user.email, user.display_name, user.role) == ("neu@example.org", "Neu", "teacher")
    finally:
        db.close()
    assert _count(sm, "late-sub") == 1
