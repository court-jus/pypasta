"""
Melotor Engine.

It takes a random note from the scale, base on
user chosen weights.
"""
import random

from pypastator.engine.base import BaseArp
from pypastator.engine.field import Field, ListField


class Melotor(BaseArp):
    """
    Melotor Engine.
    """

    def __init__(self, track):
        self.weights = ListField(default=[10, 2, 4, 3, 8, 6, 8, 5, 5, 0, 3, 0, 2])
        self.chord_influence = Field(default=48)
        super().__init__(track)

    def get_melotor_choices(self):
        """
        Get the possible choices for melotor to pick from.
        """
        scale_notes = self.track.session.scale.get_value()
        chord_notes = [degree - 1 for degree in self.track.session.current_chord.get_value()]
        chord_influence = self.chord_influence.get_value() / 128
        choices = []
        for degree, weight in enumerate(self.weights.get_value()):
            if degree in chord_notes and chord_influence > 0.1 and weight == 0:
                weight = 20 * chord_influence
            in_chord_ratio = 1 + (1 if degree in chord_notes else -1) * chord_influence
            tuned_weight = weight * in_chord_ratio
            octave = degree // len(scale_notes)
            choices.extend(
                [scale_notes[degree % len(scale_notes)] + octave * 12] * int(tuned_weight)
            )
        if not choices:
            return [0]
        return choices

    def get_candidate_notes(self):
        choices = self.get_melotor_choices()
        transposed = self.transpose_notes(choices, centered=False)
        return random.choice(transposed)
