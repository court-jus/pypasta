"""
Melotor Engine.

It takes a random note from the scale, base on
user chosen weights.
"""
import random

from pypastator.engine.base import BaseArp
from pypastator.engine.field import ListField


class Melotor(BaseArp):
    """
    Melotor Engine.
    """

    def __init__(self, track):
        self.weights = ListField(default=[10, 2, 4, 3, 8, 6, 8, 5, 5, 0, 3, 0, 2])
        super().__init__(track)

    def get_melotor_choices(self):
        """
        Get the possible choices for melotor to pick from.
        """
        scale_notes = self.track.session.scale.get_value()
        choices = []
        for degree, weight in enumerate(self.weights.get_value()):
            octave = degree // len(scale_notes)
            choices.extend(
                [scale_notes[degree % len(scale_notes)] + octave * 12] * weight
            )
        if not choices:
            return 0
        return choices

    def get_candidate_notes(self):
        choices = self.get_melotor_choices()
        transposed = self.transpose_notes(choices, centered=False)
        return [random.choice(transposed)]
