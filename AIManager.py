import neat
import neat.population
from pygame.math import clamp

class AIManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            'neat-config.txt'
        )
        self.population = neat.Population(config)
        self.gen = 0
        self.gen_timer = 0
        self.max_gen_time = 10 #s

        self.stop_running = False

    def run_one_generation(self):
        self.gen += 1
        print(f"Generacja {self.gen}")
        self.population.run(self.run_player, 1)

    def run_player(self, genomes, config):
        nets = []
        players = []

        for id, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0
            self.game_manager.create_player(len(self.game_manager.players))
            current_player = self.game_manager.players[len(self.game_manager.players) - 1]

            current_player.create_player_ai(
            net,
            lambda: self.build_observation(current_player),  # przekazujemy kontekst gracza
            g)
            players.append(current_player)

    def build_observation(self, player):
        curr_id = player.curr_platform_id
        # Pobranie danych następnych platform, jeśli brak to kopiuje ostatnie elementy
        next_platforms = self.game_manager.platforms[curr_id:curr_id + 2]
        if len(next_platforms) < 2 and next_platforms:
            last = next_platforms[-1]
            next_platforms.extend([last] * (2 - len(next_platforms)))
            #ver 1
        return [
            # jumping
            player.currJumpCharge / player.MAXJUMPCHARGE,
            1.0 if player.currJumpCharge >= player.MAXJUMPCHARGE else 0.0,

            clamp((player.posX - next_platforms[0].hitbox.centerx) / self.game_manager.screen_width, -1, 1),
            clamp((player.posX - next_platforms[0].hitbox.left) / self.game_manager.screen_width, -1, 1),

            clamp((player.posX - next_platforms[1].hitbox.centerx) / self.game_manager.screen_width, -1, 1),
            next_platforms[1].hitbox.width / self.game_manager.screen_width,
            clamp((player.posY - next_platforms[1].hitbox.top) / self.game_manager.screen_height, -1, 1),
        ]

        #ver 2
        # def signed_distance(player_x, platform):
        #     dist_left = player_x - platform.hitbox.left
        #     dist_right = platform.hitbox.right - player_x
        #     if abs(dist_left) < abs(dist_right):
        #         return clamp(-abs(dist_left) / self.game_manager.screen_width, -1, 1)
        #     else:
        #         return clamp(abs(dist_right) / self.game_manager.screen_width, -1, 1)
        #
        # return [
        #     # jumping
        #     player.currJumpCharge / player.MAXJUMPCHARGE,
        #     #1.0 if player.currJumpCharge >= player.MAXJUMPCHARGE else 0.0,
        #
        #     signed_distance(player.posX, next_platforms[0]),
        #     signed_distance(player.posX, next_platforms[1]),
        #     clamp((player.posY - next_platforms[1].hitbox.top) / self.game_manager.screen_height, -1, 1),
        # ]

        # ver 3
        # return [
        #     # curr % jump charge
        #     player.currJumpCharge / player.MAXJUMPCHARGE,
        #     # is player in air
        #     0.0 if player.in_air else 1.0,
        #
        #     #noramlizowana pozycja
        #     player.posX / self.game_manager.screen_width,
        #     (self.game_manager.screen_height - player.posY) / self.game_manager.screen_height,
        #
        #     #pozcja na platformie na której stoi
        #     clamp((player.posX - next_platforms[0].hitbox.centerx) / next_platforms[0].hitbox.width, -1, 1),
        #     #szerokość
        #     next_platforms[0].hitbox.width / self.game_manager.screen_width,
        #
        #     #następna platforma
        #     (next_platforms[1].hitbox.centerx - player.posX) / self.game_manager.screen_width,
        #     ((self.game_manager.screen_height - next_platforms[1].hitbox.top) - (self.game_manager.screen_height - player.posY)) / self.game_manager.screen_height,
        #
        #     next_platforms[1].hitbox.width / self.game_manager.screen_width,
        #     next_platforms[1].hitbox.centerx / self.game_manager.screen_width
        # ]

    def create_new_generation_if_out_of_time(self, dt):
        self.gen_timer += dt
        if self.gen_timer >= self.max_gen_time:
            self.gen_timer = 0
            self.end_generation_calculations()
            self.game_manager.reset_transitions()
            self.run_one_generation()

    def end_generation_calculations(self):
        for player in self.game_manager.players:
            if player.jump_count == 0:
                player.ai.no_jump_penalty()
        self.collect_and_display_gen_stats()
        self.game_manager.players.clear()

    def collect_and_display_gen_stats(self):
        fitness_stats = []
        for player in self.game_manager.players:
            fitness_stats.append(player.ai.genome.fitness)
        fitness_stats.sort(reverse=True)

        for i, fitness in enumerate(fitness_stats[:10], start=1):
            print(f"{i}. {fitness:.2f}")


