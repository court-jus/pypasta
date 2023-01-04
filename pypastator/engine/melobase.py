"""
Melotor and melostep base Engine.
"""
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

MIN_LENGTH = 2
MAX_LENGTH = 24


class Melobase(BaseArp):
    """
    Base for melotor/melostep engines.
    """

    def __init__(self, track):
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

    def get_loadable_keys(self):
        """
        List keys that can be loaded/saved.
        """
        return ["melo_length", "change_frequency", "change_intensity"]

    def engine_load(self, data):
        """
        Load from data.
        """
        for loadable_key in self.get_loadable_keys():
            if loadable_key in data:
                field = getattr(self, loadable_key)
                field.set_value(data[loadable_key], force=True)

    def engine_save(self):
        """
        Get data to save this engine.
        """
        result = {}
        for savable_key in self.get_loadable_keys():
            field = getattr(self, savable_key)
            result[savable_key] = field.value
        return result

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
