from engine.base import BaseEngine

class Strum(BaseEngine):

    def get_positions(self):
        rpattern = self.get_rythm_pattern()
        notes_pattern = self.get_pattern()
        base_positions = [0]
        strumming = 3
        for duration in rpattern[:-1]:
            base_positions.append(duration + base_positions[-1])
        positions = []
        for base_position in base_positions:
            positions.extend([base_position + i * strumming for i in range(len(notes_pattern))])
        return positions

    def get_stop_positions(self):
        rpattern = self.get_rythm_pattern()
        stop_positions = [0]
        for duration in rpattern[:-1]:
            stop_positions.append(duration + stop_positions[-1])
        return stop_positions

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

    def get_vel(self, tick):
        vel = int(self.basevel * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation)
        return max(1, min(vel, 127))
