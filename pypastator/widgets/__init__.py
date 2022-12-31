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
    MESSAGE_FONT_SIZE,
    MOUSE_LEFT_CLICK,
    MOUSE_WHEEL_DOWN,
    MOUSE_WHEEL_UP,
    SMALL_FONT_NAME,
    SMALL_FONT_SIZE,
)
from pypastator.engine.field import Field


class BaseWidget:
    """
    Base class for all widgets.
    """

    pygame.font.init()
    font = pygame.font.Font(FONT_NAME, FONT_SIZE)
    small_font = pygame.font.Font(SMALL_FONT_NAME, SMALL_FONT_SIZE)
    msg_font = pygame.font.Font(FONT_NAME, MESSAGE_FONT_SIZE)
    emoji_font = pygame.font.Font(EMOJI_FONT_NAME, EMOJI_FONT_SIZE)

    def __init__(
        self,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=BASE_WIDGET_WIDTH,
        h=BASE_WIDGET_HEIGHT,
        x=1024,
        y=768,
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
        self.selected = False
        self.modulation = 0
        self.pos_x, self.pos_y = x, y
        self.width, self.height = w, h
        self.visible = visible
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (
            self.pos_x + int(self.width / 2),
            self.pos_y + int(self.height / 2),
        )
        self.font_size = font_size
        self.debug = kw.pop("debug", False)
        self.widget_init(**kw)
        self.set_value(value)

    def get_font(self):
        """
        Gather the font to be used.
        """
        return self.font

    def widget_init(self, **_kw):
        """
        Widget specific init code, should be overriden when needed.
        """

    def get_click_value(self, _pos):
        """
        Get the value of the attribute based on click position.
        """
        return 127

    def is_hovered(self):
        """
        Detect if this widget is hovered by the mouse.
        """
        return self.rect is not None and self.rect.collidepoint(pygame.mouse.get_pos())

    def handle_click(self, pos, button):
        """
        Handle click events.
        """
        if (
            button not in (MOUSE_LEFT_CLICK, MOUSE_WHEEL_UP, MOUSE_WHEEL_DOWN)
            or self.rect is None
            or self.on_click is None
            or not self.rect.collidepoint(pos)
        ):
            return
        val = self.get_click_value(pos)
        if isinstance(self.on_click, (list, tuple)):
            click_cb, handle_wheel = self.on_click
        else:
            click_cb, handle_wheel = self.on_click, False
        if (
            handle_wheel
            or button not in (MOUSE_WHEEL_UP, MOUSE_WHEEL_DOWN)
            or len(self.hooked_to.keys()) != 1
        ):
            click_cb(val, button)
        else:
            field = getattr(*list(self.hooked_to.values())[0])
            if isinstance(field, Field):
                field.increment(1 if button == MOUSE_WHEEL_UP else -1)

    def hook(self, instance, attrname, hook_name, set_text=False, value_getter=None):
        """
        Hook a callback to update this widget based on a Field value.
        """
        if hook_name in self.hooked_to:
            self.unhook(hook_name)

        def callback(value, modulation):
            if value_getter:
                value = value_getter()
            if set_text and self.text != str(value):
                self.set_text(str(value))
            elif not set_text and self.value != value:
                self.set_value(value)
            self.set_modulation(modulation)

        field = getattr(instance, attrname)
        if isinstance(field, Field):
            field.hook(callback, hook_name, send_modulation=True)
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

    def set_modulation(self, modulation):
        """
        Set the modulation value so it can be displayed along the value.
        """
        self.modulation = modulation
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
        surf = pygame.display.get_surface()
        surf.fill(BLACK, self.rect)
        self.visible = False

    def get_width(self):
        """
        Get this widget's width.
        """
        return self.width

    def move_to(self, new_x, new_y, new_width=None):
        """
        Move widget to another position.
        """
        self.hide()
        self.pos_x = new_x
        self.pos_y = new_y
        if new_width is not None:
            self.width = new_width
        self.apply_new_pos()

    def apply_new_pos(self):
        """
        Apply move_to result.
        """
        self.rect.update(self.rect.left, self.rect.top, self.width, self.height)
        self.rect.center = (
            self.pos_x + int(self.width / 2),
            self.pos_y + int(self.height / 2),
        )
        self.show()

    def redraw(self):
        """
        Refresh the display.
        """
        self.draw()

    def draw(self):
        """
        Draw this widget on a pygame surface.
        """
        raise NotImplementedError

    def highlight(self):
        """
        Highlight this widget.
        """
        self.selected = True
        self.draw()

    def shade(self):
        """
        Remove highlighting from this widget.
        """
        self.selected = False
        self.draw()
