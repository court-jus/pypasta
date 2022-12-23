"""
Base for all musical engines.
"""
import pygame.midi

from pypastator.constants import ACCENT, NOTE_PATTERNS, RYTHM_PATTERNS
from pypastator.engine.field import BooleanField, EnumField, Field
from pypastator.engine.utils import spread_notes

LOADABLE_KEYS = (
    "pitch",
    "gravity",
    "rythm",
    "pattern",
    "basevel",
    "midi_channel",
    "active",
    "accentuation",
)


class BaseEngine:
    """
    Base engine.
    """

    def __init__(self, track):
        super().__init__()
        self.track = track
        # Settings
        self.pitch = Field(smooth=True)
        self.gravity = Field(default=12, smooth=True)
        self.rythm = Field(smooth=True)
        self.pattern = Field(smooth=True)
        self.basevel = Field(smooth=True)
        self.midi_channel = Field(min_value=0, max_value=15)
        self.active = BooleanField(default=True)
        self.accentuation = Field(default=ACCENT, smooth=True)
        self.related_to = EnumField(choices=["scale", "chord"])
        # Internal stuff
        self.pos = Field(max_value=None)
        self.currently_playing_notes = []
        self.chord_number = 1

    def load(self, data):
        """
        Load from data.
        """
        for loadable_key in LOADABLE_KEYS:
            if loadable_key in data:
                field = getattr(self, loadable_key)
                if isinstance(field, Field):
                    field.set_value(data[loadable_key], force=True)
                else:
                    setattr(self, loadable_key, data[loadable_key])

    def save(self):
        """
        Get data to save this engine.
        """
        result = {"type": self.track.engine_type.get_value()}
        for savable_key in LOADABLE_KEYS:
            field = getattr(self, savable_key)
            if isinstance(field, Field):
                result[savable_key] = field.value
            else:
                result[savable_key] = field
        return result

    @property
    def pattern_str(self):
        """
        Get str representation of the melodic pattern.
        """
        lowest, highest = [
            f"{pygame.midi.midi_to_ansi_note(note):4}" for note in self.get_tessitura()
        ]
        note_names = ", ".join(
            [f"{pygame.midi.midi_to_ansi_note(note):4}" for note in self.get_notes()]
        )
        return f"{lowest} < {note_names} < {highest}"

    @property
    def rythm_str(self):
        """
        Get str representation of the rythmic pattern.

        The representation uses 'o' and '.', for example a simple
        4/4 rythm will be presented as:

        o...o...o...o...
        """
        rpat = self.get_rythm_pattern()
        if not all(int(r / 6) == r / 6 for r in rpat):
            return str()
        rpat = [int(r / 6) for r in rpat]
        return "".join(["o" + ("." * (r - 1) if r > 1 else "") for r in rpat])

    @property
    def related_to_str(self):
        """
        Get str representation of the 'related_to' attribute.
        """
        return self.related_to.str_value()

    def midi_tick(self, ticks, timestamp, chord_number):
        """
        Handle Midi tick event.

        Gather positions where the engine should trigger events.
        Gather notes it should play and at which velocity.

        Return event list.
        """
        midi_channel = self.midi_channel.get_value()
        self.chord_number = chord_number
        result = []
        rpattern = self.get_rythm_pattern()
        rlength = sum(rpattern)
        tick = ticks % rlength
        positions = self.get_positions()
        stop_positions = self.get_stop_positions()
        if self.currently_playing_notes and (
            tick in stop_positions or not self.active.get_value()
        ):
            for prevnote in self.currently_playing_notes:
                result.append((timestamp, "off", midi_channel, prevnote, 0))
            self.currently_playing_notes = []
        if not self.active.get_value():
            return result
        if tick in positions:
            self.pos.increment()
            notes = self.get_notes()
            vel = self.get_vel(tick)
            for note in notes:
                if self.active.get_value():
                    result.append((timestamp, "on", midi_channel, note, vel))
                self.currently_playing_notes.append(note)
        return result

    def get_rythm_pattern(self):
        """
        Get rythmic pattern.
        """
        return RYTHM_PATTERNS[
            int(self.rythm.get_value() * (len(RYTHM_PATTERNS) - 1) / 127)
        ]

    def get_positions(self):
        """
        Get all positions where the engine should trigger Note ON events.
        """
        rpattern = self.get_rythm_pattern()
        positions = [0]
        for duration in rpattern[:-1]:
            positions.append(duration + positions[-1])
        return positions

    def get_stop_positions(self):
        """
        Get all positions where the engine should trigger Note OFF events.
        """
        return self.get_positions()

    def get_pattern(self):
        """
        Get melodic pattern.
        """
        return NOTE_PATTERNS[
            int(self.pattern.get_value() * (len(NOTE_PATTERNS) - 1) / 127)
        ]

    def get_tessitura(self):
        """
        Get the lowest/highest playable notes.
        """
        delta = int(self.gravity.get_value() / 4)
        center = self.pitch.get_value()
        if center - delta < 0:
            center = delta
        if center + delta > 127:
            center = 127 - delta
        return (center - delta, center + delta)

    def get_notes(self):
        """
        Get playable notes.
        """
        pattern = self.get_pattern()
        scale_notes = self.track.session.scale.get_value()
        chord_notes = self.track.session.current_chord.get_value()
        lowest, highest = self.get_tessitura()
        notes = []
        for degree in pattern:
            octave = self.pitch.get_value() // 12
            scale_degree = (
                chord_notes[(degree - 1) % len(chord_notes)] - 1 + self.chord_number - 1
            ) % len(scale_notes)
            note = scale_notes[scale_degree] + 12 * octave
            if note < lowest:
                note += (((lowest - note) // 12) + 1) * 12
            if note > highest:
                note -= (((note - highest) // 12) + 1) * 12
            if note < lowest:
                # note is outside of our tessitura, find the closest equivalent
                if lowest - note > (note + 12 - lowest):
                    note += 12
            if degree > max(chord_notes):
                octave += 1
            notes.append(int(note))
        # Now spread the notes into the whole allowed tessitura
        return spread_notes(notes, lowest, highest)

    def get_vel(self, tick):
        """
        Get velocity for this tick.

        This is used to generate accentuation based on beat.
        """
        vel = int(self.basevel.get_value() * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation.get_value())
        return max(1, min(vel, 127))

    def stop(self):
        """
        Send Note OFF event for all currently playing notes.
        """
        timestamp = pygame.midi.time()
        midi_channel = self.midi_channel.get_value()
        result = []
        if self.currently_playing_notes:
            for prevnote in self.currently_playing_notes:
                result.append((timestamp, "off", midi_channel, prevnote, 0))
        return result


class BaseArp(BaseEngine):
    """
    Base for all arpegiating engines.
    """

    def get_notes(self):
        notes = super().get_notes()
        return [notes[self.pos.get_value() % len(notes)]]
