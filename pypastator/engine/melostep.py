"""
Melostep Engine.

It creates a melody by following steps, skips and leaps
"""
import random

from pypastator.constants import BAR
from pypastator.engine.field import DictField, Field
from pypastator.engine.melobase import Melobase
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

class Melostep(Melobase):
    """
    Melostep Engine.
    
    Uses a kind of Markov Chain mechanism to choose the next step.
    """

    def __init__(self, track):
        # markov represents the probabilities to go from one step type to another
        self.markov = DictField(default=DEFAULT_MARKOV.copy())
        self.prev_step = Field(default=0)
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

    def reset_melo(self):
        """
        Reset the current set of random choices.
        """
        melody = self.generate_new_melody()
        self.current_melo.set_value(melody)
        return melody

    def generate_next_step(self):
        """
        Generate the next step based on current step and markov prob.
        """
        src = self.prev_step.get_value()
        prob = [self.markov.get_value((src, dst)) for dst in range(-3, 4)]
        next = random.choices(range(-3, 4), weights=prob)
        return next

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

    def evolve_melo(self):
        """
        Take current melo and slighty change it.
        """
        self.reset_melo()
        current = self.get_choices()
        return current

    def get_choices(self):
        """
        Get the possible choices for melostep to pick from.
        """
        current_value = self.current_melo.get_value()
        if current_value:
            return current_value
        return self.reset_melo()

    def get_candidate_notes(self):
        return self.get_choices()

    def transpose_notes(self, candidates, *_a, **_kw):
        """
        Transpose notes based on pitch, ignore boundaries.
        """
        notes = []
        for candidate in candidates:
            note = candidate + 12 * (self.pitch.get_value() // 12)
            notes.append(int(note))
        return notes

    def midi_tick(self, ticks, timestamp, chord_number):
        """
        Trigger melostep evolution based on ticks.
        """
        tick_evolution = self.change_frequency.get_value()
        if ticks % BAR == 0:
            # Always start bar at the start of the melo
            self.pos.set_value(0)
        if ticks % tick_evolution == 0:
            self.evolve_melo()
        return super().midi_tick(ticks, timestamp, chord_number)

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
        markov = self.markov.get_value()
        phrase_length = len(self.get_positions())
        arrows = {1: "⇑", 2: "⤊", 3: "⟰", -1: "⇓", -2: "⤋", -3: "⟱", 0: "⇒"}
        return "  ".join(
            arrows[markov[i % len(markov)]] for i in range(phrase_length - 1)
        )

    def melo_str(self):
        """
        Return the visual representation of the current melody.
        """
        current_value = self.current_melo.get_value()
        if current_value:
            return " ".join(
                f"{car:2}" for car in current_value[: len(self.get_positions())]
            )
        return "..."
