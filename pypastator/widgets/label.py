import pygame

from constants import (BUTTON_WIDTH, DARK_GRAY, FONT_SIZE, LIGHT_GRAY,
                         WIDGETS_MARGIN, GREEN, BLACK)


class Label:
    def __init__(
        self,
        label,
        fcolor=LIGHT_GRAY,
        fcolor_selected=GREEN,
        bcolor=DARK_GRAY,
        bcolor_selected=DARK_GRAY,
        w=BUTTON_WIDTH,
        h=FONT_SIZE * 2,
        x=WIDGETS_MARGIN,
        y=WIDGETS_MARGIN,
        value=False,
    ):
        self.label = label
        self.fcolor = fcolor
        self.fcolor_selected = fcolor_selected
        self.bcolor = bcolor
        self.bcolor_selected = bcolor_selected
        self.value = value
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.width, self.height = w, h

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x + int(self.width / 2), y)


    def draw(self):
        fcolor = self.fcolor_selected if self.value else self.fcolor
        bcolor = self.bcolor_selected if self.value else self.bcolor
        msg_image = self.font.render(self.label, True, fcolor, bcolor)
        msg_image_rect = msg_image.get_rect()
        msg_image_rect.center = self.rect.center
        brect = pygame.Rect(0, 0, self.width - 2, self.height - 2)
        brect.center = self.rect.center
        pygame.display.get_surface().fill(fcolor, self.rect)
        pygame.display.get_surface().fill(bcolor, brect)
        pygame.display.get_surface().blit(msg_image, msg_image_rect)

    def hide(self):
        pygame.display.get_surface().fill(BLACK, self.rect)

