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
            positions.extend(
                [base_position + i * strumming for i in range(len(notes_pattern))]
            )
        return positions

    def get_stop_positions(self):
        rpattern = self.get_rythm_pattern()
        stop_positions = [0]
        for duration in rpattern[:-1]:
            stop_positions.append(duration + stop_positions[-1])
        return stop_positions

    def get_notes(self):
        pattern = self.get_pattern()
        chord_degree = pattern[self.pos.get_value() % len(pattern)]
        if not chord_degree:
            return []
        octave = self.pitch.value // 12
        scale = self.track.session.scale.get_value()
        chord_notes = self.track.session.current_chord.get_value()
        scale_degree = (
            chord_notes[(chord_degree - 1) % len(chord_notes)]
            - 1
            + self.chord_number
            - 1
        ) % len(scale)
        note = scale[scale_degree] + 12 * octave

        return [note]

    def get_vel(self, tick):
        vel = int(self.basevel.get_value() * 90 / 127)
        if tick == 0:
            vel = int(vel * self.accentuation.get_value())
        return max(1, min(vel, 127))
