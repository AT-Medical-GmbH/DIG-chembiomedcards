import pytest

from app import srs


def test_sm2_good_sequence_grows_interval():
    s = srs.SrsState()
    intervals = []
    for _ in range(4):
        s = srs.sm2(s, "good")
        intervals.append(s.interval_days)
    assert intervals[:2] == [1, 6]
    assert intervals[2] > intervals[1] and intervals[3] > intervals[2]


def test_sm2_again_resets_and_counts_lapse():
    s = srs.SrsState(ease_factor=2.5, interval_days=15, repetitions=3)
    s = srs.sm2(s, "again")
    assert (s.repetitions, s.interval_days, s.lapses) == (0, 1, 1)


def test_sm2_ease_never_below_minimum():
    s = srs.SrsState()
    for _ in range(20):
        s = srs.sm2(s, "again")
    assert s.ease_factor == srs.MIN_EASE


def test_leitner_boxes():
    s = srs.SrsState()
    s = srs.leitner(s, "good")
    assert s.leitner_box == 2 and s.interval_days == srs.LEITNER_INTERVALS[2]
    s = srs.leitner(s, "easy")
    assert s.leitner_box == 4
    s = srs.leitner(s, "hard")
    assert s.leitner_box == 4                      # „Unsicher“ bleibt im Fach
    s = srs.leitner(s, "easy")
    assert s.leitner_box == 5                      # Obergrenze
    s = srs.leitner(s, "again")
    assert s.leitner_box == 1 and s.lapses == 1


def test_apply_validates_input():
    with pytest.raises(ValueError):
        srs.apply(srs.SrsState(), "great")
    with pytest.raises(ValueError):
        srs.apply(srs.SrsState(), "good", "anki")
