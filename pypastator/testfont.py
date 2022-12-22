"""
A simple script to test fonts.
"""

import pygame

UNICODE_STR = "Pitch♛"
pygame.font.init()
srf = pygame.display.set_mode((500, 500))
f = pygame.font.Font("seguisym.ttf", 64)
print(f)
srf.blit(f.render(UNICODE_STR, True, (255, 0, 0)), (0, 0))
pygame.display.flip()

RUNNING = True
while RUNNING:
    srf.blit(f.render(UNICODE_STR, True, (255, 255, 255)), (0, 0))
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            RUNNING = False
