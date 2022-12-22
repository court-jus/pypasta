"""
Text widget.
"""
import pygame

from pypastator.constants import DARK_GRAY, FONT_SIZE, GREEN
from pypastator.widgets import BaseWidget


class Label(BaseWidget):
    """
    Definition of the Label widget.
    """

    def __init__(self, *a, **kw):
        self.text = None
        self.fcolor_selected = None
        self.bcolor_selected = None
        kw.setdefault("font_size", FONT_SIZE)
        super().__init__(*a, **kw)

    def widget_init(self, *a, **kw):
        """
        Widget specific init code.
        """
        self.text = kw.pop("text", None)
        self.fcolor_selected = kw.pop("fcolor_selected", GREEN)
        self.bcolor_selected = kw.pop("bcolor_selected", DARK_GRAY)
        super().widget_init(*a, **kw)

    def draw(self):
        """
        Draw this widget to pygame surface.
        """
        fcolor = self.fcolor_selected if self.value else self.fcolor
        bcolor = self.bcolor_selected if self.value else self.bcolor
        msg_image = self.font.render(self.text, True, fcolor)
        msg_image_rect = msg_image.get_rect()
        msg_image_rect.center = self.rect.center
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        surf = pygame.display.get_surface()
        surf.fill(fcolor, self.rect)
        surf.fill(bcolor, brect)
        surf.blit(msg_image, msg_image_rect)

    def highlight(self):
        """
        Highlight this widget.
        """
        self.set_value(True)

    def shade(self):
        """
        Remove highlighting from this widget.
        """
        self.set_value(False)
