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
        kw.setdefault("w", VERT_SLIDER_WIDTH)
        kw.setdefault("h", VERT_SLIDER_HEIGHT)
        super().__init__(*a, **kw)

    def draw(self):
        """
        Draw this widget on a pygame surface.
        """
        fcolor = self.fcolor_selected if self.selected else self.fcolor
        bcolor = self.bcolor_selected if self.selected else self.bcolor
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        cursor = pygame.Rect(0, 0, self.width, 5)
        cell_size = self.rect.height / self.ratio
        cursor.center = (
            self.rect.center[0],
            self.rect.bottom - int(cell_size * (self.value or 0) + 0.5 * cell_size),
        )
        surf = pygame.display.get_surface()
        surf.fill(fcolor, self.rect)
        surf.fill(bcolor, brect)
        if self.stripes:
            for i in range(self.ratio):
                line_pos = int(cell_size * i + self.pos_y + 0.5 * cell_size)
                pygame.draw.line(
                    surf,
                    fcolor,
                    (self.rect.left, line_pos),
                    (self.rect.right - 1, line_pos),
                )
        if self.modulation:
            line_pos = self.pos_y + int(
                (self.value - self.modulation) * self.height / self.ratio
            )
            pygame.draw.circle(surf, GREEN, (self.rect.right - 3, line_pos), 3)
        surf.fill(fcolor, cursor)

    def get_click_value(self, pos):
        """
        Return value related to where the user clicked.
        """
        relative_click_position = self.ratio - (
            (pos[1] - self.rect.y) / self.height * self.ratio
        )
        return min(self.ratio, int(relative_click_position))
