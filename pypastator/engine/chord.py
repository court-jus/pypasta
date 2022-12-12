from constants import ACCENT, DHALF, DQUARTER, DEIGHTH, EIGHTH, FULL, HALF, QUARTER, SIXTEENTH

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
    (1, 3, 2),
    (1, 3, 3),
    (1, 3, 3, 4),
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
    (SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH, SIXTEENTH),
]

SCALE = [0, 2, 3, 5, 7, 8, 10]
CHORD = [1, 3, 5, 7]

class Chord:
    def __init__(self):
        self.pitch = 0
        self.rythm = 0
        self.pattern = 0
        self.basevel = 0
        self.pos = 0
        self.midi_channel = 0
        self.prevnotes = []
        self.mute = True
    
    def load(self, data):
        for loadable_key in ("pitch", "rythm", "pattern", "basevel", "mute", "midi_channel"):
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

    def midi_tick(self, ticks, timestamp, chord):
        result = []
        rpattern = RYTHM_PATTERNS[int(self.rythm * (len(RYTHM_PATTERNS) - 1) / 127)]
        rlength = sum(rpattern)
        positions = [0]
        for duration in rpattern[:-1]:
            positions.append(duration + positions[-1])
        tick = ticks % rlength
        if tick in positions:
            notes, vel = self.get_notes(tick, chord)
            self.pos += 1
            if self.prevnotes and (self.mute or len(notes) > 0):
                for prevnote in self.prevnotes:
                    result.append((timestamp, "off", self.midi_channel, prevnote, 0))
                self.prevnotes = []
            for note in notes:
                if not self.mute:
                    result.append((timestamp, "on", self.midi_channel, note, vel))
                self.prevnotes.append(note)
        return result


    def get_notes(self, tick, chord):
        pattern = NOTE_PATTERNS[int(self.pattern * (len(NOTE_PATTERNS) - 1) / 127)]
        notes = []
        for degree in pattern:
            octave = self.pitch // 12
            scale_degree = (CHORD[(degree - 1) % len(CHORD)] - 1 + chord - 1) % len(SCALE)
            note = SCALE[scale_degree] + 12 * octave

            print("t", tick, "ch", chord, "pa", pattern, "cd", degree, "o", octave, "sd", scale_degree, "no", note)
            notes.append(note)
        vel = int(self.basevel * 90 / 127)
        if tick == 0:
            vel = int(vel * ACCENT)
        vel = max(1, min(vel, 127))
        return notes, vel
