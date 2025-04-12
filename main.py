import pygame
import sys

# Inicjalizacja pygame
pygame.init()

# Ustawienia okna
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moje Okno")

# Główna pętla gry
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Odświeżanie ekranu (np. na czarno)
    screen.fill((0, 0, 0))
    pygame.display.flip()

# Zakończenie
pygame.quit()
sys.exit()