"""
Melotor Engine.

It takes a random note from the scale, base on
user chosen weights.
"""
import random

import pygame.midi

from pypastator.constants import (
    BAR,
    DEIGHTH,
    DHALF,
    DQUARTER,
    EIGHTH,
    HALF,
    QUARTER,
    SIXTEENTH,
)
from pypastator.engine.base import BaseArp
from pypastator.engine.field import EnumField, Field, ListField
from pypastator.engine.utils import duration_to_str

LOADABLE_KEYS = (
    "weights",
    "chord_influence",
    "melo_length",
    "change_frequency",
    "change_intensity",
)

FASTEST_EVOLUTION = SIXTEENTH
SLOWEST_EVOLUTION = 32 * BAR
MIN_LENGTH = 2
MAX_LENGTH = 24


class Melotor(BaseArp):
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
        self.melo_length = Field(default=5, min_value=MIN_LENGTH, max_value=MAX_LENGTH)
        self.change_frequency = EnumField(
            default=8,
            choices=[
                SIXTEENTH,
                EIGHTH,
                DEIGHTH,
                QUARTER,
                DQUARTER,
                HALF,
                DHALF,
                DHALF + EIGHTH,
                BAR,
                BAR + HALF,
                2 * BAR,
                3 * BAR,
                4 * BAR,
                6 * BAR,
                8 * BAR,
                12 * BAR,
                16 * BAR,
            ],
        )
        self.change_intensity = Field(default=64)
        self.current_melo = ListField()
        super().__init__(track)

    def engine_load(self, data):
        """
        Load from data.
        """
        for loadable_key in LOADABLE_KEYS:
            if loadable_key in data:
                field = getattr(self, loadable_key)
                field.set_value(data[loadable_key], force=True)

    def engine_save(self):
        """
        Get data to save this engine.
        """
        result = {}
        for savable_key in LOADABLE_KEYS:
            field = getattr(self, savable_key)
            result[savable_key] = field.value
        return result

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

    def get_notes(self):
        """
        Get playable notes.
        """
        pos = self.pos.get_value()
        candidates = self.get_candidate_notes()
        transposed = self.transpose_notes(candidates, centered=False)
        note_at_pos = transposed[pos % len(transposed)]
        return [note_at_pos]

    # For GUI
    @property
    def current_melo_str(self):
        """
        Get a str representation of current melo.
        """
        notes = self.current_melo.get_value()
        notes = self.transpose_notes(notes, centered=False)
        note_names = " ".join(
            [
                f"{' ' if idx % 4 == 0 else ''}{pygame.midi.midi_to_ansi_note(note):2}"
                for idx, note in enumerate(notes)
            ]
        )
        return note_names

    @property
    def get_change_frequency_str(self):
        """
        Get a str representation of the change frequency.
        """
        return f"Ch.Frq: {duration_to_str(self.change_frequency.get_value())}"

    @property
    def get_melo_length_knob(self):
        """
        Get the value for the melo length knob.
        """
        return int(self.melo_length.get_value() / (MAX_LENGTH - MIN_LENGTH) * 127)
