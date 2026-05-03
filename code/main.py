import pygame
from sys import exit

INTERAL_W, INTERAL_H = 320, 180
SCALE = 4

pygame.init()

screen = pygame.display.set_mode((INTERAL_W * SCALE, INTERAL_H * SCALE))
surface = pygame.Surface((INTERAL_H, INTERAL_H))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

while True:


    # --- Input ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


    # --- Update ---


    # --- Render ---
    

    # --- Scale ---
    scaled = pygame.transform.scale(surface,(INTERAL_W * SCALE, INTERAL_H * SCALE))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

    clock.tick_busy_loop()