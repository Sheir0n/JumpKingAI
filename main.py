import pygame
import sys
import neat
from GameManager import GameManager

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

game_manager = None

ge = []
nets = []
global pop

def run_player():
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock
    game_manager = GameManager(screen, 1)

    while running:
        raw_dt = clock.tick(targetFrameRate) / 1000.0

        dt = min(raw_dt, max_dt)
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if accumulator < physics_step*10:
            while accumulator >= physics_step:
                game_manager.update(physics_step)
                accumulator -= physics_step
        else:
            accumulator = 0
            game_manager.update(physics_step)

        screen.fill((0, 0, 0))
        game_manager.draw_board()
        game_manager.update_draw()
        pygame.display.update()

        if game_manager.win:
            running = False

    pygame.quit()
    sys.exit()

#TODO: dorobić zamykanie okna kończońce program
def eval_genomes(genomes, config):
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock, speed_multiplication, ge, nets, pop, game_manager

    running = True

    player_id = 0
    max_genomes = 2 * config.pop_size

    for genome_id, genome in genomes:
        print("genome count: ", len(genomes))
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

    while running:
        raw_dt = clock.tick(targetFrameRate) / 1000.0
        if selected_index == 0:
            raw_dt *= speed_multiplication

        dt = min(raw_dt, max_dt)
        accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if accumulator < physics_step*10:
            while accumulator >= physics_step:
                game_manager.update(physics_step)
                accumulator -= physics_step
        else:
            accumulator = 0
            game_manager.update(physics_step)

        screen.fill((0, 0, 0))
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


def run_ai():
    global accumulator, physics_step, max_dt, running, targetFrameRate, clock, speed_multiplication, pop, game_manager
    game_manager = GameManager(screen, 0)

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        'neat-config.txt'
    )

    pop = neat.Population(config)

    pop.run(eval_genomes,500)

def gameWindow():
    if selected_index == 1:
        run_player()
    else:
        run_ai()


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
