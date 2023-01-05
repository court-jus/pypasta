"""
Melotor Engine.

It takes a random note from the scale, base on
user chosen weights.
"""
import random

from pypastator.constants import BAR
from pypastator.engine.field import Field, ListField
from pypastator.engine.melobase import Melobase
from pypastator.widgets.gui.engine import MelotorGUI


class Melotor(Melobase):
    """
    Melotor Engine.

    IDEAS:
    * to account for variable pattern length determined by the rythm parameter,
      allow the notes pattern to be reset whenever the rythm pattern is reset
    * cut parts of the generated melody and repeat them (like in the bach
      prelidium)
    """

    def __init__(self, track):
        self.weights = ListField(default=[10, 2, 4, 3, 8, 6, 8, 5, 5, 0, 3, 0, 2])
        self.chord_influence = Field(default=48)
        super().__init__(track)

    def init_menus(self, pos_y):
        super().init_menus(pos_y)
        self.sub_menus.append(MelotorGUI(self, pos_y=pos_y))

    def get_loadable_keys(self):
        return super().get_loadable_keys() + ["weights", "chord_influence"]

    def reset_melo(self):
        """
        Reset the current set of random choices.
        """
        choices = self.generate_new_choices()
        if not choices:
            choices = [0]
        melo = [random.choice(choices) for _ in range(self.melo_length.get_value())]
        self.current_melo.set_value(melo)
        return melo

    def generate_new_choices(self):
        """
        Generate a new set of random choices.
        """
        scale_notes = self.track.session.scale.get_value()
        chord_notes = [
            degree - 1 for degree in self.track.session.current_chord.get_value()
        ]
        chord_influence = self.chord_influence.get_value() / 128
        choices = []
        for degree, weight in enumerate(self.weights.get_value()):
            if degree in chord_notes and chord_influence > 0.1 and weight == 0:
                weight = 20 * chord_influence
            in_chord_ratio = 1 + (1 if degree in chord_notes else -1) * chord_influence
            tuned_weight = weight * in_chord_ratio
            octave = degree // len(scale_notes)
            choices.extend(
                [scale_notes[degree % len(scale_notes)] + octave * 12]
                * int(tuned_weight)
            )
        return choices

    def evolve_melo(self):
        """
        Take current melo and slighty change it.
        """
        current = self.get_melotor_choices()
        new_value = current[:]
        intensity = self.change_intensity.get_value()
        # Full intensity = change all notes
        # Zero intensity = change nothing
        changes = int(intensity / 127 * len(current))
        choices = self.generate_new_choices()
        already_changed = set()
        while changes > 0:
            change_index = random.randint(0, len(current) - 1)
            # Avoid changing the same note twice
            while change_index in already_changed:
                change_index = random.randint(0, len(current) - 1)
            already_changed.add(change_index)
            if len(already_changed) == len(current):
                already_changed = set()
            new_note = random.choice(choices)
            if len(choices) > 1:
                # Avoid replacing a note by itself
                while new_note == current[change_index]:
                    new_note = random.choice(choices)
            new_value[change_index] = new_note
            changes -= 1
        self.current_melo.set_value(new_value, force=True)

    def get_melotor_choices(self):
        """
        Get the possible choices for melotor to pick from.
        """
        current_value = self.current_melo.get_value()
        if current_value:
            return current_value
        return self.reset_melo()

    def get_candidate_notes(self):
        choices = self.get_melotor_choices()
        # transposed = self.transpose_notes(choices, centered=False)
        return choices

    def midi_tick(self, ticks, timestamp, chord_number):
        """
        Trigger melotor evolution based on ticks.
        """
        if ticks % BAR == 0:
            # Always start bar at the start of the melo
            self.pos.set_value(0)
        tick_evolution = self.change_frequency.get_value()
        if ticks % tick_evolution == 0:
            self.evolve_melo()
        return super().midi_tick(ticks, timestamp, chord_number)
