"""
Message shown at the bottom of the screen.

The message widget clears it self after a while.
"""
import time

from pypastator.constants import (
    BASE_WIDGET_HEIGHT,
    SCR_HEIGHT,
    SCR_WIDTH,
    WIDGETS_MARGIN,
)
from pypastator.widgets.label import Label

DEFAULT_MESSAGE = "Welcome to Pastator"
MESSAGE_DURATION = 2.5


class Message(Label):
    """
    Message widget.
    """

    def __init__(self, *a, **kw):
        kw.setdefault("pos_x", WIDGETS_MARGIN)
        kw.setdefault("pos_y", SCR_HEIGHT - BASE_WIDGET_HEIGHT - WIDGETS_MARGIN)
        kw.setdefault("width", SCR_WIDTH - 2 * WIDGETS_MARGIN)
        kw.setdefault("text", DEFAULT_MESSAGE)
        super().__init__(*a, **kw)
        self.shown_time = None
        self.say(self.text)

    def get_font(self):
        """
        Gather the font to be used.
        """
        return self.msg_font

    def handle_tick(self):
        """
        Handle tick.

        If the message has been shown for at least MESSAGE_DURATION, then hide it.
        """
        timestamp = time.time()
        if (
            self.shown_time is not None
            and self.shown_time + MESSAGE_DURATION <= timestamp
        ):
            self.set_text(DEFAULT_MESSAGE)
            self.shade()
            self.shown_time = None

    def say(self, message):
        """
        Display said message and set shown_time.
        """
        self.set_text(message)
        self.highlight()
        self.redraw()
        self.shown_time = time.time()
