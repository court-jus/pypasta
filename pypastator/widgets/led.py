import math

import pygame
from constants import (
    BLACK,
    DARK_GRAY,
    SMALL_FONT_NAME,
    GREEN,
    KNOB_LABEL_SIZE,
    BASE_WIDGET_HEIGHT,
    KNOB_SIZE,
    LIGHT_GRAY,
    RED,
    SMALL_FONT_SIZE,
    EMOJI_FONT_NAME,
    EMOJI_FONT_SIZE,
    WIDGETS_MARGIN,
)
from widgets import BaseWidget
from widgets.label import Label


class Led(BaseWidget):
    def __init__(
        self,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=BASE_WIDGET_HEIGHT,
        h=BASE_WIDGET_HEIGHT,
        x=WIDGETS_MARGIN,
        y=WIDGETS_MARGIN,
        label=None,
        value=True,
        draw=True,
        label_in=None,
        emoji=None,
    ):
        super().__init__()
        self.fcolor = fcolor
        self.bcolor_on = GREEN
        self.bcolor_off = RED
        self.bcolor = bcolor
        self.x, self.y = (
            x + ((KNOB_LABEL_SIZE + WIDGETS_MARGIN) if label is not None else 0),
            y,
        )
        self.width, self.height = w, h
        self.small_font = pygame.font.Font(SMALL_FONT_NAME, SMALL_FONT_SIZE)
        self.emoji_font = pygame.font.Font(EMOJI_FONT_NAME, EMOJI_FONT_SIZE)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x + int(self.width / 2), y + int(self.height / 2))
        self.label = None
        self.label_in = label_in
        self.emoji = emoji
        if label:
            self.label = Label(
                label,
                fcolor=fcolor,
                bcolor=bcolor,
                w=KNOB_LABEL_SIZE,
                h=h,
                x=x,
                y=y,
                draw=draw,
            )
        self.set_value(value, draw)

    def draw(self):
        if self.label is not None:
            self.label.draw()
        radius = KNOB_SIZE / 2
        bcolor = self.bcolor_on if self.value else self.bcolor_off
        fcolor = BLACK if self.value else self.fcolor
        surf = pygame.display.get_surface()
        pygame.draw.circle(surf, bcolor, self.rect.center, radius)
        pygame.draw.circle(surf, self.fcolor, self.rect.center, radius, width=1)
        if self.label_in is not None:
            msg_image = self.small_font.render(self.label_in, True, fcolor)
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = self.rect.center
            pygame.display.get_surface().blit(msg_image, msg_image_rect)
        if self.emoji is not None:
            msg_image = self.emoji_font.render(self.emoji, True, fcolor)
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = self.rect.center
            pygame.display.get_surface().blit(msg_image, msg_image_rect)

    def set_value(self, value, draw=True):
        self.value = value
        if draw:
            self.draw()

    def handle_click(self, pos, callback):
        if self.rect.collidepoint(pos):
            new_value = callback(127)
            self.set_value(new_value)
