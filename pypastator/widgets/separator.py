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
        kw.setdefault("pos_x", 0)
        kw.setdefault("width", 200)
        kw.setdefault("height", WIDGET_LINE + 1 if kw.get("text") else 1)
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
        fcolor = self.fcolor_selected if self.selected else self.fcolor
        surf = pygame.display.get_surface()
        surf.fill(BLACK, self.rect)
        # Title
        pygame.draw.line(
            surf, fcolor, (self.pos_x, pos_y), (self.pos_x + self.width, pos_y)
        )
        if self.text:
            msg_image = self.font.render(self.text, True, fcolor)
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = (
                (self.width / 2) + self.pos_x,
                pos_y + WIDGET_LINE / 2,
            )
            surf.blit(msg_image, msg_image_rect)
            pos_y += WIDGET_LINE
            pygame.draw.line(
                surf, fcolor, (self.pos_x, pos_y), (self.pos_x + self.width, pos_y)
            )
