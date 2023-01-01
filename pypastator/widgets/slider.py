"""
Horizontal widget with a cursor moving left and right.

Shows its value inside.
"""
import pygame

from pypastator.constants import BLACK, DARK_GRAY, GREEN, SLIDER_WIDTH
from pypastator.widgets.labeled import Labeled


class Slider(Labeled):
    """
    Definition of the Slider widget.
    """

    def __init__(self, *a, **kw):
        self.ratio = None
        self.stripes = None
        self.fcolor_selected = None
        self.bcolor_selected = None
        kw.setdefault("width", SLIDER_WIDTH)
        super().__init__(*a, **kw)

    def widget_init(self, **kw):
        self.ratio = kw.pop("ratio", 128)
        self.stripes = kw.pop("stripes", False)
        self.fcolor_selected = kw.pop("fcolor_selected", GREEN)
        self.bcolor_selected = kw.pop("bcolor_selected", DARK_GRAY)
        super().widget_init(**kw)

    def _draw_background(self, surf, fcolor, bcolor):
        surf.fill(fcolor, self.rect)
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        surf.fill(bcolor, brect)

    def _draw_stripes(self, surf, fcolor):
        cell_size = self.rect.width / self.ratio
        if self.stripes:
            for i in range(self.ratio):
                line_pos = int(cell_size * i + self.pos_x + 0.5 * cell_size)
                pygame.draw.line(
                    surf,
                    fcolor,
                    (line_pos, self.rect.top),
                    (line_pos, self.rect.bottom - 1),
                )

    def _draw_cursor(self, surf, fcolor):
        cell_size = self.rect.width / self.ratio
        cursor = pygame.Rect(0, 0, 5, self.height)
        cursor.center = (
            int(cell_size * (self.value or 0) + self.pos_x + 0.5 * cell_size),
            self.rect.center[1],
        )
        surf.fill(fcolor, cursor)

    def _draw_modulation_dot(self, surf):
        if self.modulation:
            line_pos = self.pos_x + int(
                (self.value - self.modulation) * self.width / self.ratio
            )
            pygame.draw.circle(surf, GREEN, (line_pos, self.rect.bottom - 3), 3)

    def _draw_text(self, surf):
        txt = self.font.render(str(self.value), True, BLACK)
        txtrect = txt.get_rect()
        txtrect.center = self.rect.center
        surf.blit(txt, txtrect)

    def draw(self):
        """
        Draw this widget on a pygame surface.
        """
        surf = pygame.display.get_surface()
        fcolor = self.fcolor_selected if self.selected else self.fcolor
        bcolor = self.bcolor_selected if self.selected else self.bcolor
        self._draw_background(surf, fcolor, bcolor)
        self._draw_stripes(surf, fcolor)
        self._draw_cursor(surf, fcolor)
        self._draw_modulation_dot(surf)
        self._draw_text(surf)
        super().draw()

    def get_click_value(self, pos):
        """
        Return value related to where the user clicked.
        """
        relative_click_position = (pos[0] - self.rect.x) / self.width * self.ratio
        return min(self.ratio, int(relative_click_position))
