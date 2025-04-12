import pygame
import sys

# Inicjalizacja pygame
pygame.init()

# Ustawienia okna
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Moje Okno")

player = pygame.Rect((400, 550, 25, 25))
ground = pygame.Rect((0, 575, 800, 25))

# Główna pętla gry
running = True
while running:

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (250, 0, 0), player)
    pygame.draw.rect(screen, (0, 200, 100), ground)

    key = pygame.key.get_pressed()
    if key[pygame.K_a] == True:
        player.move_ip(-1, 0)
    elif key[pygame.K_d] == True:
        player.move_ip(1, 0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ograniczenie ruchu do granic ekranu
    if player.left < 0:
        player.left = 0
    if player.right > SCREEN_WIDTH:
        player.right = SCREEN_WIDTH

    pygame.display.update()

# Zakończenie
pygame.quit()
sys.exit()