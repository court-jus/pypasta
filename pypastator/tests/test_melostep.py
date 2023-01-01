"""
Tests for the melostep engine.
"""
import random

import pytest

from pypastator.engine.melostep import Melostep


class BaseEngineForTest(Melostep):
    """
    A 'mocked' engine for tests
    """

    def get_pattern(self):
        return [1, 2, 3]  # The three notes in the chord


@pytest.fixture(name="melostep")
def fixture_melostep(track):
    """
    Test engine
    """
    test_engine = BaseEngineForTest(track)
    test_engine.pitch.set_value(60, force=True)
    test_engine.gravity.set_value(48, force=True)
    test_engine.related_to.set_value(0, force=True)
    test_engine.melo_length.set_value(5, force=True)
    return test_engine


@pytest.mark.parametrize(
    "steps, result",
    [
        ([0, 0, 0, 0, 0], [0, 0, 0, 0, 0]),
        ([0, 1, 0, -1, 0], [0, 0, 2, 2, 0]),
        ([1, 1, -2, 3, 0], [0, 2, 4, 0, 5]),
        ([-1, -1, 2, 1, -2], [0, -1, -3, 0, 2]),
    ],
)
def test_melostep_generate_new_melody(melostep, steps, result):
    """
    Test how melostep generate new melodies.
    """
    random.seed(1)
    melostep.steps.set_value(steps, force=True)
    assert melostep.generate_new_melody() == result
