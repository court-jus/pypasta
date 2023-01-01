"""
Visual widget showing an on/off status.
"""
import pygame

from pypastator.constants import BLACK, GREEN, LED_SIZE, RED
from pypastator.widgets.labeled import Labeled


class Led(Labeled):
    """
    Definition of the Led widget.
    """

    def __init__(self, *a, **kw):
        self.label_in = None
        self.emoji = None
        self.bcolor_on = GREEN
        self.bcolor_off = RED
        self.debug = False
        kw.setdefault("width", LED_SIZE)
        kw.setdefault("height", LED_SIZE)
        super().__init__(*a, **kw)

    def widget_init(
        self,
        **kw,
    ):
        self.label_in = kw.pop("label_in", None)
        self.emoji = kw.pop("emoji", None)
        self.debug = kw.pop("debug", False)
        self.bcolor_on = kw.pop("bcolor_on", GREEN)
        self.bcolor_off = kw.pop("bcolor_off", RED)

    def draw(self):
        radius = LED_SIZE / 2
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
        super().draw()

    def hide(self):
        radius = LED_SIZE / 2
        surf = pygame.display.get_surface()
        pygame.draw.circle(surf, BLACK, self.rect.center, radius)
        super().hide()
