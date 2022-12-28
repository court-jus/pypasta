"""
LowFrequencyOscillators allow to smoothly change a value over time.
"""

import math
import random

from pypastator.engine.field import EnumField, Field, StrField

WAVEFORMS = ["sinus", "squarish", "sincos", "saw", "triangle", "random"]


class LFO:
    """
    Basic LFO, sin waveform.
    """

    def __init__(self, destination, waveform, smoothness=0.6 * 127):
        self.destination = destination
        self.smoothness = Field(default=max(smoothness, 1))
        self.dest_name = StrField()
        self.rate = Field(default=1)
        self.depth = Field(default=10)
        self.waveform = EnumField(default=WAVEFORMS.index(waveform), choices=WAVEFORMS)
        self.last_random_time = 0
        self.last_random_value = 0
        self.target_value = 0
        self.running = True
        self.value = 0

    @property
    def waveform_str(self):
        """
        Return the name of the waveform.
        """
        return self.waveform.get_value()

    def save(self):
        """
        Save this LFO's attributes.
        """
        return {
            "waveform": self.waveform.get_value(),
            "smoothness": self.smoothness.get_value(),
            "attrname": self.dest_name.get_value(),
            "depth": self.depth.get_value(),
            "rate": self.rate.get_value(),
        }

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
        method_name = f"get_{self.waveform.get_value()}_value"
        if not hasattr(self, method_name):
            return 0
        return getattr(self, method_name)(ticks, rate)

    def get_sinus_value(self, ticks, rate):
        """
        Generate a sinus waveform.
        """
        return math.sin(ticks / rate)

    def get_squarish_value(self, ticks, rate):
        """
        Generate the squarish waveform.
        """
        smoothness = max(1, self.smoothness.get_value()) / 127
        return max(min(smoothness, math.sin(ticks / rate)), -smoothness) / smoothness

    def get_sincos_value(self, ticks, rate):
        """
        Generate the sincos waveform.
        """
        return (math.sin(ticks / rate) + math.cos(2 * ticks / rate)) / 2

    def get_saw_value(self, ticks, rate):
        """
        Generate the saw waveform.
        """
        return ((ticks / (2 * math.pi)) % rate) / rate * 2 - 1

    def get_triangle_value(self, ticks, rate):
        """
        Generate the triangle waveform.
        """
        return abs(((ticks / (2 * math.pi)) % rate) / rate * 2 - 1) * 2 - 1

    def get_random_value(self, ticks, rate):
        """
        Generate the random waveform.
        """
        if self.last_random_time == 0 or ticks - rate > self.last_random_time:
            self.target_value = random.random() * 2 - 1
            self.last_random_time = ticks
        elif abs(self.last_random_value - self.target_value) > 0:
            # smoothness 0 -> jump straight at target
            # smoothness 1 -> will reach target just before new target choice
            smoothness = max(1, self.smoothness.get_value()) / 127
            if (self.last_random_time + (rate * smoothness)) - ticks != 0:
                delta = (self.target_value - self.last_random_value) / (
                    (self.last_random_time + (rate * smoothness)) - ticks
                )
                self.last_random_value += delta
        return self.last_random_value
