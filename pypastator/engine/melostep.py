"""
Melostep Engine.

It creates a melody by following steps, skips and leaps
"""
import random

from pypastator.constants import BAR
from pypastator.engine.field import DictField, Field
from pypastator.engine.base import BaseArp
from pypastator.widgets.gui.engine import MelostepGUI

MIN_LEAP = 3
MAX_LEAP = 6

DEFAULT_MARKOV_PROB = 0.1
DEFAULT_MARKOV = {}
for src in range(-3, 4):
    for dst in range(-3, 4):
        DEFAULT_MARKOV[(src, dst)] = (
            (1 - 6 * DEFAULT_MARKOV_PROB)
            if src == dst
            else DEFAULT_MARKOV_PROB
        )

class Melostep(BaseArp):
    """
    Melostep Engine.
    
    Uses a kind of Markov Chain mechanism to choose the next step.
    """

    def __init__(self, track):
        # markov represents the probabilities to go from one step type to another
        self.markov = DictField(default=DEFAULT_MARKOV.copy())
        self.prev_step = Field(default=0, min_value=-3, max_value=3)
        self.next_step = Field(default=0, min_value=-3, max_value=3)
        self.current = Field(default=60)
        super().__init__(track)

    def adapt_value(self, src, dst, val):
        """
        Change the markov probabilities so that src->dst prob is val.

        The sum of probabilities going from src should always equal 1.
        """
        if src is None:
            return
        cur_val = self.markov.get_value()[(src, dst)]
        ratio = (1 - val)/(1 - cur_val)
        new_markov = {}
        for (s, d), v in self.markov.get_value().items():
            if s != src:
                new_markov[(s, d)] = v
            elif d != dst:
                new_markov[(s, d)] = v * ratio
            else:
                new_markov[(s, d)] = val
        self.markov.set_value(new_markov, force=True)

    def init_menus(self, pos_y):
        super().init_menus(pos_y)
        self.sub_menus.append(MelostepGUI(self, pos_y=pos_y))

    def get_loadable_keys(self):
        return super().get_loadable_keys() + ["markov"]

    def generate_next_step(self, low=-3, high=3):
        """
        Generate the next step based on current step and markov prob.
        """
        src = self.prev_step.get_value()
        prob = [self.markov.get_value((src, dst)) for dst in range(low, high + 1)]
        choices = random.choices(range(low, high + 1), weights=prob, k=3)
        self.next_step.set_value(choices[0], force=True)

    def generate_new_melody(self):
        """
        Generate a new melody.
        """
        scale_notes = self.track.session.scale.get_value()
        root = self.track.session.root_note.get_value()
        chord_notes = [
            scale_notes[(degree - 1) % len(scale_notes)]
            for degree in self.track.session.current_chord.get_value()
        ]
        melody = []
        # Pick one of the chord notes to start with
        current_note = random.choice(chord_notes)
        markov = self.markov.get_value()
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
            melody.append(current_note + 12 * octave + root)
            movement = markov[current_step_pos % len(markov)]
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

    def get_notes(self):
        scale_notes = self.track.session.scale.get_value()
        root = self.track.session.root_note.get_value()
        step = self.next_step.get_value()
        current_note = self.current.get_value()
        scale_degree = current_note % 12
        octave = current_note // 12
        scale_size = len(scale_notes)
        try:
            current_scale_pos = scale_notes.index(scale_degree)
        except ValueError:
            current_scale_pos = 0
        print(f"gn1 {self.current} + {step} {current_scale_pos} {octave} {scale_notes} {root}")
        if abs(step) < 3:
            current_scale_pos += step
        # TODO: else
        if current_scale_pos >= scale_size:
            current_scale_pos -= scale_size
            octave += 1
        elif current_scale_pos < 0:
            current_scale_pos += scale_size
            octave -= 1
        new_note = scale_notes[current_scale_pos] + 12 * octave
        self.current.set_value(new_note, force=True)
        pitch_center = self.pitch.get_value()
        low, high = -3, 3
        if new_note > pitch_center + 24:
            high = 0
        elif new_note > pitch_center + 12:
            high = 2
        elif new_note < pitch_center - 24:
            low = 0
        elif new_note < pitch_center - 12:
            low = -2
        self.generate_next_step(low=low, high=high)
        # markov = [self.markov.get_value((self.current.get_value(), i)) for i in range(-3, 4)]
        # TODO: chord influence
        return [self.current.get_value()]

    def transpose_notes(self, candidates, *_a, **_kw):
        """
        Transpose notes based on pitch, ignore boundaries.
        """
        notes = []
        for candidate in candidates:
            note = candidate + 12 * (self.pitch.get_value() // 12)
            notes.append(int(note))
        return notes

    # For the GUI
    def steps_str(self):
        """
        Return the visual representation of steps.
        """
        steps = self.steps.get_value()
        phrase_length = len(self.get_positions())
        arrows = {1: "⇑", 2: "⤊", 3: "⟰", -1: "⇓", -2: "⤋", -3: "⟱", 0: "⇒"}
        return "  ".join(
            arrows[steps[i % len(steps)]] for i in range(phrase_length - 1)
        )

    def markov_str(self):
        """
        Return the visual representation of markov probabilities.
        """
        markov = [f"{int(self.markov.get_value((self.prev_step.get_value(), i))*100)}" for i in range(-3, 4)]
        return " ".join(markov)
        phrase_length = len(self.get_positions())
        arrows = {1: "⇑", 2: "⤊", 3: "⟰", -1: "⇓", -2: "⤋", -3: "⟱", 0: "⇒"}
        return "  ".join(
            arrows[markov[i % len(markov)]] for i in range(phrase_length - 1)
        )

    def melo_str(self):
        """
        Return the visual representation of the current melody.
        """
        return f"{self.prev_step}, {self.current}, {self.next_step}"
