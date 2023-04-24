"""
GUI that appear when the mouse moves.
"""
import time

from pypastator.constants import BLUE, CHORDS_MODE_MANUAL_RECORD, CHORDS_MODE_PROGRESSION, LED_SIZE, WIDGET_LINE, WIDGETS_MARGIN
from pypastator.widgets.gui.base import GUI
from pypastator.widgets.led import Led

MOUSE_GUI_DURATION = 1


class MouseGUI(GUI):
    """
    Mouse GUI for when a MIDI controller is not available.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.shown_time = None

    def init_widgets(self):
        """
        Initialize GUI's widgets.
        """
        kwargs = dict(visible=False, bcolor_on=BLUE, bcolor_off=BLUE)
        self.widgets["add_track"] = Led(emoji="➕", **kwargs)
        self.widgets["add_track"].on_click = lambda _v, _b: self.add_track_callback()
        self.widgets["save"] = Led(emoji="⚙️", **kwargs)
        self.widgets["save"].on_click = lambda _v, _b: self.model.settings_menu.show()
        self.widgets["record"] = Led(emoji="⏺️", **kwargs)
        self.widgets["record"].on_click = lambda _v, _b: self.model.set_chords_mode(CHORDS_MODE_MANUAL_RECORD)
        self.widgets["stop_record"] = Led(emoji="⏹️", **kwargs)
        self.widgets["stop_record"].on_click = lambda _v, _b: self.model.set_chords_mode(CHORDS_MODE_PROGRESSION)

    def add_track_callback(self):
        """
        Method called when clicking the "+" button.
        """
        self.model.add_track()
        self.update_widgets()

    def update_widgets(self):
        """
        Update widgets position or details.
        """
        self.make_row(
            self.widgets.values(),
            0,
            pos_y=WIDGET_LINE * (len(self.model.tracks.keys())) + WIDGETS_MARGIN,
            width=(LED_SIZE + WIDGETS_MARGIN) * len(self.widgets.keys())
            - WIDGETS_MARGIN,
        )

    def show(self):
        """
        Show this GUI and handle it's timeout to hide.
        """
        if self.visible:
            return
        super().show()
        self.update_widgets()
        self.shown_time = time.time()

    def handle_tick(self):
        """
        Handle tick.

        If the message has been shown for at least MESSAGE_DURATION, then hide it.
        """
        super().handle_tick()
        timestamp = time.time()
        if (
            self.shown_time is not None
            and self.shown_time + MOUSE_GUI_DURATION <= timestamp
        ):
            for widget in self.widgets.values():
                if widget.is_hovered():
                    return
            self.hide()
            self.shown_time = None
