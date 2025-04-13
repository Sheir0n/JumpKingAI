import pygame
import sys
from GameManager import GameManager

# Inicjalizacja pygame
pygame.init()

# Ustawienia okna
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jump King AI")

ground = pygame.Rect((0, 695, 1280, 25))

gameManager = GameManager(screen)
clock = pygame.time.Clock()
targetFrameRate = 60

# Main game loop
running = True
while running:
    # calculates delta time in seconds
    dt = clock.tick(targetFrameRate) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # update logic
    gameManager.update(dt)

    # render frame
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 200, 100), ground)
    gameManager.updateDraw()
    pygame.display.update()

# Zakończenie
pygame.quit()
sys.exit()