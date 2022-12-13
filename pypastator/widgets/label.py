import pygame

from constants import (
    BUTTON_WIDTH,
    DARK_GRAY,
    FONT_NAME,
    FONT_SIZE,
    LIGHT_GRAY,
    BASE_WIDGET_HEIGHT,
    WIDGETS_MARGIN,
    GREEN,
    BLACK,
)

from widgets import BaseWidget


class Label(BaseWidget):
    def __init__(
        self,
        text,
        fcolor=LIGHT_GRAY,
        fcolor_selected=GREEN,
        bcolor=DARK_GRAY,
        bcolor_selected=DARK_GRAY,
        w=BUTTON_WIDTH,
        h=BASE_WIDGET_HEIGHT,
        x=0,
        y=0,
        value=False,
        draw=True,
    ):
        super().__init__()
        self.text = text
        self.fcolor = fcolor
        self.fcolor_selected = fcolor_selected
        self.bcolor = bcolor
        self.bcolor_selected = bcolor_selected
        self.font = pygame.font.Font(FONT_NAME, FONT_SIZE)
        self.width, self.height = w, h

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x + int(self.width / 2), y + BASE_WIDGET_HEIGHT / 2)
        self.set_value(value, draw)

    def draw(self):
        fcolor = self.fcolor_selected if self.value else self.fcolor
        bcolor = self.bcolor_selected if self.value else self.bcolor
        msg_image = self.font.render(self.text, True, fcolor)
        msg_image_rect = msg_image.get_rect()
        msg_image_rect.center = self.rect.center
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        pygame.display.get_surface().fill(fcolor, self.rect)
        pygame.display.get_surface().fill(bcolor, brect)
        pygame.display.get_surface().blit(msg_image, msg_image_rect)

    def hide(self):
        pygame.display.get_surface().fill(BLACK, self.rect)

    def set_value(self, value, draw=True):
        self.value = value
        if draw:
            self.draw()

    def set_text(self, new_text, draw=True):
        self.text = new_text
        if draw:
            self.draw()

    def highlight(self):
        self.set_value(True)

    def shade(self):
        self.set_value(False)
