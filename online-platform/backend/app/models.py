"""Relationales Datenmodell der Online-Plattform (docs/pharma-cards/02_datenmodell.md §3).

Kartendaten werden aus cards/PH/metadata geseedet (reproduzierbar). Nutzer-, Fortschritts-,
Notiz- und Reviewdaten entstehen nur hier und sind der schützenswerte Teil (Backup).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table,
                        Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base, JSONType


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


card_tags = Table(
    "card_tags", Base.metadata,
    Column("card_id", ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

card_secondary_categories = Table(
    "card_secondary_categories", Base.metadata,
    Column("card_id", ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    color: Mapped[str | None] = mapped_column(String(16))
    icon: Mapped[str | None] = mapped_column(String(64))
    sort_order: Mapped[int] = mapped_column(Integer, default=1000)
    release: Mapped[str | None] = mapped_column(String(8))


class DrugClass(Base):
    __tablename__ = "drug_classes"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("drug_classes.id"))
    color: Mapped[str | None] = mapped_column(String(16))
    icon: Mapped[str | None] = mapped_column(String(64))


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))


class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[str | None] = mapped_column(String(300))
    substance_name: Mapped[str | None] = mapped_column(String(200))
    card_type: Mapped[str] = mapped_column(String(32))
    front_type: Mapped[str] = mapped_column(String(32))
    level: Mapped[str | None] = mapped_column(String(32))
    difficulty: Mapped[str | None] = mapped_column(String(32))
    warning_level: Mapped[str] = mapped_column(String(16), index=True)
    review_status: Mapped[str] = mapped_column(String(32), index=True)
    version: Mapped[str] = mapped_column(String(16))
    primary_category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    drug_class_id: Mapped[int | None] = mapped_column(ForeignKey("drug_classes.id"))
    front_content: Mapped[dict] = mapped_column(JSONType, default=dict)
    back_sections: Mapped[list] = mapped_column(JSONType, default=list)
    content: Mapped[dict] = mapped_column(JSONType, default=dict)      # vollständiger Datensatz
    search_text: Mapped[str] = mapped_column(Text, default="")
    content_hash: Mapped[str] = mapped_column(String(64))
    qr_url: Mapped[str | None] = mapped_column(String(300))
    lms_url: Mapped[str | None] = mapped_column(String(300))
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow,
                                                 onupdate=utcnow)

    primary_category: Mapped[Category | None] = relationship()
    drug_class: Mapped[DrugClass | None] = relationship()
    secondary_categories: Mapped[list[Category]] = relationship(secondary=card_secondary_categories)
    tags: Mapped[list[Tag]] = relationship(secondary=card_tags)


class CardVersion(Base):
    """Änderungsverlauf: Snapshot je inhaltlicher Änderung (Pflicht für klinische Karten)."""
    __tablename__ = "card_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    version: Mapped[str] = mapped_column(String(16))
    content_hash: Mapped[str] = mapped_column(String(64))
    content_snapshot: Mapped[dict] = mapped_column(JSONType)
    changed_by: Mapped[str] = mapped_column(String(200))
    change_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # OIDC sub / lokal
    email: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="learner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (UniqueConstraint("user_id", "card_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="new")
    flags: Mapped[list] = mapped_column(JSONType, default=list)  # favorit, klinisch_wichtig, ...
    leitner_box: Mapped[int] = mapped_column(Integer, default=1)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[int] = mapped_column(Integer, default=0)
    repetitions: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)
    next_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_rating: Mapped[str | None] = mapped_column(String(16))


class StudyEvent(Base):
    """Lernhistorie pro Karte (eine Zeile je Bewertung)."""
    __tablename__ = "study_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    rating: Mapped[str] = mapped_column(String(16))
    algorithm: Mapped[str] = mapped_column(String(16))
    interval_days: Mapped[int] = mapped_column(Integer)
    leitner_box: Mapped[int] = mapped_column(Integer)
    ease_factor: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class UserNote(Base):
    __tablename__ = "user_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    note_text: Mapped[str] = mapped_column(Text, default="")
    annotation_data: Mapped[dict | None] = mapped_column(JSONType)  # Overlay, nie ins Bild
    visibility: Mapped[str] = mapped_column(String(16), default="private")  # private | course
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow,
                                                 onupdate=utcnow)


class ReviewEvent(Base):
    """Protokoll fachlicher Prüfungen. Der verbindliche Status steht in den YAML-Daten (Git)."""
    __tablename__ = "review_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    review_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32))
    card_version: Mapped[str] = mapped_column(String(16))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ExportLog(Base):
    __tablename__ = "exports"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    card_id: Mapped[int | None] = mapped_column(ForeignKey("cards.id", ondelete="SET NULL"))
    type: Mapped[str] = mapped_column(String(32))       # card_download | notes_export
    format: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LtiLaunchState(Base):
    """Einmaliger state/nonce zwischen LTI-Login-Start und Launch (ohne Cookies, iframe-tauglich)."""
    __tablename__ = "lti_launch_states"
    state: Mapped[str] = mapped_column(String(64), primary_key=True)
    nonce: Mapped[str] = mapped_column(String(64))
    issuer: Mapped[str] = mapped_column(String(255))
    client_id: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
