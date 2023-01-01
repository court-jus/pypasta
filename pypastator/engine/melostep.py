"""
Melostep Engine.

It creates a melody by following steps, skips and leaps
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
    "steps",
    "melo_length",
    "change_frequency",
    "change_intensity",
)

FASTEST_EVOLUTION = SIXTEENTH
SLOWEST_EVOLUTION = 32 * BAR
MIN_LENGTH = 2
MAX_LENGTH = 24

MIN_LEAP = 3
MAX_LEAP = 6


class Melostep(BaseArp):
    """
    Melostep Engine.
    """

    def __init__(self, track):
        self.steps = ListField(default=[0, 1, 1, -2, 3, -3])
        self.melo_length = Field(default=12, min_value=MIN_LENGTH, max_value=MAX_LENGTH)
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
        melody = self.generate_new_melody()
        self.current_melo.set_value(melody)
        return melody

    def generate_new_melody(self):
        """
        Generate a new melody.
        """
        scale_notes = self.track.session.scale.get_value()
        chord_notes = [
            scale_notes[(degree - 1) % len(scale_notes)]
            for degree in self.track.session.current_chord.get_value()
        ]
        melody = []
        # Pick one of the chord notes to start with
        current_note = random.choice(chord_notes)
        steps = self.steps.get_value()
        current_step_pos = 0
        try:
            current_scale_pos = scale_notes.index(current_note)
        except ValueError:
            current_scale_pos = 0
        while len(melody) < self.melo_length.get_value():
            octave = 0
            if current_scale_pos < 0:
                octave += current_scale_pos // 12
            current_note = scale_notes[current_scale_pos % len(scale_notes)]
            melody.append(current_note + 12 * octave)
            movement = steps[current_step_pos % len(steps)]
            if abs(movement) < 3:
                # Step or Skip, that's a deterministic move
                current_scale_pos = current_scale_pos + movement
            else:
                if movement > 0:
                    movement = random.randint(MIN_LEAP, MAX_LEAP)
                else:
                    movement = random.randint(-MAX_LEAP, -MIN_LEAP)
                current_scale_pos = current_scale_pos + movement
            current_step_pos += 1
        return melody

    def evolve_melo(self):
        """
        Take current melo and slighty change it.
        """
        self.reset_melo()
        current = self.get_choices()
        return current

    def get_choices(self):
        """
        Get the possible choices for melostep to pick from.
        """
        current_value = self.current_melo.get_value()
        if current_value:
            return current_value
        return self.reset_melo()

    def get_candidate_notes(self):
        choices = self.get_choices()
        # transposed = self.transpose_notes(choices, centered=False)
        return choices

    def midi_tick(self, ticks, timestamp, chord_number):
        """
        Trigger melostep evolution based on ticks.
        """
        tick_evolution = self.change_frequency.get_value()
        if ticks % BAR == 0:
            # Always start bar at the start of the melo
            self.pos.set_value(0)
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
        Return the value for the melo length knob.
        """
        return int(self.melo_length.get_value() / (MAX_LENGTH - MIN_LENGTH) * 127)
