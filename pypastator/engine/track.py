from constants import FONT_SIZE, KNOB_LABEL_SIZE, KNOB_SIZE, SLIDER_LABEL_SIZE, SLIDER_WIDTH, WIDGETS_MARGIN
from engine.arp import Arp
from widgets.led import Led
from widgets.slider import Slider
from widgets.knob import Knob

class Track:
    def __init__(self, track_id):
        self.track_id = track_id
        self.is_menu_opened = False
        sliders_right = WIDGETS_MARGIN * 3 + FONT_SIZE * 2 + SLIDER_WIDTH + SLIDER_LABEL_SIZE
        knob_size = KNOB_SIZE + KNOB_LABEL_SIZE + WIDGETS_MARGIN * 2
        y = WIDGETS_MARGIN + (FONT_SIZE + WIDGETS_MARGIN) * self.track_id
        self.arp = Arp()
        self.cc_controls = {
            8 + track_id: (Knob(y=y, x=sliders_right + knob_size * 2, label="Vel.", value=self.arp.basevel), self.arp.set_basevel),
            16 + track_id: (Knob(y=y, x=sliders_right + knob_size, label="Pat.", value=self.arp.pattern), self.arp.set_pattern),
            24 + track_id: (Knob(y=y, x=sliders_right, label="Rythm", value=self.arp.rythm), self.arp.set_rythm),
            32 + track_id: (Slider(y=y, x= FONT_SIZE * 2, label="Pitch", value=self.arp.pitch), self.arp.set_pitch),
            40 + track_id: (Led(y=y, value=True), self.arp.set_mute),
        }
        self.menu_widgets = {
            1: (Slider(y=500, x=FONT_SIZE * 2, label="Pitch", value=self.arp.pitch), self.arp.set_pitch),
        }
        for cc_control in self.cc_controls.values():
            cc_control[0].draw()

    def midi_tick(self, ticks, timestamp, chord):
        return self.arp.midi_tick(ticks, timestamp, chord)

    def handle_cc(self, cc, value):
        if cc in self.cc_controls:
            ctrl = self.cc_controls[cc]
            widget, callback = ctrl[:2]
            widget_value = callback(value)
            widget.value = widget_value
            widget.draw()
        if self.is_menu_opened and cc in self.menu_widgets:
            print("activate menu widget", cc)

    def menu(self):
        self.is_menu_opened = not self.is_menu_opened
        for widget in self.menu_widgets.values():
            if self.is_menu_opened:
                widget[0].draw()
            else:
                widget[0].hide()
        print(id(self), self.is_menu_opened, "Menu is", "opened" if self.is_menu_opened else "closed")

