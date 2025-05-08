import pygame
import sys
from GameManager import GameManager

def gameWindow():
    gameManager = GameManager(screen, selected_index)
    clock = pygame.time.Clock()
    targetFrameRate = 1000

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

        if gameManager.win:
            running = False

    # Ending
    pygame.quit()
    sys.exit()


# Pygame initailization
pygame.init()

# Window settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jump King AI")

# Kolory
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont(None, 60)

# Menu opcje
menu_options = ["AI game", "Player game"]
selected_index = 0

clock = pygame.time.Clock()

running = True
while running:
    screen.fill(BLACK)

    # Rysowanie opcji
    for i, option in enumerate(menu_options):
        color = WHITE if i == selected_index else GRAY
        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 80))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % len(menu_options)
            elif event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % len(menu_options)
            elif event.key == pygame.K_RETURN:
                gameWindow()

    pygame.display.flip()
    clock.tick(60)