from engine.base import BaseEngine
from constants import SCALES, CHORDS


class Arp(BaseEngine):
    def get_notes(self):
        pattern = self.get_pattern()
        scale_notes = SCALES[self.track.session.scale.value]
        chord_notes = self.track.session.current_chord.get_value()
        chord_degree = pattern[self.pos.get_value() % len(pattern)]
        if not chord_degree:
            return []
        octave = self.pitch.value // 12
        if chord_degree > 7:
            octave += 1
        scale_degree = (
            chord_notes[(chord_degree - 1) % len(chord_notes)]
            - 1
            + self.chord_number
            - 1
        ) % len(scale_notes)
        note = scale_notes[scale_degree] + 12 * octave

        return [note]
