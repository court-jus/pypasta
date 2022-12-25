"""
The Strum engine

It does play all the notes like the Chord engine but
strums them.
"""
from pypastator.constants import DEFAULT_STRUMMING
from pypastator.engine.base import BaseArp


class Strum(BaseArp):
    """
    Definition of the Strum engine.
    """

    def get_positions(self):
        rpattern = self.get_rythm_pattern()
        notes_pattern = self.get_pattern()
        base_positions = [0]
        strumming = DEFAULT_STRUMMING
        for duration in rpattern[:-1]:
            base_positions.append(duration + base_positions[-1])
        positions = []
        for base_position in base_positions:
            positions.extend(
                [base_position + i * strumming for i in range(len(notes_pattern))]
            )
        return positions

    def get_stop_positions(self):
        rpattern = self.get_rythm_pattern()
        stop_positions = [0]
        for duration in rpattern[:-1]:
            stop_positions.append(duration + stop_positions[-1])
        return stop_positions

    def get_vel(self, tick):
        vel = int(self.basevel.get_value() * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation.get_value())
        return max(1, min(vel, 127))
