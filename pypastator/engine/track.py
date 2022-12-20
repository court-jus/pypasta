from constants import (
    BUTTON_WIDTH,
    FONT_SIZE,
    BASE_WIDGET_HEIGHT,
    KNOB_LABEL_SIZE,
    KNOB_SIZE,
    SLIDER_LABEL_SIZE,
    SLIDER_WIDTH,
    WIDGETS_MARGIN,
)
from engine.arp import Arp
from engine.chord import Chord
from engine.strum import Strum
from engine.field import EnumField
from widgets.label import Label
from widgets.led import Led
from widgets.slider import Slider
from widgets.knob import Knob


class Track:
    def __init__(self, track_id, session):
        self.track_id = track_id
        self.session = session
        self.engine = None
        self.engine_type = EnumField(choices=["arp", "chord", "strum"])
        self.engine_type.hook(
            lambda val: self.set_type(self.engine_type_str), "track_set_type"
        )
        sliders_right = (
            WIDGETS_MARGIN * 4 + FONT_SIZE * 3 + SLIDER_WIDTH + SLIDER_LABEL_SIZE
        )
        sliders_left = WIDGETS_MARGIN + FONT_SIZE * 3
        knob_size = KNOB_SIZE + KNOB_LABEL_SIZE + WIDGETS_MARGIN * 2
        y = WIDGETS_MARGIN + (BASE_WIDGET_HEIGHT + WIDGETS_MARGIN) * self.track_id
        self.widgets = {
            "basevel": Knob(y=y, x=sliders_right + knob_size * 2, label="Vel."),
            "pattern": Knob(y=y, x=sliders_right + knob_size, label="Pat."),
            "rythm": Knob(y=y, x=sliders_right, label="Rythm"),
            "pitch": Slider(y=y, x=sliders_left, label="Pitch"),
            "active": Led(y=y, x=WIDGETS_MARGIN * 2 + FONT_SIZE, emoji="🔈"),
        }
        self.cc_controls = {}

    @property
    def engine_type_str(self):
        return self.engine_type.str_value()

    def set_type(self, engine_type="arp"):
        change = self.engine is not None
        data = {}
        if change:
            data = self.engine.save()
            for evt in self.engine.stop():
                self.session.pasta.emit_out_event(evt)
            for widget in self.widgets.values():
                widget.unhook()
        if engine_type == "arp":
            self.engine = Arp(self)
        elif engine_type == "chord":
            self.engine = Chord(self)
        elif engine_type == "strum":
            self.engine = Strum(self)
        if change:
            self.engine.load(data)
            self.engine_to_controls()
            if self.session.menu.visible:
                self.session.menu.show(self, "track.engine_type")

    def engine_to_controls(self):
        for attrname, widget in self.widgets.items():
            widget.hook(self.engine, attrname, "engine_to_controls")
        self.cc_controls[8 + self.track_id] = self.engine.basevel.set_value
        self.cc_controls[16 + self.track_id] = self.engine.pattern.set_value
        self.cc_controls[24 + self.track_id] = self.engine.rythm.set_value
        self.cc_controls[32 + self.track_id] = self.engine.pitch.set_value
        self.cc_controls[40 + self.track_id] = (
            lambda v: self.engine.active.increment() if v == 127 else False
        )

    def load(self, data):
        self.set_type(data.get("type", "arp"))
        self.engine.load(data)
        self.engine_to_controls()

    def midi_tick(self, ticks, timestamp, chord):
        if self.engine is not None:
            return self.engine.midi_tick(ticks, timestamp, chord)

    def handle_cc(self, cc, value):
        if cc in self.cc_controls:
            callback = self.cc_controls[cc]
            callback(value)

    def handle_click(self, pos):
        for widget, callback in self.cc_controls.values():
            widget.handle_click(pos, callback)
