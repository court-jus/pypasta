"""
Vertical widget with a cursor moving up and down.
"""
import pygame

from pypastator.constants import GREEN, VERT_SLIDER_HEIGHT, VERT_SLIDER_WIDTH
from pypastator.widgets.slider import Slider


class VertSlider(Slider):
    """
    Definition of the VertSlider widget.
    """

    def __init__(self, *a, **kw):
        kw.setdefault("width", VERT_SLIDER_WIDTH)
        kw.setdefault("height", VERT_SLIDER_HEIGHT)
        super().__init__(*a, **kw)

    def _draw_cursor(self, surf, fcolor):
        cursor = pygame.Rect(0, 0, self.width, 5)
        cell_size = (self.rect.height - 2) / self.ratio
        cursor.center = (
            self.rect.center[0],
            (self.rect.bottom - 2)
            - int(cell_size * (self.value or 0) + 0.5 * cell_size),
        )
        surf.fill(fcolor, cursor)

    def _draw_stripes(self, surf, fcolor):
        cell_size = (self.rect.height - 2) / self.ratio
        if self.stripes:
            for i in range(self.ratio):
                line_pos = int(cell_size * i + self.pos_y + 0.5 * cell_size)
                pygame.draw.line(
                    surf,
                    fcolor,
                    (self.rect.left, line_pos),
                    (self.rect.right - 1, line_pos),
                )

    def _draw_modulation_dot(self, surf):
        if self.modulation:
            line_pos = self.pos_y + int(
                (self.value - self.modulation) * self.height / self.ratio
            )
            pygame.draw.circle(surf, GREEN, (self.rect.right - 3, line_pos), 3)

    def get_click_value(self, pos):
        """
        Return value related to where the user clicked.
        """
        relative_click_position = self.ratio - (
            (pos[1] - self.rect.y) / self.height * self.ratio
        )
        return min(self.ratio, int(relative_click_position))
