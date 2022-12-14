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

