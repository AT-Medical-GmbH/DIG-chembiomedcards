"""Wiederholungslogik: SM-2 (Standard) und Leitner-Box-System (wählbar).

Reine Funktionen ohne Datenbankbezug, damit sie isoliert getestet werden können.
Bewertungen der Lernoberfläche:
    again (Wiederholen) · hard (Unsicher) · good (Gelernt) · easy (Beherrscht)
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

RATINGS = ("again", "hard", "good", "easy")
SM2_QUALITY = {"again": 1, "hard": 3, "good": 4, "easy": 5}
LEITNER_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}   # Tage je Fach
MIN_EASE = 1.3
STATUS_BY_RATING = {"again": "repeat", "hard": "unsure", "good": "learning", "easy": "mastered"}


@dataclass(frozen=True)
class SrsState:
    ease_factor: float = 2.5
    interval_days: int = 0
    repetitions: int = 0
    leitner_box: int = 1
    lapses: int = 0


def sm2(state: SrsState, rating: str) -> SrsState:
    """SuperMemo-2: Qualität < 3 setzt zurück; der Leichtigkeitsfaktor fällt nie unter 1,3."""
    q = SM2_QUALITY[rating]
    if q < 3:
        reps, interval, lapses = 0, 1, state.lapses + 1
    else:
        reps = state.repetitions + 1
        if state.repetitions == 0:
            interval = 1
        elif state.repetitions == 1:
            interval = 6
        else:
            interval = max(1, round(state.interval_days * state.ease_factor))
        lapses = state.lapses
    ease = state.ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    return replace(state, ease_factor=max(MIN_EASE, round(ease, 4)), interval_days=interval,
                   repetitions=reps, lapses=lapses)


def leitner(state: SrsState, rating: str) -> SrsState:
    """Leitner: richtig -> nächstes Fach (max. 5), falsch -> Fach 1; „Unsicher“ bleibt im Fach."""
    if rating == "again":
        box, lapses = 1, state.lapses + 1
    elif rating == "hard":
        box, lapses = state.leitner_box, state.lapses
    else:
        box, lapses = min(5, state.leitner_box + (2 if rating == "easy" else 1)), state.lapses
    return replace(state, leitner_box=box, interval_days=LEITNER_INTERVALS[box], lapses=lapses,
                   repetitions=state.repetitions + (0 if rating == "again" else 1))


def apply(state: SrsState, rating: str, algorithm: str = "sm2") -> SrsState:
    if rating not in RATINGS:
        raise ValueError(f"Unbekannte Bewertung: {rating}")
    if algorithm == "leitner":
        return leitner(state, rating)
    if algorithm == "sm2":
        new = sm2(state, rating)
        # Leitner-Fach parallel mitführen, damit beim Wechsel des Verfahrens nichts verloren geht
        return replace(new, leitner_box=leitner(state, rating).leitner_box)
    raise ValueError(f"Unbekanntes Verfahren: {algorithm}")


def next_due(now: datetime, state: SrsState) -> datetime:
    return now + timedelta(days=state.interval_days)
