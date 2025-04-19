import pygame
import sys
from GameManager import GameManager

# Pygame initailization
pygame.init()

# Window settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jump King AI")

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
    gameManager.drawBoard()
    
    gameManager.updateDraw()
    pygame.display.update()

# Ending
pygame.quit()
sys.exit()