import pygame.midi

from .field import Field, BooleanField, EnumField
from constants import (
    ACCENT,
    NOTE_PATTERNS,
    RYTHM_PATTERNS,
    SCALE_NAMES,
    SCALES,
    CHORDS,
)


class BaseEngine:
    def __init__(self, track):
        super().__init__()
        self.track = track
        # Settings
        self.pitch = Field()
        self.rythm = Field()
        self.pattern = Field()
        self.basevel = Field()
        self.midi_channel = Field(min_value=0, max_value=15)
        self.active = BooleanField(default=True)
        self.accentuation = Field(default=ACCENT)
        self.related_to = EnumField(choices=["scale", "chord"])
        # Internal stuff
        self.pos = Field(max_value=None)
        self.prevnotes = []
        self.chord_number = 1

    def load(self, data):
        for loadable_key in (
            "pitch",
            "rythm",
            "pattern",
            "basevel",
            "midi_channel",
            "active",
            "accentuation",
        ):
            if loadable_key in data:
                field = getattr(self, loadable_key)
                if isinstance(field, Field):
                    field.value = data[loadable_key]
                else:
                    setattr(self, loadable_key, data[loadable_key])

    def save(self):
        result = {}
        for savable_key in (
            "pitch",
            "rythm",
            "pattern",
            "basevel",
            "midi_channel",
            "active",
            "accentuation",
        ):
            field = getattr(self, savable_key)
            if isinstance(field, Field):
                result[savable_key] = field.value
            else:
                result[savable_key] = field
        return result

    @property
    def pattern_str(self):
        note_names = [pygame.midi.midi_to_ansi_note(note) for note in self.get_notes()]
        return ", ".join(note_names)

    @property
    def rythm_str(self):
        rpat = self.get_rythm_pattern()
        if not all([int(r / 6) == r / 6 for r in rpat]):
            return str()
        rpat = [int(r / 6) for r in rpat]
        return "".join(["o" + ("." * (r - 1) if r > 1 else "") for r in rpat])

    @property
    def related_to_str(self):
        return self.related_to.str_value()

    def midi_tick(self, ticks, timestamp, chord_number):
        midi_channel = self.midi_channel.value
        self.chord_number = chord_number
        result = []
        rpattern = self.get_rythm_pattern()
        rlength = sum(rpattern)
        tick = ticks % rlength
        positions = self.get_positions()
        stop_positions = self.get_stop_positions()
        if self.prevnotes and (tick in stop_positions or not self.active.value):
            for prevnote in self.prevnotes:
                result.append((timestamp, "off", midi_channel, prevnote, 0))
            self.prevnotes = []
        if not self.active.value:
            return result
        if tick in positions:
            self.pos.increment()
            notes = self.get_notes()
            vel = self.get_vel(tick)
            for note in notes:
                if self.active.value:
                    result.append((timestamp, "on", midi_channel, note, vel))
                self.prevnotes.append(note)
        return result

    def get_rythm_pattern(self):
        return RYTHM_PATTERNS[int(self.rythm.value * (len(RYTHM_PATTERNS) - 1) / 127)]

    def get_positions(self):
        rpattern = self.get_rythm_pattern()
        positions = [0]
        for duration in rpattern[:-1]:
            positions.append(duration + positions[-1])
        return positions

    def get_stop_positions(self):
        return self.get_positions()

    def get_pattern(self):
        return NOTE_PATTERNS[int(self.pattern.value * (len(NOTE_PATTERNS) - 1) / 127)]

    def get_notes(self):
        pattern = self.get_pattern()
        scale_notes = SCALES[self.track.session.scale.value]
        chord_notes = self.track.session.current_chord.get_value()
        notes = []
        for degree in pattern:
            octave = self.pitch.value // 12
            if degree > max(chord_notes):
                octave += 1
            scale_degree = (
                chord_notes[(degree - 1) % len(chord_notes)] - 1 + self.chord_number - 1
            ) % len(scale_notes)
            note = scale_notes[scale_degree] + 12 * octave
            notes.append(note)
        return notes

    def get_vel(self, tick):
        vel = int(self.basevel.value * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation.value)
        return max(1, min(vel, 127))

    def stop(self):
        timestamp = pygame.midi.time()
        midi_channel = self.midi_channel.value
        result = []
        if self.prevnotes:
            for prevnote in self.prevnotes:
                result.append((timestamp, "off", midi_channel, prevnote, 0))
        return result
