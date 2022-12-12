import math

import pygame

from constants import (DARK_GRAY, FONT_SIZE, KNOB_ANGLE, KNOB_LABEL_SIZE,
                         KNOB_SIZE, LIGHT_GRAY, WIDGETS_MARGIN, GREEN, RED)
from widgets.label import Label


class Led:
    def __init__(
        self,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=KNOB_SIZE,
        h=KNOB_SIZE,
        x=WIDGETS_MARGIN,
        y=WIDGETS_MARGIN,
        label=None,
        value=True,
        draw=True,
    ):
        self.fcolor = fcolor
        self.bcolor_on = GREEN
        self.bcolor_off = RED
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
        pygame.draw.circle(surf, self.bcolor_on if self.value else self.bcolor_off, self.rect.center, radius)
        pygame.draw.circle(surf, self.fcolor, self.rect.center, radius, width=1)

    def set_value(self, value, draw=True):
        self.value = value
        if draw:
            self.draw()
