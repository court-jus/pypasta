"""
Message shown at the bottom of the screen.

The message widget clears it self after a while.
"""
import pygame.midi

from pypastator.constants import BASE_WIDGET_HEIGHT, MESSAGE_FONT_SIZE, WIDGETS_MARGIN
from pypastator.widgets.label import Label

DEFAULT_MESSAGE = "Welcome to Pastator"
MESSAGE_DURATION = 2500


class Message(Label):
    """
    Message widget.
    """

    def __init__(self, *a, **kw):
        kw.setdefault("font_size", MESSAGE_FONT_SIZE)
        kw.setdefault("x", WIDGETS_MARGIN)
        kw.setdefault("y", 768 - BASE_WIDGET_HEIGHT - WIDGETS_MARGIN)
        kw.setdefault("w", 1024 - 2 * WIDGETS_MARGIN)
        kw.setdefault("text", DEFAULT_MESSAGE)
        super().__init__(*a, **kw)
        self.say(self.text)

    def midi_tick(self, timestamp):
        """
        Handle Midi tick.

        If the message has been shown for at least MESSAGE_DURATION, then hide it.
        """
        if self.shown_time + MESSAGE_DURATION <= timestamp:
            self.set_text(DEFAULT_MESSAGE)
            self.shade()

    def say(self, message):
        """
        Display said message and set shown_time.
        """
        self.set_text(message)
        self.highlight()
        self.shown_time = pygame.midi.time()
