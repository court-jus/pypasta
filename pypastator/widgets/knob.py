import math

import pygame

from constants import (DARK_GRAY, FONT_SIZE, KNOB_ANGLE, KNOB_LABEL_SIZE,
                         KNOB_SIZE, LIGHT_GRAY, WIDGETS_MARGIN)
from widgets.label import Label


class Knob:
    def __init__(
        self,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=KNOB_SIZE,
        h=KNOB_SIZE,
        x=WIDGETS_MARGIN,
        y=WIDGETS_MARGIN,
        label=None,
        value=0,
        draw=True,
    ):
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.x, self.y = (
            x + ((KNOB_LABEL_SIZE + WIDGETS_MARGIN) if label is not None else 0),
            y,
        )
        self.width, self.height = w, h
        self.font = pygame.font.SysFont(None, FONT_SIZE)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x + int(self.width / 2), y + int(self.height / 2))
        self.label = None
        if label:
            self.label = Label(
                label, fcolor=fcolor, bcolor=bcolor, w=KNOB_LABEL_SIZE, h=h, x=x, y=self.rect.center[1], draw=draw,
            )
        self.set_value(value, draw)

    def draw(self):
        if self.label is not None:
            self.label.draw()
        radius = KNOB_SIZE / 2
        surf = pygame.display.get_surface()
        pygame.draw.circle(surf, self.bcolor, self.rect.center, radius)
        pygame.draw.circle(surf, self.fcolor, self.rect.center, radius, width=1)
        line_angle = (self.value * 1.8 * math.pi / 127) + 0.1 * math.pi + KNOB_ANGLE
        dest_x = math.cos(line_angle) * radius + self.rect.center[0]
        dest_y = math.sin(line_angle) * radius + self.rect.center[1]
        pygame.draw.line(surf, self.fcolor, self.rect.center, (dest_x, dest_y))

    def set_value(self, value, draw=True):
        self.value = value
        if draw:
            self.draw()
