"""
Separator with optional text.
"""
import pygame

from pypastator.constants import BLACK, FONT_SIZE, WHITE, WIDGET_LINE
from pypastator.widgets.label import Label


class Separator(Label):
    """
    Definition of the Separator widget.
    """

    def __init__(self, *a, **kw):
        self.text = None
        self.fcolor_selected = None
        self.bcolor_selected = None
        kw.setdefault("font_size", FONT_SIZE)
        kw.setdefault("x", 0)
        kw.setdefault("w", 1024)
        kw.setdefault("h", WIDGET_LINE + 1 if kw.get("text") else 1)
        kw.setdefault("fcolor", WHITE)
        kw.setdefault("bcolor", BLACK)
        super().__init__(*a, **kw)

    def widget_init(self, **kw):
        """
        Widget specific init code.
        """
        self.text = kw.pop("text", None)
        self.fcolor_selected = kw.pop("fcolor_selected", WHITE)
        self.bcolor_selected = kw.pop("bcolor_selected", BLACK)

    def draw(self):
        """
        Draw this widget to pygame surface.
        """
        pos_y = self.pos_y
        fcolor = self.fcolor_selected if self.value else self.fcolor
        surf = pygame.display.get_surface()
        surf.fill(BLACK, self.rect)
        # Title
        pygame.draw.line(surf, fcolor, (0, pos_y), (1024, pos_y))
        if self.text:
            msg_image = self.font.render(self.text, True, fcolor)
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = (1024 / 2, pos_y + WIDGET_LINE / 2)
            surf.blit(msg_image, msg_image_rect)
            pos_y += WIDGET_LINE
            pygame.draw.line(surf, fcolor, (0, pos_y), (1024, pos_y))
