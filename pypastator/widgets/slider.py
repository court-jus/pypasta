import pygame

from constants import (
    DARK_GRAY,
    FONT_NAME,
    FONT_SIZE,
    LIGHT_GRAY,
    SLIDER_LABEL_SIZE,
    BASE_WIDGET_HEIGHT,
    SLIDER_WIDTH,
    WIDGETS_MARGIN,
    BLACK,
)
from widgets.label import Label

from widgets import BaseWidget


class Slider(BaseWidget):
    def __init__(
        self,
        fcolor=LIGHT_GRAY,
        bcolor=DARK_GRAY,
        w=SLIDER_WIDTH,
        h=BASE_WIDGET_HEIGHT,
        x=0,
        y=0,
        label=None,
        value=0,
        draw=True,
        ratio=127,
        stripes=False,
    ):
        super().__init__()
        self.fcolor = fcolor
        self.bcolor = bcolor
        self.x, self.y = (
            x + ((SLIDER_LABEL_SIZE + WIDGETS_MARGIN) if label is not None else 0),
            y,
        )
        self.width, self.height = w, h
        self.ratio = ratio
        self.stripes = stripes
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (self.x + int(self.width / 2), y + int(self.height / 2))
        self.label = None
        if label:
            self.label = Label(
                label,
                fcolor=fcolor,
                bcolor=bcolor,
                w=SLIDER_LABEL_SIZE,
                h=h,
                x=x,
                y=y,
                draw=draw,
            )
        self.set_value(value, draw)

    def draw(self):
        if self.label is not None:
            self.label.draw()
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        txt = self.font.render(str(self.value), True, self.fcolor)
        txtrect = txt.get_rect()
        txtrect.center = self.rect.center
        cursor = pygame.Rect(0, 0, 5, self.height)
        cursor.center = (
            self.x + int(self.value * self.width / self.ratio),
            self.rect.center[1],
        )
        surf = pygame.display.get_surface()
        surf.fill(self.fcolor, self.rect)
        surf.fill(self.bcolor, brect)
        if self.stripes:
            for i in range(self.ratio):
                x = int((self.rect.width / self.ratio * (i + 0.5)) + self.x)
                pygame.draw.line(
                    surf, self.fcolor, (x, self.rect.top), (x, self.rect.bottom - 1)
                )
        surf.blit(txt, txtrect)
        surf.fill(self.fcolor, cursor)

    def hide(self):
        if self.label is not None:
            self.label.hide()
        pygame.display.get_surface().fill(BLACK, self.rect)

    def set_value(self, value, draw=True):
        self.value = value
        if draw:
            self.draw()

    def handle_click(self, pos, callback):
        if self.rect.collidepoint(pos):
            relative_click_position = pos[0] - self.rect.x
            pos_shift = (self.rect.width / self.ratio) / 2
            equivalent_cc_value = int(
                (relative_click_position + pos_shift) * 127 / self.rect.width
            )
            new_value = callback(equivalent_cc_value)
            self.set_value(new_value)
