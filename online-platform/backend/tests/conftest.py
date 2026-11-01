"""Testumgebung: SQLite-Datei je Test, Kartendaten als Kopie der echten Repository-Karten.

Eine Karte (ph_006) wird in der Kopie auf `approved` gesetzt, damit sich das Freigabe-Gating
prüfen lässt; alle übrigen bleiben im Review (wie im Repository).
"""
from __future__ import annotations

import shutil
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from app.config import REPO_ROOT, Settings
from app.main import create_app
from app.seed import run as run_seed

APPROVED = "ph_006"
DRAFT = "ph_100"           # Antidot Naloxon, critical, im Review


@pytest.fixture()
def cards_dir(tmp_path: Path) -> Path:
    dst = tmp_path / "cards"
    shutil.copytree(REPO_ROOT / "cards/PH/metadata", dst)
    f = next(dst.glob(f"{APPROVED}_*.yaml"))
    data = yaml.safe_load(f.read_text(encoding="utf-8"))
    data["review_status"] = "approved"
    f.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return dst


@pytest.fixture()
def settings(tmp_path: Path, cards_dir: Path) -> Settings:
    return Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", cards_dir=cards_dir)


@pytest.fixture()
def make_client(settings):
    def _make(**overrides):
        jwk = overrides.pop("jwk", None)
        s = replace(settings, **overrides)
        app = create_app(s, create_schema=True, jwk_resolver=jwk)
        run_seed(app.state.sessionmaker, s)
        return TestClient(app)
    return _make


@pytest.fixture()
def client(make_client) -> TestClient:
    return make_client()


def as_user(subject: str, role: str = "learner") -> dict:
    return {"X-User": subject, "X-Role": role}


LEARNER = as_user("lerner@example.org")
REVIEWER = as_user("reviewer@example.org", "reviewer_tox")
TEACHER = as_user("dozent@example.org", "teacher")
