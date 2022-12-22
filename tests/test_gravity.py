"""
Tests related to the gravity (or tessitura) feature.
"""
import pytest

from pypastator.engine.base import BaseEngine
from pypastator.engine.session import Session
from pypastator.engine.track import Track


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
    test_session.scale.set_value(0)  # major
    test_session.chord_type.set_value(0)  # triad
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
    test_engine.pitch.set_value(60)
    test_engine.gravity.set_value(0)
    return test_engine


@pytest.mark.parametrize(
    "pitch, gravity, lower, higher",
    [
        (60, 0, 60, 60),
        (60, 12, 54, 66),
        (0, 12, 0, 12),
        (3, 24, 0, 24),
        (125, 10, 117, 127),
    ],
)
def test_tessitura_calculation(engine, pitch, gravity, lower, higher):
    """
    Test how we compute higher/lower bounds based on pitch and gravity.
    """
    engine.pitch.set_value(pitch)
    engine.gravity.set_value(gravity)
    assert engine.get_tessitura() == (lower, higher)


@pytest.mark.parametrize(
    "pitch, gravity, notes",
    [
        (60, 0, [60, 64, 55]),
        (60, 12, [60, 64, 55]),
        (0, 12, [0, 4, 7]),
        (3, 24, [0, 4, 7]),
        (125, 10, [120, 124, 127]),
    ],
)
def test_notes_choice(engine, pitch, gravity, notes):
    """
    Test how we use higher/lower bounds to choose playable notes.
    """
    engine.pitch.set_value(pitch)
    engine.gravity.set_value(gravity)
    assert engine.get_notes() == notes
