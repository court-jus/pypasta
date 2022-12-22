"""
GUI widgets.
"""

import pygame

from pypastator.constants import (
    BASE_WIDGET_HEIGHT,
    BASE_WIDGET_WIDTH,
    BLACK,
    DARK_GRAY,
    EMOJI_FONT_NAME,
    EMOJI_FONT_SIZE,
    FONT_NAME,
    FONT_SIZE,
    LIGHT_GRAY,
    SMALL_FONT_NAME,
    SMALL_FONT_SIZE,
    WIDGETS_MARGIN,
)
from pypastator.engine.field import Field


class BaseWidget:
    """
    Base class for all widgets.
    """

    def __init__(
        self,
        *a,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=BASE_WIDGET_WIDTH,
        h=BASE_WIDGET_HEIGHT,
        x=WIDGETS_MARGIN,
        y=WIDGETS_MARGIN,
        on_click=None,
        value=None,
        visible=True,
        font_size=FONT_SIZE,
        **kw,
    ):
        self.hooked_to = {}
        self.on_click = on_click
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.rect = None
        self.text = None
        self.value = value
        self.pos_x, self.pos_y = x, y
        self.width, self.height = w, h
        self.visible = visible
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (
            self.pos_x + int(self.width / 2),
            self.pos_y + int(self.height / 2),
        )
        self.font_size = font_size
        self.font = pygame.font.Font(FONT_NAME, self.font_size)
        self.small_font = pygame.font.Font(SMALL_FONT_NAME, SMALL_FONT_SIZE)
        self.emoji_font = pygame.font.Font(EMOJI_FONT_NAME, EMOJI_FONT_SIZE)
        self.widget_init(*a, **kw)
        self.set_value(value)

    def widget_init(self):
        """
        Widget specific init code, should be overriden when needed.
        """

    def get_click_value(self, _pos):
        """
        Get the value of the attribute based on click position.
        """
        return 127

    def handle_click(self, pos):
        """
        Handle click events.
        """
        if (
            self.rect is not None
            and self.rect.collidepoint(pos)
            and self.on_click is not None
        ):
            val = self.get_click_value(pos)
            self.on_click(val)

    def hook(self, instance, attrname, hook_name, set_text=False, value_getter=None):
        """
        Hook a callback to update this widget based on a Field value.
        """
        if hook_name in self.hooked_to:
            self.unhook(hook_name)

        def callback(value):
            if value_getter:
                value = value_getter()
            if set_text and self.text != str(value):
                self.set_text(str(value))
            elif not set_text and self.value != value:
                self.set_value(value)

        field = getattr(instance, attrname)
        if isinstance(field, Field):
            field.hook(callback, hook_name)
            self.hooked_to[hook_name] = [instance, attrname]

    def unhook(self, hook_name=None):
        """
        Remove hook for this widget.
        """
        if hook_name is None:
            for name, [instance, attrname] in self.hooked_to.items():
                field = getattr(instance, attrname)
                if isinstance(field, Field):
                    field.unhook(name)
                    self.hooked_to = {}
        else:
            instance, attrname = self.hooked_to[hook_name]
            field = getattr(instance, attrname)
            if isinstance(field, Field):
                field.unhook(hook_name)
                self.hooked_to = {}

    def set_value(self, value):
        """
        Set this widget's value.
        """
        self.value = value
        if self.visible:
            self.draw()

    def set_text(self, new_text):
        """
        Set this widget's text.
        """
        self.text = new_text
        if self.visible:
            self.draw()

    def show(self):
        """
        Set this widget as visible and draw it.
        """
        self.visible = True
        self.draw()

    def hide(self):
        """
        Hide this widget.
        """
        self.visible = False
        pygame.display.get_surface().fill(BLACK, self.rect)

    def draw(self):
        """
        Draw this widget on a pygame surface.
        """

    def highlight(self):
        """
        Highlight this widget.
        """

    def shade(self):
        """
        Remove highlighting from this widget.
        """
