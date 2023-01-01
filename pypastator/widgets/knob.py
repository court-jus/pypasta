"""
Rotary widget.
"""
import math

import pygame

from pypastator.constants import BLACK, GREEN, KNOB_ANGLE, KNOB_SIZE
from pypastator.widgets.labeled import Labeled


class Knob(Labeled):
    """
    Definition of the Knob widget.
    """

    def __init__(self, *a, **kw):
        kw.setdefault("width", KNOB_SIZE)
        kw.setdefault("height", KNOB_SIZE)
        super().__init__(*a, **kw)

    def draw(self):
        """
        Draw the knob to a pygame surface.
        """
        radius = KNOB_SIZE / 2
        surf = pygame.display.get_surface()
        surf.fill(BLACK, self.rect)
        pygame.draw.circle(surf, self.bcolor, self.rect.center, radius)
        pygame.draw.circle(surf, self.fcolor, self.rect.center, radius, width=1)
        rad = (self.value or 0) * 1.8 * math.pi / 127
        line_angle = rad + 0.1 * math.pi + KNOB_ANGLE
        dest_x = math.cos(line_angle) * radius + self.rect.center[0]
        dest_y = math.sin(line_angle) * radius + self.rect.center[1]
        pygame.draw.line(surf, self.fcolor, self.rect.center, (dest_x, dest_y))
        if self.modulation:
            origin_rad = ((self.value - self.modulation) or 0) * 1.8 * math.pi / 127
            origin_line_angle = origin_rad + 0.1 * math.pi + KNOB_ANGLE
            dest_x = math.cos(origin_line_angle) * (radius - 3) + self.rect.center[0]
            dest_y = math.sin(origin_line_angle) * (radius - 3) + self.rect.center[1]
            pygame.draw.circle(surf, GREEN, (dest_x, dest_y), 3)
        super().draw()

    def get_click_value(self, pos):
        """
        Get the value based on the position of the click.
        """
        center_x, center_y = self.rect.center
        delta_x = (pos[0] - center_x) / (self.rect.height / 2)
        delta_y = (pos[1] - center_y) / (self.rect.height / 2)
        rad = -math.atan2(delta_x, delta_y)
        equivalent_cc_value = int(
            (rad + 0.1 * math.pi - KNOB_ANGLE * 0.5) * 127 / 1.8 / math.pi
        )
        if equivalent_cc_value < 0:
            equivalent_cc_value = 127 + equivalent_cc_value
        equivalent_cc_value = min(127, max(1, equivalent_cc_value))
        return equivalent_cc_value
