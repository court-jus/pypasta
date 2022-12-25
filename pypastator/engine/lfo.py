"""
LowFrequencyOscillators allow to smoothly change a value over time.
"""

import math
import random

from pypastator.engine.field import Field, StrField


class LFO:
    """
    Basic LFO, sin waveform.
    """

    def __init__(self, destination):
        self.destination = destination
        self.dest_name = StrField()
        self.rate = Field(default=1)
        self.depth = Field(default=10)
        self.running = True
        self.value = 0

    def reset(self):
        """
        Reset destination's modulation value to 0.
        """
        self.running = False
        self.destination(0)

    def change_destination(self, new_destination, new_name):
        """
        Change this LFO's destination.
        """
        self.reset()
        self.destination = new_destination
        self.dest_name.set_value(new_name)
        self.running = True

    def midi_tick(self, ticks):
        """
        Calculate the LFO value, each tick.
        """
        if not self.running:
            return
        rate = self.rate.get_value() * 6
        depth = self.depth.get_value()
        value = self.get_value(ticks, rate)
        self.destination(int(value * depth))

    def get_value(self, ticks, rate):
        """
        Get the raw value of the LFO.
        """
        return math.sin(ticks / rate)


class SinCoSLFO(LFO):
    """
    A combination of a sin and cos twice as fast.
    """

    def get_value(self, ticks, rate):
        return (math.sin(ticks / rate) + math.cos(2 * ticks / rate)) / 2


class SawLFO(LFO):
    """
    A sawtooth waveform.
    """

    def get_value(self, ticks, rate):
        return ((ticks / (2 * math.pi)) % rate) / rate * 2 - 1


class TriangleLFO(LFO):
    """
    A triangle waveform.
    """

    def get_value(self, ticks, rate):
        return abs(((ticks / (2 * math.pi)) % rate) / rate * 2 - 1) * 2 - 1


class SquarishLFO(LFO):
    """
    Truncated sinwave.

    If smoothness is 1, that's a sinwave.
    """

    def __init__(self, destination, smoothness=0.6):
        self.smoothness = max(smoothness, 0.001)
        super().__init__(destination)

    def get_value(self, ticks, rate):
        return (
            max(min(self.smoothness, math.sin(ticks / rate)), -self.smoothness)
            / self.smoothness
        )


class SquareLFO(SquarishLFO):
    """
    Square (smoothness set to its minimal).
    """

    def __init__(self, destination):
        super().__init__(destination, smoothness=0)


class AlmostSinLFO(SquarishLFO):
    """
    Almost sinus (Squarish with smoothness set high).
    """

    def __init__(self, destination):
        super().__init__(destination, smoothness=0.8)


class RandomLFO(LFO):
    """
    Random value, can be smoothed over time to avoid big leaps.

    IDEA: the rate could be randomized too.
    """

    def __init__(self, destination, smoothness=0):
        self.smoothness = smoothness
        super().__init__(destination)
        self.last_random_time = 0
        self.last_random_value = 0
        self.target_value = 0

    def get_value(self, ticks, rate):
        if self.last_random_time == 0 or ticks - rate > self.last_random_time:
            self.target_value = random.random() * 2 - 1
            self.last_random_time = ticks
        # smoothness 0 -> jump straight at target
        # smoothness 1 -> will reach target just before new target choice
        elif abs(self.last_random_value - self.target_value) > 0:
            delta = (self.target_value - self.last_random_value) / (
                (self.last_random_time + (rate * self.smoothness)) - ticks
            )
            self.last_random_value += delta
        return self.last_random_value


class SmoothRandomLFO(RandomLFO):
    """
    Random value, smoothed over time to avoid big leaps.
    """

    def __init__(self, destination):
        super().__init__(destination, smoothness=0.7)


def get_lfo(destination, waveform="squarish", **kw):
    """
    Instantiate required LFO based on the waveform argument.
    """
    return {
        "squarish": SquarishLFO,
        "square": SquareLFO,
        "almostsin": AlmostSinLFO,
        "sinus": LFO,
        "sincos": SinCoSLFO,
        "saw": SawLFO,
        "triangle": TriangleLFO,
        "random": RandomLFO,
        "smoothrandom": SmoothRandomLFO,
    }[waveform](destination, **kw)
