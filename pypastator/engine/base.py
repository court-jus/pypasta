from constants import (
    ACCENT,
    DHALF,
    DQUARTER,
    DEIGHTH,
    EIGHTH,
    FULL,
    HALF,
    QUARTER,
    SIXTEENTH,
)

NOTE_PATTERNS = [
    (3, 1, 1),
    (3, 1, 2),
    (3, 2, 1),
    (3, 2, 2),
    (3, 2, 3, 4),
    (3, 3, 2),
    (3, 3, 3, 4),
    (1, 1, 1),
    (1, 1, 2),
    (1, 2, 2),
    (1, 2, 3, 3),
    (1, 2, 3, 4),
    (1, 3, 2),
    (1, 3, 3),
    (1, 3, 3, 4),
    (1, 2, 3, 4, 5),
]

RYTHM_PATTERNS = [
    (FULL,),
    (HALF, HALF),
    (QUARTER, DHALF),
    (QUARTER, QUARTER, HALF),
    (QUARTER, QUARTER, QUARTER, QUARTER),
    (HALF, EIGHTH, DQUARTER),
    (QUARTER, QUARTER, EIGHTH, EIGHTH, QUARTER),
    (QUARTER, DQUARTER, EIGHTH, EIGHTH, EIGHTH),
    (EIGHTH, DEIGHTH, EIGHTH, QUARTER, SIXTEENTH, SIXTEENTH, EIGHTH),
    (
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
        SIXTEENTH,
    ),
]

SCALE = [0, 2, 3, 5, 7, 8, 10]
CHORD = [1, 3, 5, 7, 9]


class BaseEngine:
    def __init__(self):
        self.pitch = 0
        self.rythm = 0
        self.pattern = 0
        self.basevel = 0
        self.pos = 0
        self.midi_channel = 0
        self.prevnotes = []
        self.mute = True
        self.scale = SCALE
        self.chord = CHORD
        self.accentuation = ACCENT

    def load(self, data):
        for loadable_key in (
            "pitch",
            "rythm",
            "pattern",
            "basevel",
            "mute",
            "midi_channel",
        ):
            if loadable_key in data:
                setattr(self, loadable_key, data[loadable_key])

    def set_pitch(self, value):
        self.pitch = value
        return value

    def set_rythm(self, value):
        self.rythm = value
        return value

    def set_pattern(self, value):
        self.pattern = value
        return value

    def set_basevel(self, value):
        self.basevel = value
        return value

    def set_mute(self, value):
        if value == 127:
            self.mute = not self.mute
        return not self.mute

    def midi_tick(self, ticks, timestamp, chord_number):
        result = []
        rpattern = self.get_rythm_pattern()
        rlength = sum(rpattern)
        tick = ticks % rlength
        positions = self.get_positions()
        stop_positions = self.get_stop_positions()
        if self.prevnotes and (tick in stop_positions or self.mute):
            for prevnote in self.prevnotes:
                result.append((timestamp, "off", self.midi_channel, prevnote, 0))
            self.prevnotes = []
        if tick in positions:
            notes = self.get_notes(tick, chord_number)
            vel = self.get_vel(tick)
            self.pos += 1
            for note in notes:
                if not self.mute:
                    result.append((timestamp, "on", self.midi_channel, note, vel))
                self.prevnotes.append(note)
        return result

    def get_rythm_pattern(self):
        return RYTHM_PATTERNS[int(self.rythm * (len(RYTHM_PATTERNS) - 1) / 127)]

    def get_positions(self):
        rpattern = self.get_rythm_pattern()
        positions = [0]
        for duration in rpattern[:-1]:
            positions.append(duration + positions[-1])
        return positions

    def get_stop_positions(self):
        return self.get_positions()

    def get_pattern(self):
        return NOTE_PATTERNS[int(self.pattern * (len(NOTE_PATTERNS) - 1) / 127)]

    def get_notes(self, tick, chord_number):
        pattern = self.get_pattern()
        notes = []
        for degree in pattern:
            octave = self.pitch // 12
            scale_degree = (
                self.chord[(degree - 1) % len(self.chord)] - 1 + chord_number - 1
            ) % len(self.scale)
            note = self.scale[scale_degree] + 12 * octave

            print(
                "t",
                tick,
                "ch",
                chord_number,
                "pa",
                pattern,
                "cd",
                degree,
                "o",
                octave,
                "sd",
                scale_degree,
                "no",
                note,
            )
            notes.append(note)
        return notes

    def get_vel(self, tick):
        vel = int(self.basevel * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation)
        return max(1, min(vel, 127))
