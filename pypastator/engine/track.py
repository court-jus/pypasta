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
            self.controls = []
        else:
            self.controls = [
                {
                    "widget": Knob(y=topy, x=sliders_right + knob_size * 2, label="1"),
                    "current_page": 0,
                    "pages": [
                        {
                            "label": "Vel.",
                            "attrname": "basevel",
                        },
                        {
                            "label": "Grvt",
                            "attrname": "gravity",
                        },
                    ],
                },
                {
                    "widget": Knob(y=topy, x=sliders_right + knob_size, label="2"),
                    "current_page": 0,
                    "pages": [
                        {
                            "label": "Pat.",
                            "attrname": "pattern",
                        }
                    ],
                },
                {
                    "widget": Knob(y=topy, x=sliders_right, label="3"),
                    "current_page": 0,
                    "pages": [
                        {
                            "label": "Rythm",
                            "attrname": "rythm",
                        }
                    ],
                },
                {
                    "widget": Slider(y=topy, x=sliders_left, label="4"),
                    "current_page": 0,
                    "pages": [
                        {
                            "label": "Pitch",
                            "attrname": "pitch",
                        }
                    ],
                },
                {
                    "widget": Led(y=topy, x=WIDGETS_MARGIN * 2 + LED_SIZE, emoji="🔈"),
                    "current_page": 0,
                    "pages": [
                        {
                            "attrname": "active",
                            "setter": "increment",
                            "cc_value_match": lambda cc_value: cc_value == 127,
                        }
                    ],
                },
            ]
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
            for widget in [ctrl["widget"] for ctrl in self.controls]:
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

    def setup_control(self, ctrl):
        """
        Setup a control based on its current_page.
        """
        widget = ctrl["widget"]
        page = ctrl["pages"][ctrl["current_page"]]
        label = page.get("label")
        attrname = page["attrname"]
        if label:
            widget.set_label(label)
        widget.hook(self.engine, attrname, "engine_to_controls")
        field = getattr(self.engine, attrname)
        setter = page.get("setter", "set_value")
        widget.on_click = getattr(field, setter)

    def engine_to_controls(self):
        """
        Based on the engine type, hook controls.
        """
        for ctrl in self.controls:
            self.setup_control(ctrl)

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
        if cc_number in (2, 3):
            page_change = cc_number * 2 - 5  # 2 -> -1, 3 -> 1
            for ctrl in self.controls:
                previous = ctrl["current_page"]
                next = (ctrl["current_page"] + page_change) % len(ctrl["pages"])
                if previous != next:
                    ctrl["current_page"] = next
                    self.setup_control(ctrl)
        elif (cc_number - self.track_id) % 8 == 0:
            ctrl = self.controls[int((cc_number - self.track_id) / 8) - 1]
            page = ctrl["pages"][ctrl["current_page"]]
            if "cc_value_match" in page and not page["cc_value_match"](value):
                return
            attrname = page["attrname"]
            field = getattr(self.engine, attrname)
            setter = page.get("setter", "set_value")
            getattr(field, setter)(value)

    def handle_click(self, pos):
        """
        Pass click event to this track's widgets.
        """
        for widget in [ctrl["widget"] for ctrl in self.controls]:
            widget.handle_click(pos)
