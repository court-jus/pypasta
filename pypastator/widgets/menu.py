from engine.field import Field

from constants import (
    BUTTON_WIDTH,
    FONT_SIZE,
    KNOB_LABEL_SIZE,
    KNOB_SIZE,
    SLIDER_LABEL_SIZE,
    SLIDER_WIDTH,
    WIDGETS_MARGIN,
    BASE_WIDGET_HEIGHT,
)
from widgets.label import Label
from widgets.led import Led
from widgets.slider import Slider
from widgets.knob import Knob

WIDGET_LINE = BASE_WIDGET_HEIGHT + WIDGETS_MARGIN
LEFT_COL = WIDGETS_MARGIN * 2 + BUTTON_WIDTH
BIG_LABEL_W = SLIDER_WIDTH + BUTTON_WIDTH + WIDGETS_MARGIN


class Menu:
    def __init__(self, session):
        self.session = session
        self.visible = False
        self.current_track = None
        topy = 500
        self.session_widgets = {
            "scale_label": Label(
                text="Scale",
                y=topy,
                x=WIDGETS_MARGIN,
            ),
            "scale": Label(
                text="",
                y=topy,
                x=LEFT_COL,
                w=BIG_LABEL_W,
            ),
            "chord_label": Label(
                text="Chord",
                y=topy + WIDGET_LINE * 1,
                x=WIDGETS_MARGIN,
            ),
            "chord": Label(
                text="Chord",
                y=topy + WIDGET_LINE * 1,
                x=LEFT_COL,
                w=BIG_LABEL_W,
            ),
        }
        topy += WIDGET_LINE * 2
        self.track_widgets = {
            "engine_type": Label(
                text="Eng.",
                y=topy,
                x=LEFT_COL
                + SLIDER_WIDTH / 2
                + WIDGETS_MARGIN
                + SLIDER_LABEL_SIZE
                + WIDGETS_MARGIN,
                draw=False,
            ),
        }
        self.engine_widgets = {
            "track_id": Label(text="Trk #", y=topy, x=WIDGETS_MARGIN, draw=False),
            "midi_channel": Slider(
                y=topy,
                x=LEFT_COL,
                w=SLIDER_WIDTH / 2,
                label="Chan.",
                ratio=15,
                stripes=True,
                draw=False,
            ),
            "related_to": Label(
                text="RTo",
                y=topy,
                x=LEFT_COL
                + SLIDER_WIDTH / 2
                + WIDGETS_MARGIN
                + SLIDER_LABEL_SIZE
                + WIDGETS_MARGIN
                + BUTTON_WIDTH
                + WIDGETS_MARGIN,
                draw=False,
            ),
            "pattern_str": Label(
                text="P.",
                y=topy + WIDGET_LINE * 1,
                x=LEFT_COL,
                w=BIG_LABEL_W,
                draw=False,
            ),
            "pattern": Label(
                text="P.",
                y=topy + WIDGET_LINE * 1,
                x=WIDGETS_MARGIN,
                w=BUTTON_WIDTH,
                draw=False,
            ),
            "rythm_str": Label(
                text="R.",
                y=topy + WIDGET_LINE * 2,
                x=LEFT_COL,
                w=BIG_LABEL_W,
                draw=False,
            ),
            "rythm": Label(
                text="R.",
                y=topy + WIDGET_LINE * 2,
                x=WIDGETS_MARGIN,
                w=BUTTON_WIDTH,
                draw=False,
            ),
        }
        self.active_widget = None
        self.widgets_order = [
            "engine.midi_channel",
            "track.engine_type",
            "engine.related_to",
        ]

        # Hook session widgets
        self.session_widgets["scale"].hook(
            self.session,
            "scale",
            "menu",
            set_text=True,
            value_getter=lambda: self.session.scale_str,
        )
        self.session_widgets["chord"].hook(
            self.session,
            "scale",
            "scale_to_chord",
            set_text=True,
            value_getter=lambda: self.session.chord_str,
        )
        self.session_widgets["chord"].hook(
            self.session,
            "chord_type",
            "chord_to_chord",
            set_text=True,
            value_getter=lambda: self.session.chord_str,
        )

    def hide(self):
        self.visible = False
        self.current_track = None
        for widget in self.engine_widgets.values():
            widget.unhook()
            widget.hide()
        for widget in self.track_widgets.values():
            widget.unhook()
            widget.hide()

    def show(self, track, select_widget="engine.midi_channel"):
        if not track or not track.engine:
            return
        track_id = track.track_id
        self.visible = True
        self.engine_widgets["track_id"].set_text(f"Trk {track_id}")
        self.engine_widgets["midi_channel"].hook(track.engine, "midi_channel", "menu")
        self.track_widgets["engine_type"].hook(
            track,
            "engine_type",
            "menu",
            set_text=True,
            value_getter=lambda: track.engine_type_str,
        )
        self.engine_widgets["related_to"].hook(
            track.engine,
            "related_to",
            "menu",
            set_text=True,
            value_getter=lambda: track.engine.related_to_str,
        )
        self.engine_widgets["pattern_str"].hook(
            track.engine,
            "pattern",
            "pattern_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.engine_widgets["pattern_str"].hook(
            self.session,
            "scale",
            "scale_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.engine_widgets["pattern_str"].hook(
            self.session,
            "chord_type",
            "chord_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.engine_widgets["pattern_str"].hook(
            track.engine,
            "pitch",
            "pitch_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.engine_widgets["pattern_str"].hook(
            self.session,
            "current_chord",
            "current_chord_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.engine_widgets["pattern_str"].hook(
            track.engine,
            "pos",
            "pos_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.engine_widgets["pattern"].hook(
            track.engine, "pattern", "menu", set_text=True
        )
        self.engine_widgets["rythm_str"].hook(
            track.engine,
            "rythm",
            "rythm_to_rythm_str",
            set_text=True,
            value_getter=lambda: track.engine.rythm_str,
        )
        self.engine_widgets["rythm"].hook(track.engine, "rythm", "menu", set_text=True)
        self.current_track = track
        for widget in self.engine_widgets.values():
            widget.draw()
        for widget in self.track_widgets.values():
            widget.draw()
        self.activate_widget(select_widget)

    def activate_widget(self, widget_id):
        if self.active_widget is not None:
            category, widget = self.active_widget.split(".")
            if category == "engine":
                self.engine_widgets[widget].shade()
            elif category == "track":
                self.track_widgets[widget].shade()
        category, widget = widget_id.split(".")
        if category == "engine":
            self.engine_widgets[widget].highlight()
        elif category == "track":
            self.track_widgets[widget].highlight()
        self.active_widget = widget_id

    def activate_next(self, increment=1):
        if self.active_widget is None:
            widget = self.widgets_order[0]
        else:
            widget = self.widgets_order[
                (self.widgets_order.index(self.active_widget) + increment)
                % len(self.widgets_order)
            ]
        self.activate_widget(widget)

    def increment(self, increment=1):
        if self.active_widget is None or self.current_track is None:
            return
        category, widget = self.active_widget.split(".")
        if category == "track":
            field = getattr(self.current_track, widget)
        elif category == "engine":
            field = getattr(self.current_track.engine, widget)
        if isinstance(field, Field):
            field.increment(increment)

    def handle_click(self, pos):
        pass
        """
        for widget, callback in self.engine_widgets.values():
            widget.handle_click(pos, callback)
        """

    def handle_cc(self, cc, value):
        if not self.visible:
            return
        if cc == 3:
            self.activate_next()
        elif cc == 2:
            self.activate_next(-1)
        elif cc == 0:
            self.increment()
        elif cc == 1:
            self.increment(-1)
