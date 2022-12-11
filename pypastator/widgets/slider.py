import pygame

from constants import (DARK_GRAY, FONT_SIZE, LIGHT_GRAY, SLIDER_LABEL_SIZE,
                         SLIDER_WIDTH, WIDGETS_MARGIN, BLACK)
from widgets.label import Label


class Slider:
    def __init__(
        self,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=SLIDER_WIDTH,
        h=FONT_SIZE + 2,
        x=WIDGETS_MARGIN,
        y=WIDGETS_MARGIN,
        label=None,
        value=0,
    ):
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.x, self.y = (
            x + ((SLIDER_LABEL_SIZE + WIDGETS_MARGIN) if label is not None else 0),
            y,
        )
        self.width, self.height = w, h
        self.value = value
        self.font = pygame.font.SysFont(None, FONT_SIZE)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x + int(self.width / 2), y + int(self.height / 2))
        self.label = None
        if label:
            self.label = Label(
                label, fcolor=fcolor, bcolor=bcolor, w=SLIDER_LABEL_SIZE, h=h, x=x, y=self.rect.center[1]
            )

    def draw(self):
        if self.label is not None:
            self.label.draw()
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        txt = self.font.render(str(self.value), True, self.fcolor, self.bcolor)
        cursor = pygame.Rect(0, 0, 5, self.height)
        cursor.center = (
            self.x + int(self.value * self.width / 127),
            self.rect.center[1],
        )
        pygame.display.get_surface().fill(self.fcolor, self.rect)
        pygame.display.get_surface().fill(self.bcolor, brect)
        pygame.display.get_surface().blit(
            txt, (self.rect.center[0], self.rect.center[1] - (FONT_SIZE / 4))
        )
        pygame.display.get_surface().fill(self.fcolor, cursor)

    def hide(self):
        if self.label is not None:
            self.label.hide()
        pygame.display.get_surface().fill(BLACK, self.rect)