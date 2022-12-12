from constants import FONT_SIZE, KNOB_LABEL_SIZE, KNOB_SIZE, SLIDER_LABEL_SIZE, SLIDER_WIDTH, WIDGETS_MARGIN
from engine.arp import Arp
from engine.chord import Chord
from engine.strum import Strum
from widgets.led import Led
from widgets.slider import Slider
from widgets.knob import Knob

class Track:
    def __init__(self, track_id):
        self.track_id = track_id
        self.is_menu_opened = False
        self.engine = None
        self.cc_controls = {}

    def set_type(self, track_type="arp"):
        sliders_right = WIDGETS_MARGIN * 3 + FONT_SIZE * 2 + SLIDER_WIDTH + SLIDER_LABEL_SIZE
        knob_size = KNOB_SIZE + KNOB_LABEL_SIZE + WIDGETS_MARGIN * 2
        y = WIDGETS_MARGIN + (FONT_SIZE + WIDGETS_MARGIN) * self.track_id
        if track_type == "arp":
            self.engine = Arp()
            self.cc_controls = {
                8 + self.track_id: (Knob(y=y, x=sliders_right + knob_size * 2, label="Vel.", value=self.engine.basevel), self.engine.set_basevel),
                16 + self.track_id: (Knob(y=y, x=sliders_right + knob_size, label="Pat.", value=self.engine.pattern), self.engine.set_pattern),
                24 + self.track_id: (Knob(y=y, x=sliders_right, label="Rythm", value=self.engine.rythm), self.engine.set_rythm),
                32 + self.track_id: (Slider(y=y, x= FONT_SIZE * 2, label="Pitch", value=self.engine.pitch), self.engine.set_pitch),
                40 + self.track_id: (Led(y=y, value=True), self.engine.set_mute),
            }
        elif track_type == "chord":
            self.engine = Chord()
            self.cc_controls = {
                8 + self.track_id: (Knob(y=y, x=sliders_right + knob_size * 2, label="Vel.", value=self.engine.basevel), self.engine.set_basevel),
                16 + self.track_id: (Knob(y=y, x=sliders_right + knob_size, label="Pat.", value=self.engine.pattern), self.engine.set_pattern),
                24 + self.track_id: (Knob(y=y, x=sliders_right, label="Rythm", value=self.engine.rythm), self.engine.set_rythm),
                32 + self.track_id: (Slider(y=y, x= FONT_SIZE * 2, label="Pitch", value=self.engine.pitch), self.engine.set_pitch),
                40 + self.track_id: (Led(y=y, value=True), self.engine.set_mute),
            }
        elif track_type == "strum":
            self.engine = Strum()
            self.cc_controls = {
                8 + self.track_id: (Knob(y=y, x=sliders_right + knob_size * 2, label="Vel.", value=self.engine.basevel), self.engine.set_basevel),
                16 + self.track_id: (Knob(y=y, x=sliders_right + knob_size, label="Pat.", value=self.engine.pattern), self.engine.set_pattern),
                24 + self.track_id: (Knob(y=y, x=sliders_right, label="Rythm", value=self.engine.rythm), self.engine.set_rythm),
                32 + self.track_id: (Slider(y=y, x= FONT_SIZE * 2, label="Pitch", value=self.engine.pitch), self.engine.set_pitch),
                40 + self.track_id: (Led(y=y, value=True), self.engine.set_mute),
            }
        self.menu_widgets = {
            1: (Slider(y=500, x=FONT_SIZE * 2, label="Pitch", value=self.engine.pitch, draw=False), self.engine.set_pitch),
        }

    def load(self, data):
        self.set_type(data.get("type", "arp"))
        self.engine.load(data)
        self.cc_controls[8 + self.track_id][0].set_value(self.engine.basevel)
        self.cc_controls[16 + self.track_id][0].set_value(self.engine.pattern)
        self.cc_controls[24 + self.track_id][0].set_value(self.engine.rythm)
        self.cc_controls[32 + self.track_id][0].set_value(self.engine.pitch)
        self.cc_controls[40 + self.track_id][0].set_value(not self.engine.mute)

    def midi_tick(self, ticks, timestamp, chord):
        if self.engine is not None:
            return self.engine.midi_tick(ticks, timestamp, chord)

    def handle_cc(self, cc, value):
        if cc in self.cc_controls:
            ctrl = self.cc_controls[cc]
            widget, callback = ctrl[:2]
            widget_value = callback(value)
            widget.set_value(widget_value)
        if self.is_menu_opened and cc in self.menu_widgets:
            print("activate menu widget", cc)

    def menu(self):
        self.is_menu_opened = not self.is_menu_opened
        for widget in self.menu_widgets.values():
            if self.is_menu_opened:
                widget[0].draw()
            else:
                widget[0].hide()

