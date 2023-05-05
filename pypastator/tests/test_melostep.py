"""
Tests for the melostep engine.
"""
import random

import pytest

from pypastator.engine.melostep import Melostep, DEFAULT_MARKOV


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
    "chg_src, chg_dst, new_val, src, dst",
    [
        (None, None, None, 0, 0),
        (-3, 1, 0.5, -3, 0),
        (-3, 1, 0, -3, -1),
        (-3, 1, 0.9, -3, 1),
    ],
)
def test_melostep_generate_new_step(melostep, chg_src, chg_dst, new_val, src, dst):
    """
    Test how melostep generate new step.
    """
    random.seed(1)
    melostep.adapt_value(chg_src, chg_dst, new_val)
    melostep.prev_step.set_value(src, force=True)
    assert melostep.generate_next_step() == dst


def test_default_value():
    """
    Validate some default values.
    """
    assert DEFAULT_MARKOV[(-3, -2)] == 0.1
    assert DEFAULT_MARKOV[(0, 0)] == pytest.approx(0.4)


def test_adapt_value(melostep):
    """
    Test the adapt value method.
    """
    assert melostep.markov.get_value((-3, 2)) == 0.1
    assert melostep.markov.get_value((-3, 0)) == 0.1
    assert melostep.markov.get_value((-2, 0)) == 0.1
    melostep.adapt_value(-3, 2, 0.5)
    assert melostep.markov.get_value((-3, 2)) == 0.5
    assert melostep.markov.get_value((-3, 0)) == pytest.approx(0.1 * 0.5/0.9)
    assert sum([melostep.markov.get_value((-3, dst)) for dst in range(-3, 4)]) == pytest.approx(1)
    assert melostep.markov.get_value((-2, 0)) == 0.1
