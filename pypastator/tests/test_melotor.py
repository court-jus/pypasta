"""
Tests for the melotor engine.
"""
import pytest

from pypastator.engine.melotor import Melotor


class BaseEngineForTest(Melotor):
    """
    A 'mocked' engine for tests
    """

    def get_pattern(self):
        return [1, 2, 3]  # The three notes in the chord


@pytest.fixture(name="melotor")
def fixture_melotor(track):
    """
    Test engine
    """
    test_engine = BaseEngineForTest(track)
    test_engine.pitch.set_value(60, force=True)
    test_engine.gravity.set_value(48, force=True)
    test_engine.related_to.set_value(0, force=True)
    test_engine.chord_influence.set_value(0, force=True)
    return test_engine


@pytest.mark.parametrize(
    "weights, choices",
    [
        ([1, 1, 1], [0, 2, 4]),
        ([1, 0, 1, 0, 1], [0, 4, 7]),
        (
            [5, 1, 2, 1, 3, 1, 4],
            [0, 0, 0, 0, 0, 2, 4, 4, 5, 7, 7, 7, 9, 11, 11, 11, 11],
        ),
    ],
)
def test_melotor_choices(melotor, weights, choices):
    """
    Test how melotor generate choices from which to pick a note.
    """
    melotor.weights.set_value(weights, force=True)
    assert melotor.generate_new_choices() == choices


@pytest.mark.parametrize(
    "current, notes",
    [
        ([7, 0, 0, 11, 0], [67, 60, 60, 71, 60]),
        ([7, 11, 7, 7, 14], [67, 71, 67, 67, 74]),
    ],
)
def test_melotor_get_notes(melotor, current, notes):
    """
    Test how melotor generate notes based on current_melo.
    """
    melotor.current_melo.set_value(current, force=True)
    assert (
        melotor.transpose_notes(melotor.get_candidate_notes(), centered=False) == notes
    )
