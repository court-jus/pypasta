"""
Tests related to the gravity (or tessitura) feature.
"""
import pytest

from pypastator.engine.base import BaseEngine
from pypastator.engine.session import Session
from pypastator.engine.track import Track
from pypastator.engine.utils import spread_notes


class BaseEngineForTest(BaseEngine):
    """
    A 'mocked' engine for tests
    """

    def get_pattern(self):
        return [1, 2, 3]  # The three notes in the chord


@pytest.fixture(name="session")
def fixture_session():
    """
    Test session
    """
    test_session = Session(None)
    test_session.scale.set_value(0, force=True)  # major
    test_session.chord_type.set_value(0, force=True)  # triad
    return test_session


@pytest.fixture(name="track")
def fixture_track(session):
    """
    Test track
    """
    return Track(0, session)


@pytest.fixture(name="engine")
def fixture_engine(track):
    """
    Test engine
    """
    test_engine = BaseEngineForTest(track)
    test_engine.pitch.set_value(60, force=True)
    test_engine.gravity.set_value(0, force=True)
    return test_engine


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
