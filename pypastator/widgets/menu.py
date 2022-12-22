"""
Handle menu visuals and interaction.
"""
from pypastator.constants import (
    BASE_WIDGET_HEIGHT,
    BUTTON_WIDTH,
    SLIDER_WIDTH,
    WIDGET_LABEL_SIZE,
    WIDGETS_MARGIN,
)
from pypastator.engine.field import Field
from pypastator.widgets.label import Label
from pypastator.widgets.slider import Slider

WIDGET_LINE = BASE_WIDGET_HEIGHT + WIDGETS_MARGIN
LEFT_COL = WIDGETS_MARGIN * 2 + BUTTON_WIDTH
BIG_LABEL_W = SLIDER_WIDTH + BUTTON_WIDTH + WIDGETS_MARGIN


class Menu:
    """
    Definition of the menu.
    """

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
                + WIDGET_LABEL_SIZE
                + WIDGETS_MARGIN,
                visible=False,
            ),
            "track_id": Label(text="Trk #", y=topy, x=WIDGETS_MARGIN, visible=False),
            "midi_channel": Slider(
                y=topy,
                x=LEFT_COL,
                w=SLIDER_WIDTH / 2,
                label="Chan.",
                ratio=15,
                stripes=True,
                visible=False,
            ),
            "related_to": Label(
                text="RTo",
                y=topy,
                x=LEFT_COL
                + SLIDER_WIDTH / 2
                + WIDGETS_MARGIN
                + WIDGET_LABEL_SIZE
                + WIDGETS_MARGIN
                + BUTTON_WIDTH
                + WIDGETS_MARGIN,
                visible=False,
            ),
            "pattern_str": Label(
                text="P.",
                y=topy + WIDGET_LINE * 1,
                x=LEFT_COL,
                w=BIG_LABEL_W,
                visible=False,
            ),
            "pattern": Label(
                text="P.",
                y=topy + WIDGET_LINE * 1,
                x=WIDGETS_MARGIN,
                w=BUTTON_WIDTH,
                visible=False,
            ),
            "rythm_str": Label(
                text="R.",
                y=topy + WIDGET_LINE * 2,
                x=LEFT_COL,
                w=BIG_LABEL_W,
                visible=False,
            ),
            "rythm": Label(
                text="R.",
                y=topy + WIDGET_LINE * 2,
                x=WIDGETS_MARGIN,
                w=BUTTON_WIDTH,
                visible=False,
            ),
        }
        self.active_widget = None
        self.widgets_order = [
            "track.midi_channel",
            "track.engine_type",
            "track.related_to",
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
        self.session_widgets["chord"].hook(
            self.session,
            "current_chord",
            "current_chord_to_chord",
            set_text=True,
            value_getter=lambda: self.session.chord_str,
        )

    def hide(self):
        """
        Hide the menu and unhook all widgets.
        """
        self.visible = False
        self.current_track = None
        for widget in self.track_widgets.values():
            widget.unhook()
            widget.hide()

    def show(self, track, select_widget="track.midi_channel"):
        """
        Show the menu for a specific track.
        """
        if not track or not track.engine:
            return
        track_id = track.track_id
        self.visible = True
        self.track_widgets["track_id"].set_text(f"Trk {track_id}")
        self.track_widgets["midi_channel"].hook(track.engine, "midi_channel", "menu")
        self.track_widgets["engine_type"].hook(
            track,
            "engine_type",
            "menu",
            set_text=True,
            value_getter=lambda: track.engine_type_str,
        )
        self.track_widgets[
            "engine_type"
        ].on_click = lambda v: track.engine_type.increment()
        self.track_widgets["related_to"].hook(
            track.engine,
            "related_to",
            "menu",
            set_text=True,
            value_getter=lambda: track.engine.related_to_str,
        )
        self.track_widgets["pattern_str"].hook(
            track.engine,
            "pattern",
            "pattern_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.track_widgets["pattern_str"].hook(
            self.session,
            "scale",
            "scale_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.track_widgets["pattern_str"].hook(
            self.session,
            "chord_type",
            "chord_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.track_widgets["pattern_str"].hook(
            track.engine,
            "pitch",
            "pitch_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.track_widgets["pattern_str"].hook(
            self.session,
            "current_chord",
            "current_chord_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.track_widgets["pattern_str"].hook(
            track.engine,
            "pos",
            "pos_to_pattern_str",
            set_text=True,
            value_getter=lambda: track.engine.pattern_str,
        )
        self.track_widgets["pattern"].hook(
            track.engine, "pattern", "menu", set_text=True
        )
        self.track_widgets["rythm_str"].hook(
            track.engine,
            "rythm",
            "rythm_to_rythm_str",
            set_text=True,
            value_getter=lambda: track.engine.rythm_str,
        )
        self.track_widgets["rythm"].hook(track.engine, "rythm", "menu", set_text=True)
        self.current_track = track
        for widget in self.track_widgets.values():
            widget.show()
        self.activate_widget(select_widget)

    def activate_widget(self, widget_id):
        """
        Activate a widget for arrows manipulation.
        """
        if self.active_widget is not None:
            widget = self.active_widget.split(".")[1]
            self.track_widgets[widget].shade()
        widget = widget_id.split(".")[1]
        self.track_widgets[widget].highlight()
        self.active_widget = widget_id

    def activate_next(self, increment=1):
        """
        Activate next/prev widget in order.
        """
        if self.active_widget is None:
            widget = self.widgets_order[0]
        else:
            widget = self.widgets_order[
                (self.widgets_order.index(self.active_widget) + increment)
                % len(self.widgets_order)
            ]
        self.activate_widget(widget)

    def increment(self, increment=1):
        """
        Increment/decrement the value behind the currently active widget.
        """
        if self.active_widget is None or self.current_track is None:
            return
        widget = self.active_widget.split(".")[1]
        field = getattr(self.current_track.engine, widget) if hasattr(self.current_track.engine, widget) else getattr(self.current_track, widget)
        if isinstance(field, Field):
            field.increment(increment)

    def handle_click(self, pos):
        """
        Handle click events.
        """
        for widget in list(self.track_widgets.values()) + list(
            self.session_widgets.values()
        ):
            widget.handle_click(pos)

    def handle_cc(self, cc_number):
        """
        Handle Midi CC events.
        """
        if not self.visible:
            return
        if cc_number == 3:
            self.activate_next()
        elif cc_number == 2:
            self.activate_next(-1)
        elif cc_number == 0:
            self.increment()
        elif cc_number == 1:
            self.increment(-1)
