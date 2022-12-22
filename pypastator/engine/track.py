"""
Track holds the details about the musical engine of a particular track.
"""
import sys

from pypastator.constants import (
    BASE_WIDGET_HEIGHT,
    ENGINE_TYPE_ARP,
    ENGINE_TYPE_CHORD,
    ENGINE_TYPE_STRUM,
    ENGINE_TYPES,
    KNOB_SIZE,
    LED_SIZE,
    SLIDER_WIDTH,
    WIDGET_LABEL_SIZE,
    WIDGETS_MARGIN,
)
from pypastator.engine.arp import Arp
from pypastator.engine.chord import Chord
from pypastator.engine.field import EnumField
from pypastator.engine.strum import Strum
from pypastator.widgets.knob import Knob
from pypastator.widgets.led import Led
from pypastator.widgets.slider import Slider


class Track:
    """
    Definition of a track.
    """

    def __init__(self, track_id, session):
        self.track_id = track_id
        self.session = session
        self.engine = None
        self.engine_type = EnumField(choices=ENGINE_TYPES)
        sliders_left = WIDGETS_MARGIN * 3 + LED_SIZE * 2
        sliders_right = (
            sliders_left + WIDGET_LABEL_SIZE + SLIDER_WIDTH + WIDGETS_MARGIN * 2
        )
        knob_size = KNOB_SIZE + WIDGET_LABEL_SIZE + WIDGETS_MARGIN * 2
        topy = WIDGETS_MARGIN + (BASE_WIDGET_HEIGHT + WIDGETS_MARGIN) * self.track_id
        if "pytest" in sys.modules:
            self.widgets = {}
        else:
            self.widgets = {
                "basevel": Knob(y=topy, x=sliders_right + knob_size * 2, label="Vel."),
                "pattern": Knob(y=topy, x=sliders_right + knob_size, label="Pat."),
                "rythm": Knob(y=topy, x=sliders_right, label="Rythm"),
                "pitch": Slider(y=topy, x=sliders_left, label="Pitch"),
                "active": Led(y=topy, x=WIDGETS_MARGIN * 2 + LED_SIZE, emoji="🔈"),
            }
        self.cc_controls = {}
        self.engine_type.hook(self.set_type, "track_set_type")

    @property
    def engine_type_str(self):
        """
        Get the str representation of the engine type.
        """
        return self.engine_type.str_value()

    def set_type(self, engine_type=ENGINE_TYPE_ARP):
        """
        Set the type of engine used by the track.
        """
        change = self.engine is not None
        data = {}
        if change:
            data = self.engine.save()
            for evt in self.engine.stop():
                self.session.pasta.emit_out_event(evt)
            for widget in self.widgets.values():
                widget.unhook()
        if engine_type == ENGINE_TYPE_ARP:
            self.engine = Arp(self)
        elif engine_type == ENGINE_TYPE_CHORD:
            self.engine = Chord(self)
        elif engine_type == ENGINE_TYPE_STRUM:
            self.engine = Strum(self)
        if change:
            self.engine.load(data)
            self.engine_to_controls()
            if self.session.menu.visible:
                self.session.menu.show(self, "track.engine_type")

    def engine_to_controls(self):
        """
        Based on the engine type, hook controls.
        """
        for attrname, widget in self.widgets.items():
            widget.hook(self.engine, attrname, "engine_to_controls")
        self.cc_controls[8 + self.track_id] = self.engine.basevel.set_value
        self.cc_controls[16 + self.track_id] = self.engine.pattern.set_value
        self.cc_controls[24 + self.track_id] = self.engine.rythm.set_value
        self.cc_controls[32 + self.track_id] = self.engine.pitch.set_value
        self.cc_controls[40 + self.track_id] = (
            lambda v: self.engine.active.increment() if v == 127 else False
        )
        self.widgets["basevel"].on_click = self.engine.basevel.set_value
        self.widgets["pattern"].on_click = self.engine.pattern.set_value
        self.widgets["rythm"].on_click = self.engine.rythm.set_value
        self.widgets["pitch"].on_click = self.engine.pitch.set_value
        self.widgets["active"].on_click = self.engine.active.increment

    def load(self, data):
        """
        Load a track from data.
        """
        engine_type = ENGINE_TYPES.index(data.get("type", "arp"))
        self.engine_type.set_value(engine_type)
        self.engine.load(data)
        self.engine_to_controls()

    def midi_tick(self, ticks, timestamp, chord):
        """
        Handle Midi tick event.
        """
        if self.engine is not None:
            return self.engine.midi_tick(ticks, timestamp, chord)
        return []

    def handle_cc(self, cc_number, value):
        """
        Handle Midi CC event.
        """
        if cc_number in self.cc_controls:
            callback = self.cc_controls[cc_number]
            callback(value)

    def handle_click(self, pos):
        """
        Pass click event to this track's widgets.
        """
        for widget in self.widgets.values():
            widget.handle_click(pos)
