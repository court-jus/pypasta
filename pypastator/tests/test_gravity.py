"""
Tests related to the gravity (or tessitura) feature.
"""
import pytest

from pypastator.engine.utils import spread_notes


@pytest.mark.parametrize(
    "pitch, gravity, lower, higher",
    [
        (60, 0, 60, 60),
        (60, 24, 54, 66),
        (0, 24, 0, 12),
        (3, 48, 0, 24),
        (125, 20, 117, 127),
    ],
)
def test_tessitura_calculation(engine, pitch, gravity, lower, higher):
    """
    Test how we compute higher/lower bounds based on pitch and gravity.
    """
    engine.pitch.set_value(pitch, force=True)
    engine.gravity.set_value(gravity, force=True)
    assert engine.get_tessitura() == (lower, higher)


@pytest.mark.parametrize(
    "pitch, gravity, related_to, notes",
    [
        (60, 0, 0, [0, 2, 4]),
        (60, 24, 0, [0, 2, 4]),
        (0, 24, 0, [0, 2, 4]),
        (3, 48, 0, [0, 2, 4]),
        (125, 20, 0, [0, 2, 4]),
        (60, 0, 1, [0, 4, 7]),
        (60, 24, 1, [0, 4, 7]),
        (0, 24, 1, [0, 4, 7]),
        (3, 48, 1, [0, 4, 7]),
        (125, 20, 1, [0, 4, 7]),
        (60, 0, 2, [60]),
        (60, 24, 2, [60]),
        (0, 24, 2, [0]),
        (3, 48, 2, [3]),
        (125, 20, 2, [125]),
    ],
)
def test_candidates(engine, pitch, gravity, related_to, notes):
    """
    Test the candidate notes returned, they do NOT depend on pitch nor gravity.
    """
    engine.pitch.set_value(pitch, force=True)
    engine.gravity.set_value(gravity, force=True)
    engine.related_to.set_value(related_to, force=True)
    assert engine.get_candidate_notes() == notes


@pytest.mark.parametrize(
    "pitch, gravity, notes",
    [
        (60, 0, [60, 64, 55]),
        (60, 24, [60, 64, 55]),
        (0, 24, [0, 4, 7]),
        (3, 48, [0, 16, 19]),
        (125, 20, [120, 124, 127]),
    ],
)
def test_notes_choice(engine, pitch, gravity, notes):
    """
    Test how we use higher/lower bounds to choose playable notes.
    """
    engine.pitch.set_value(pitch, force=True)
    engine.gravity.set_value(gravity, force=True)
    assert engine.get_notes() == notes


@pytest.mark.parametrize(
    "pitch, gravity, in_notes, out_notes",
    [
        (60, 0, [0, 4, 7], [60, 64, 55]),
        (60, 24, [0, 4, 7], [60, 64, 55]),
        (0, 24, [0, 4, 7], [0, 4, 7]),
        (3, 48, [0, 4, 7], [0, 4, 7]),
        (125, 20, [0, 4, 7], [120, 124, 127]),
    ],
)
def test_transpose_notes(engine, pitch, gravity, in_notes, out_notes):
    """
    Test the transposition algorithm.
    """
    engine.pitch.set_value(pitch, force=True)
    engine.gravity.set_value(gravity, force=True)
    assert engine.transpose_notes(in_notes) == out_notes


@pytest.mark.parametrize(
    "notes, lowest, highest, result",
    [
        ([60, 64, 67], 48, 95, [48, 76, 91]),
        ([60, 64, 67], 60, 60, [60, 64, 55]),
        ([60, 64, 67], 54, 66, [60, 64, 55]),
        ([60, 64, 67], 0, 12, [0, 4, 7]),
        ([60, 64, 67], 0, 24, [0, 16, 19]),
        ([60, 64, 67], 117, 127, [120, 124, 127]),
    ],
)
def test_spread_notes(notes, lowest, highest, result):
    """
    Test notes spreading algorithm.
    """
    assert spread_notes(notes, lowest, highest) == result
