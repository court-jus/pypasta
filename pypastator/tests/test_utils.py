import pytest

from pypastator.constants import (
    BAR,
    DEIGHTH,
    DHALF,
    DQUARTER,
    DSIXTEENTH,
    EIGHTH,
    FULL,
    HALF,
    QUARTER,
    SIXTEENTH,
    THIRTYSECOND,
)
from pypastator.engine.utils import duration_to_str


@pytest.mark.parametrize(
    "in_value, out_value",
    [
        (THIRTYSECOND, "32d"),
        (SIXTEENTH, "16th"),
        (DSIXTEENTH, "16th."),
        (EIGHTH, "8th"),
        (DEIGHTH, "8th."),
        (QUARTER, "4th"),
        (DQUARTER, "4th."),
        (HALF, "½"),
        (DHALF, "½."),
        (FULL, "1"),
        (2 * BAR, "2 bars"),
        (16 * BAR, "16 bars"),
        (45, "45"),
        (0, "∅"),
    ],
)
def test_duration_to_str(in_value, out_value):
    assert duration_to_str(in_value) == out_value
