"""
GUIs for then engine model.
"""
from pypastator.constants import (
    BIG_LABEL_W,
    BUTTON_WIDTH,
    ENGINE_CC_BASEVEL,
    ENGINE_CC_MUTE,
    ENGINE_CC_PATTERN,
    ENGINE_CC_PITCH,
    ENGINE_CC_RYTHM,
    ENGINE_CC_SELECT,
    KNOB_SIZE,
    LED_SIZE,
    SLIDER_WIDTH,
    WIDGET_LABEL_SIZE,
    WIDGET_LINE,
    WIDGETS_MARGIN,
)
from pypastator.widgets.gui.base import GUI
from pypastator.widgets.knob import Knob
from pypastator.widgets.label import Label
from pypastator.widgets.led import Led
from pypastator.widgets.separator import Separator
from pypastator.widgets.slider import Slider


class MainEngineGUI(GUI):
    """
    GUI containing the main engine controls.
    """

    def init_widgets(self):
        """
        Initialize widgets.
        """
        self.hideable = False
        # Leds
        pos_y = self.pos_y
        pos_x = WIDGETS_MARGIN
        # Menu Led
        self.widgets["menu"] = Led(x=pos_x, y=pos_y, emoji="⚙️")
        self.widgets[
            "menu"
        ].on_click = lambda _v: self.model.track.session.select_track(
            self.model.track.track_id
        )
        pos_x += LED_SIZE + WIDGETS_MARGIN
        # Active Led
        self.widgets["mute"] = Led(x=pos_x, y=pos_y, emoji="🔈")
        self.widgets["mute"].hook(self.model, "active", "engine_to_controls")
        self.widgets["mute"].on_click = self.model.active.increment
        pos_x += LED_SIZE + WIDGETS_MARGIN
        # Pitch slider
        self.widgets["pitch"] = Slider(x=pos_x, y=pos_y, label="Pitch")
        self.widgets["pitch"].hook(self.model, "pitch", "engine_to_controls")
        self.widgets["pitch"].on_click = lambda v: self.model.pitch.set_value(
            v, force=True
        )
        pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN + SLIDER_WIDTH + WIDGETS_MARGIN
        # Knobs
        # Rythm
        self.widgets["rythm"] = Knob(x=pos_x, y=pos_y, label="Rythm")
        self.widgets["rythm"].hook(self.model, "rythm", "engine_to_controls")
        self.widgets["rythm"].on_click = lambda v: self.model.rythm.set_value(
            v, force=True
        )
        pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN + KNOB_SIZE + WIDGETS_MARGIN
        # Pattern
        self.widgets["pattern"] = Knob(x=pos_x, y=pos_y, label="Pat.")
        self.widgets["pattern"].hook(self.model, "pattern", "engine_to_controls")
        self.widgets["pattern"].on_click = lambda v: self.model.pattern.set_value(
            v, force=True
        )
        pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN + KNOB_SIZE + WIDGETS_MARGIN
        # Velocity
        self.widgets["basevel"] = Knob(x=pos_x, y=pos_y, label="Vel.")
        self.widgets["basevel"].hook(self.model, "basevel", "engine_to_controls")
        self.widgets["basevel"].on_click = lambda v: self.model.basevel.set_value(
            v, force=True
        )

    def handle_cc(self, cc_channel, cc_number, cc_value):
        """
        Handle Midi CC events.
        """
        super().handle_cc(cc_channel, cc_number, cc_value)
        if cc_channel != 15:
            return
        if (cc_number - self.model.track.track_id) % 8 != 0:
            return
        ctrl = int((cc_number - self.model.track.track_id) / 8) - 1

        # Base velocity
        if ctrl == ENGINE_CC_BASEVEL:
            self.model.basevel.set_value(cc_value)
        # Pattern
        elif ctrl == ENGINE_CC_PATTERN:
            self.model.pattern.set_value(cc_value)
        # Rythm
        elif ctrl == ENGINE_CC_RYTHM:
            self.model.rythm.set_value(cc_value)
        # Pitch
        elif ctrl == ENGINE_CC_PITCH:
            self.model.pitch.set_value(cc_value)
        # Mute/unmute
        elif ctrl == ENGINE_CC_MUTE and cc_value == 127:
            self.model.active.increment()
        # Select this track
        elif ctrl == ENGINE_CC_SELECT and cc_value == 127:
            self.model.track.session.select_track(self.model.track.track_id)


class EngineDetailsGUI(GUI):
    """
    First detailed GUI for the engine model.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.default_widget = "midi_channel"
        self.activable_widgets = ["midi_channel", "engine_type"]

    def init_widgets(self):
        """
        Initialize widgets.
        """
        pos_y = self.pos_y
        self.widgets["separator"] = Separator(
            text="Track details", y=pos_y, visible=False
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        pos_x = WIDGETS_MARGIN
        # First row: track id, midi_channel, engine_type and related_to, LFO
        self.widgets["track_id"] = Label(
            text=f"Trk {self.model.track.track_id}", y=pos_y, x=pos_x, visible=False
        )
        pos_x += WIDGETS_MARGIN + BUTTON_WIDTH
        self.widgets["midi_channel"] = Slider(
            y=pos_y,
            x=pos_x,
            w=SLIDER_WIDTH / 2,
            label="Chan.",
            ratio=16,
            stripes=True,
            visible=False,
        )
        self.widgets["midi_channel"].hook(self.model, "midi_channel", "menu")
        self.widgets[
            "midi_channel"
        ].on_click = lambda v: self.model.midi_channel.set_value(v, force=True)
        pos_x += BUTTON_WIDTH + WIDGETS_MARGIN * 2 + SLIDER_WIDTH / 2
        self.widgets["engine_type"] = Label(
            text="Eng.", y=pos_y, x=pos_x, visible=False
        )
        self.widgets["engine_type"].hook(
            self.model.track,
            "engine_type",
            "menu",
            set_text=True,
            value_getter=lambda: self.model.track.engine_type_str,
        )
        self.widgets[
            "engine_type"
        ].on_click = lambda v: self.model.track.engine_type.increment()
        pos_x += WIDGETS_MARGIN + BUTTON_WIDTH
        self.widgets["related_to"] = Label(text="RTo", y=pos_y, x=pos_x, visible=False)
        self.widgets["related_to"].hook(
            self.model,
            "related_to",
            "menu",
            set_text=True,
            value_getter=lambda: self.model.related_to_str,
        )
        pos_x += WIDGETS_MARGIN + BUTTON_WIDTH
        # Second row: pattern number, pattern str
        pos_y += WIDGET_LINE
        pos_x = WIDGETS_MARGIN
        self.widgets["pattern"] = Label(
            text="P.", y=pos_y, x=pos_x, w=BUTTON_WIDTH, visible=False
        )
        self.widgets["pattern"].hook(self.model, "pattern", "menu", set_text=True)
        pos_x += WIDGETS_MARGIN + BUTTON_WIDTH
        self.widgets["pattern_str"] = Label(
            text="P.", y=pos_y, x=pos_x, w=BIG_LABEL_W, visible=False
        )
        self.widgets["pattern_str"].hook(
            self.model,
            "pattern",
            "pattern_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        self.widgets["pattern_str"].hook(
            self.model.track.session,
            "scale",
            "scale_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        self.widgets["pattern_str"].hook(
            self.model.track.session,
            "chord_type",
            "chord_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        self.widgets["pattern_str"].hook(
            self.model,
            "pitch",
            "pitch_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        self.widgets["pattern_str"].hook(
            self.model,
            "gravity",
            "gravity_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        self.widgets["pattern_str"].hook(
            self.model.track.session,
            "current_chord",
            "current_chord_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        self.widgets["pattern_str"].hook(
            self.model,
            "pos",
            "pos_to_pattern_str",
            set_text=True,
            value_getter=lambda: self.model.pattern_str,
        )
        # Third row: rythm number, rythm str
        pos_y += WIDGET_LINE
        pos_x = WIDGETS_MARGIN
        self.widgets["rythm"] = Label(
            text="R.", y=pos_y, x=pos_x, w=BUTTON_WIDTH, visible=False
        )
        self.widgets["rythm"].hook(self.model, "rythm", "menu", set_text=True)
        pos_x += WIDGETS_MARGIN + BUTTON_WIDTH
        self.widgets["rythm_str"] = Label(
            text="R.", y=pos_y, x=pos_x, w=BIG_LABEL_W, visible=False
        )
        self.widgets["rythm_str"].hook(
            self.model,
            "rythm",
            "rythm_to_rythm_str",
            set_text=True,
            value_getter=lambda: self.model.rythm_str,
        )

    def increment(self, increment=1):
        """
        Increment/decrement the value behind the currently active widget.
        """
        if not self.visible:
            return
        if self.active_widget == "engine_type":
            self.model.track.engine_type.increment(increment)
        else:
            super().increment(increment=increment)


class LFOGUI(GUI):
    """
    GUI to manage LFOs.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.default_widget = "add_lfo"
        self.activable_widgets = [
            "add_lfo",
        ]

    def init_widgets(self):
        """
        Initialize widgets.
        """
        pos_y = self.pos_y
        self.widgets["separator"] = Separator(
            text="Low Frequency Oscillators", y=pos_y, visible=False
        )
        pos_y += WIDGET_LINE + WIDGETS_MARGIN
        pos_x = WIDGETS_MARGIN
        self.widgets["add_lfo"] = Label(text="Add", y=pos_y, x=pos_x, visible=False)
        self.widgets["add_lfo"].on_click = lambda _v: self.increment(widget="add_lfo")
        pos_y += WIDGET_LINE
        self.update_lfo_widgets()

    def update_lfo_widgets(self):
        """
        For each LFO, add a line of widgets (or update it).
        """
        pos_y = self.pos_y + 2 * WIDGET_LINE + WIDGETS_MARGIN
        for key in list(self.widgets.keys()):
            if key.startswith("lfo:"):
                widget = self.widgets.pop(key)
                widget.hide()
                widget.unhook()
                if key in self.activable_widgets:
                    self.activable_widgets.remove(key)
        for key, lfo in enumerate(self.model.lfos):
            pos_x = WIDGETS_MARGIN
            self.widgets[f"lfo:{key}:label"] = Label(
                text=f"LFO {key}", x=pos_x, y=pos_y, visible=False
            )
            pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN
            widget_key = f"lfo:{key}:destination"
            self.widgets[widget_key] = Label(
                text=f"dest{key}", x=pos_x, y=pos_y, visible=False
            )
            self.widgets[widget_key].hook(lfo, "dest_name", "lfo_menu", set_text=True)
            self.widgets[widget_key].on_click = self.make_callback(key, "destination")
            self.activable_widgets.append(widget_key)
            pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN
            widget_key = f"lfo:{key}:rate"
            self.widgets[widget_key] = Label(
                text=f"rate{key}", x=pos_x, y=pos_y, visible=False
            )
            self.widgets[widget_key].hook(lfo, "rate", "lfo_menu", set_text=True)
            self.widgets[widget_key].on_click = self.make_callback(key, "rate")
            self.activable_widgets.append(widget_key)
            pos_x += WIDGET_LABEL_SIZE + WIDGETS_MARGIN
            widget_key = f"lfo:{key}:depth"
            self.widgets[widget_key] = Label(
                text=f"depth{key}", x=pos_x, y=pos_y, visible=False
            )
            self.widgets[widget_key].hook(lfo, "depth", "lfo_menu", set_text=True)
            self.widgets[widget_key].on_click = self.make_callback(key, "depth")
            self.activable_widgets.append(widget_key)
            pos_y += WIDGET_LINE

    def show(self):
        self.update_lfo_widgets()
        super().show()

    def make_callback(self, lfo_number, attrname):
        """
        Prepare a callback for the on click event.
        """
        def callback(_val):
            self.apply_increment(lfo_number, attrname)

        return callback

    def apply_increment(self, lfo_number, attrname, increment=1):
        """
        Apply an increment to an LFO field.
        """
        lfo = self.model.lfos[int(lfo_number)]
        if attrname == "destination":
            destinations = ["pitch", "rythm", "pattern", "basevel"]
            current_destination = destinations.index(lfo.dest_name.get_value())
            new_destination_name = destinations[
                (current_destination + increment) % len(destinations)
            ]
            new_destination = getattr(self.model, new_destination_name).set_modulation
            lfo.change_destination(new_destination, new_destination_name)
        else:
            field = getattr(lfo, attrname)
            field.increment(increment)

    def increment(self, increment=1, widget=None):
        """
        Handle specifics.
        """
        active_widget = widget if widget is not None else self.active_widget
        if active_widget == "add_lfo":
            self.model.add_lfo(rate=1)
            if self.visible:
                self.show()
        elif active_widget.startswith("lfo:"):
            lfo_number = active_widget.split(":")[1]
            attrname = active_widget.split(":")[2]
            self.apply_increment(lfo_number, attrname, increment)
