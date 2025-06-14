import pygame
import sys
from GameManager import GameManager

def gameWindow():
    game_manager = GameManager(screen, selected_index)
    clock = pygame.time.Clock()
    targetFrameRate = 144
    speed_multiplication = 3

    running = True
    if selected_index == 0:
        game_manager.ai_manager.run_one_generation()

    # Akumulator i krok fizyczny
    accumulator = 0.0
    physics_step = 0.01
    max_dt = 0.05  # ograniczenie przy dużych lagach

    while running:
        # Pobierz czas od ostatniej klatki
        raw_dt = clock.tick(targetFrameRate) / 1000.0
        if selected_index == 0:
            raw_dt *= speed_multiplication

        # Ograniczenie zbyt dużego przeskoku czasu
        dt = min(raw_dt, max_dt)
        accumulator += dt

        # Obsługa zdarzeń (zamykanie gry)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Kilkukrotne wywołanie update, jeśli potrzeba
        if accumulator < physics_step*10:
            while accumulator >= physics_step:
                game_manager.update(physics_step)
                accumulator -= physics_step
        else:
            accumulator = 0
            game_manager.update(physics_step)
            #czekanie na odlagowanie

        # Rysowanie raz na pętlę (możesz też renderować interpolując)
        screen.fill((0, 0, 0))
        game_manager.draw_board()
        game_manager.update_draw()
        pygame.display.update()

        if game_manager.win:
            running = False

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