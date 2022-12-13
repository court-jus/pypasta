# -*- coding: utf-8 -*-

import pygame
import sys


unistr = "Pitch♛"
pygame.font.init()
srf = pygame.display.set_mode((500, 500))
f = pygame.font.Font("seguisym.ttf", 64)
print(f)
srf.blit(f.render(unistr, True, (255, 0, 0)), (0, 0))
pygame.display.flip()

while True:
    srf.blit(f.render(unistr, True, (255, 255, 255)), (0, 0))
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
