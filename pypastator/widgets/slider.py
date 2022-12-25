"""
Horizontal widget with a cursor moving left and right.

Shows its value inside.
"""
import pygame

from pypastator.constants import BLACK, GREEN, SLIDER_WIDTH
from pypastator.widgets.labeled import Labeled


class Slider(Labeled):
    """
    Definition of the Slider widget.
    """

    def __init__(self, *a, **kw):
        self.ratio = None
        self.stripes = None
        kw.setdefault("w", SLIDER_WIDTH)
        super().__init__(*a, **kw)

    def widget_init(self, *a, **kw):
        self.ratio = kw.pop("ratio", 128)
        self.stripes = kw.pop("stripes", False)
        super().widget_init(*a, **kw)

    def draw(self):
        """
        Draw this widget on a pygame surface.
        """
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        txt = self.font.render(str(self.value), True, BLACK)
        txtrect = txt.get_rect()
        txtrect.center = self.rect.center
        cursor = pygame.Rect(0, 0, 5, self.height)
        cell_size = self.rect.width / self.ratio
        cursor.center = (
            int(cell_size * (self.value or 0) + self.pos_x + 0.5 * cell_size),
            self.rect.center[1],
        )
        surf = pygame.display.get_surface()
        surf.fill(self.fcolor, self.rect)
        surf.fill(self.bcolor, brect)
        if self.stripes:
            for i in range(self.ratio):
                line_pos = int(cell_size * i + self.pos_x + 0.5 * cell_size)
                pygame.draw.line(
                    surf,
                    self.fcolor,
                    (line_pos, self.rect.top),
                    (line_pos, self.rect.bottom - 1),
                )
        if self.modulation:
            line_pos = self.pos_x + int(
                (self.value - self.modulation) * self.width / self.ratio
            )
            pygame.draw.circle(surf, GREEN, (line_pos, self.rect.bottom - 3), 3)
        surf.fill(self.fcolor, cursor)
        surf.blit(txt, txtrect)
        super().draw()

    def get_click_value(self, pos):
        """
        Return value related to where the user clicked.
        """
        relative_click_position = (pos[0] - self.rect.x) / self.width * self.ratio
        return min(self.ratio, int(relative_click_position))
