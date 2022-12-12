from engine.base import BaseEngine

class Arp(BaseEngine):

    def get_notes(self, tick, chord_number):
        pattern = self.get_pattern()
        chord_degree = pattern[self.pos % len(pattern)]
        if not chord_degree:
            return []
        octave = self.pitch // 12
        scale_degree = (self.chord[(chord_degree - 1) % len(self.chord)] - 1 + chord_number - 1) % len(self.scale)
        note = self.scale[scale_degree] + 12 * octave

        print("t", tick, "ch", chord_number, "pa", pattern, "cd", chord_degree, "o", octave, "sd", scale_degree, "no", note)
        return [note]
