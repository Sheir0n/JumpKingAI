import pygame
import sys
import neat
import pickle
from GameManager import GameManager
from UserExitException import UserExitException

# Pygame initailization
pygame.init()

# Window settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jump King AI")

accumulator = 0.0
physics_step = 0.01
max_dt = 0.05
running = True
targetFrameRate = 144
speed_multiplication = 3
clock = pygame.time.Clock()
iteration_count = 250

game_manager = None

ge = []
nets = []
global pop

def run_player():
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock
    game_manager = GameManager(screen, 1)
    game_manager.draw_king_texture = True
    running = True
    while running:
        raw_dt = clock.tick(targetFrameRate) / 1000.0

        dt = min(raw_dt, max_dt)
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                main_menu()

        if accumulator < physics_step*10:
            while accumulator >= physics_step:
                game_manager.update(physics_step)
                accumulator -= physics_step
        else:
            accumulator = 0
            game_manager.update(physics_step)

        screen.fill((0, 0, 0))
        game_manager.draw_bg()
        game_manager.draw_board()
        game_manager.update_draw()
        pygame.display.update()

        if game_manager.win:
            running = False
            game_manager = None
            main_menu()
            break

    pygame.quit()
    sys.exit()

def eval_genomes(genomes, config):
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock, speed_multiplication, ge, nets, pop, game_manager

    running = True

    player_id = 0
    max_genomes = 2 * config.pop_size

    for genome_id, genome in genomes:
        #print("genome count: ", len(genomes))
        if player_id >= max_genomes:
            if genome_id in pop.population:
                genome.fitness = 0
                del pop.population[genome_id]
            continue

        player_id += 1
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        game_manager.create_player_ai(player_id, net, genome)
        ge.append((genome_id, genome))

    max_simulation_time = 10
    curr_simulation_time = 0

    while running and game_manager.win == False:
        raw_dt = clock.tick(targetFrameRate) / 1000.0
        #if selected_index == 0:
        raw_dt *= speed_multiplication

        dt = min(raw_dt, max_dt)
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                raise UserExitException()

        if accumulator < physics_step*10:
            while accumulator >= physics_step:
                game_manager.update(physics_step)
                accumulator -= physics_step
        else:
            accumulator = 0
            game_manager.update(physics_step)

        screen.fill((0, 0, 0))
        game_manager.draw_bg()
        game_manager.draw_board()
        game_manager.update_draw()
        pygame.display.update()

        if game_manager.win:
            running = False

        if curr_simulation_time < max_simulation_time:
            curr_simulation_time += dt
        else:
            game_manager.ai_manager.end_generation_calculations()
            game_manager.players.clear()
            ge.clear()
            nets.clear()
            running = False
            print("END")
        
def run_best_player(best_genomes, config):
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock, speed_multiplication, ge, nets, pop, game_manager

    player_id = 0
    game_manager = GameManager(screen, 0)  # Używamy jednego GameManagera dla wszystkich
    game_manager.draw_king_texture = True

    for idx, genome in enumerate(best_genomes):
        # Czyszczenie graczy i AI stanu
        game_manager.players.clear()
        ge.clear()
        nets.clear()

        # Tworzenie sieci i przypisanie gracza
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        genome.fitness = 0
        nets.append(net)
        ge.append((0, genome))
        game_manager.create_player_ai(player_id, net, genome)
        game_manager.disable_players_on_checkpoint = True
        game_manager.end_generation_early = False

        # Symulacja dla tego genomu
        max_simulation_time = 15
        curr_simulation_time = 0
        running = True
        last_frame_after_win = False

        while running and (not game_manager.win or not last_frame_after_win):
            raw_dt = clock.tick(targetFrameRate) / 1000.0
            dt = min(raw_dt, max_dt)
            accumulator += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise UserExitException()

            if accumulator < physics_step * 10:
                while accumulator >= physics_step:
                    game_manager.update(physics_step)
                    accumulator -= physics_step
            else:
                accumulator = 0
                game_manager.update(physics_step)

            screen.fill((0, 0, 0))
            game_manager.draw_bg()
            game_manager.draw_board()
            game_manager.update_draw()
            pygame.display.update()

            curr_simulation_time += dt
            if curr_simulation_time >= max_simulation_time:
                print(f"Time limit reached for genome #{idx + 1}")
                break

            if game_manager.end_generation_early:
                running = False

            #1 last frame for update logic
            if game_manager.win:
                last_frame_after_win = True

        # Reset flagi win dla kolejnego genomu
        game_manager.win = False
        last_frame_after_win = False


def run_ai():
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock, speed_multiplication, pop, game_manager, ge, nets
    game_manager = GameManager(screen, 0)

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        'neat-config.txt'
    )

    pop = neat.Population(config)

    try:
        pop.run(eval_genomes, iteration_count)
        game_manager.win = False
        ge = []
        nets = []
        best_genomes = game_manager.ai_manager.best_genomes
        game_manager = GameManager(screen, False)
        with open("best_genomes.pkl", "wb") as f:
            pickle.dump(best_genomes, f)
        run_best_player(best_genomes, config)

    except UserExitException:
        game_manager = None
        ge = []
        nets = []

def run_from_file(filepath):
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock, speed_multiplication, pop, game_manager, ge, nets
    game_manager = GameManager(screen, 0)

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        'neat-config.txt'
    )

    pop = neat.Population(config)

    try:
        ge = []
        nets = []
        try:
            with open(filepath, "rb") as f:
                best_genomes = pickle.load(f)
            game_manager = GameManager(screen, False)
            run_best_player(best_genomes, config)
        except FileNotFoundError:
            game_manager = None
            ge = []
            nets = []
            config_not_found_window()

    except UserExitException:
        game_manager = None
        ge = []
        nets = []

def config_not_found_window():
    pygame.init()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 80, 80)
    
    pygame.display.set_caption("Configuration Error")

    font = pygame.font.Font("pixel_font.ttf", 32)
    title_font = pygame.font.Font("pixel_font.ttf", 48)

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(BLACK)

        title_text = title_font.render("Error", True, RED)
        message_text = font.render("Configuration file not found.", True, WHITE)
        message_text_2 = font.render("Run AI Game to generate one.", True, WHITE)

        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 180))
        screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 280))
        screen.blit(message_text_2, (SCREEN_WIDTH // 2 - message_text_2.get_width() // 2, 330))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                running = False  # Zamknięcie po naciśnięciu klawisza

        pygame.display.flip()
        clock.tick(60)



def gameWindow(selected_index):
    if selected_index == 1:
        run_player()
    elif selected_index == 0:
        run_ai()
    else:
        run_from_file("best_genomes.pkl")

def main_menu():
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    YELLOW = (255, 255, 0)
    BLACK = (0, 0, 0)

    font = pygame.font.Font("pixel_font.ttf", 32)       # menu options
    title_font = pygame.font.Font("pixel_font.ttf", 56) # tytuł
    footer_font = pygame.font.Font("pixel_font.ttf", 16)

    menu_options = ["AI game", "Player game", "Best genome game"]
    selected_index = 0

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BLACK)

        title_text = title_font.render("Jump King AI", True, YELLOW)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 80))

        # Menu opcji
        for i, option in enumerate(menu_options):
            is_selected = (i == selected_index)
            color = WHITE if not is_selected else YELLOW
            option_text = font.render(option, True, color)

            x = SCREEN_WIDTH // 2 - option_text.get_width() // 2
            y = 220 + i * 80
            screen.blit(option_text, (x, y))

            if is_selected:
                # Wskaźnik wybranej opcji
                pygame.draw.polygon(screen, YELLOW, [(x - 30, y + 10), (x - 10, y), (x - 10, y + 20)])

        # Stopka
        footer_text = footer_font.render("BIAI Project 2025 - Author: Jakub Haberek, Paweł Gaj", True, GRAY)
        screen.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    gameWindow(selected_index)

        pygame.display.flip()
        clock.tick(60)

main_menu()