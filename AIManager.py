from math import sqrt, atan2, pi

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
        self.max_gen_time = 15 #s

        self.stop_running = False

        #TODO: PRZEROBIĆ TO ABY DZIAŁAŁO NA DELTA TIME
        #player.ai.distance_to_next_platform_bonus(self.game_manager.platforms, self.game_manager.screen_width, self.game_manager.screen_height)

    def run_one_generation(self):
        self.gen += 1
        self.game_manager.generate_platforms()
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

        seen_platforms = self.game_manager.platforms[curr_id:curr_id + 3]
        if len(seen_platforms) < 3 and seen_platforms:
            last = seen_platforms[-1]
            seen_platforms.extend([last] * (3 - len(seen_platforms)))

            #ver 1
        # return [
        #     # jumping
        #     player.currJumpCharge / player.MAXJUMPCHARGE,
        #     1.0 if player.currJumpCharge >= player.MAXJUMPCHARGE else 0.0,
        #
        #     clamp((player.posX - next_platforms[0].hitbox.centerx) / self.game_manager.screen_width, -1, 1),
        #     clamp((player.posX - next_platforms[0].hitbox.left) / self.game_manager.screen_width, -1, 1),
        #
        #     clamp((player.posX - next_platforms[1].hitbox.centerx) / self.game_manager.screen_width, -1, 1),
        #     next_platforms[1].hitbox.width / self.game_manager.screen_width,
        #     clamp((player.posY - next_platforms[1].hitbox.top) / self.game_manager.screen_height, -1, 1),
        # ]

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

        #ver 4
        # return [
        #     #wartości do skoku
        #     player.currJumpCharge / player.MAXJUMPCHARGE,
        #     0.0 if player.in_air else 1.0,
        #
        #     #odległośc do środka platformy na której stoi (normalizowana do szerokości ekranu)
        #     clamp((player.posX - next_platforms[0].hitbox.centerx) / next_platforms[1].hitbox.width, -1, 1),
        #     #rozmiar platformy (normalizowany do szerokości)
        #     clamp(next_platforms[0].hitbox.width / self.game_manager.screen_width, 0,1),
        #
        #     #odl x od gracza (normalizowana) do najbliższej krawedzi bocznej następnej platformy
        #     min(
        #         abs(clamp((player.posX - next_platforms[1].hitbox.right) / self.game_manager.screen_width, -1, 1)),
        #         abs(clamp((player.posX - next_platforms[1].hitbox.left) / self.game_manager.screen_width, -1, 1))
        #     ),
        #
        #     #różnica wysokości do next platformy (normalizowana)
        #     clamp((player.posY - next_platforms[0].hitbox.top) / self.game_manager.screen_height,-1,1),
        #
        #     #kierunek do następnej platformy
        #     -1.0 if abs(player.posX - next_platforms[1].hitbox.right) >= abs(player.posX - next_platforms[1].hitbox.left) else 1.0,
        # ]

    #ver 5 (maxsafedist and directional info) WERSJA DO NOWEGO SYSTEMU SKAKANIA
        # return [
        #     #Aktualny charge skoku
        #     player.currJumpCharge / player.MAXJUMPCHARGE,
        #
        #     # Znormalizowana pozycja x na ekranie
        #     player.hitbox.centerx / self.game_manager.screen_width,
        #
        #     #Znormalizowana odleglosc od srodka aktualnej platformy
        #     (player.hitbox.centerx - seen_platforms[0].hitbox.centerx) / (seen_platforms[0].hitbox.width / 2),
        #
        #     self.nearest_platform_distance(seen_platforms[1], player),
        #     #kąt do kolejnej platformy
        #     self.nearest_platform_angle(player,seen_platforms[1]),
        #
        #     self.nearest_platform_distance(seen_platforms[2], player),
        #     # kąt do kolejnej platformy
        #     self.nearest_platform_angle(player, seen_platforms[2]),
        # ]

    #ver 5b
        return [
            player.currJumpCharge / player.MAXJUMPCHARGE,
            player.hitbox.centerx / self.game_manager.screen_width,
            player.hitbox.centery / self.game_manager.screen_height,

            player.ai.previous_jump_dir / 1.0,

            # Pozycja względem centrum platformy (ograniczona)
            max(-1.0, min(1.0,
                          (player.hitbox.centerx - seen_platforms[0].hitbox.centerx) / (seen_platforms[0].hitbox.width / 2)
                          )),

            self.nearest_platform_distance(seen_platforms[1], player),
            self.nearest_platform_angle(player, seen_platforms[1]),

            self.nearest_platform_distance(seen_platforms[2], player),
            self.nearest_platform_angle(player, seen_platforms[2]),

            seen_platforms[1].hitbox.width / self.game_manager.screen_width,
            seen_platforms[2].hitbox.width / self.game_manager.screen_width,

            1.0 if player.hitbox.left < 0.05 * self.game_manager.screen_width else 0.0,
            1.0 if player.hitbox.right > 0.95 * self.game_manager.screen_width else 0.0
        ]
    def nearest_platform_distance(self, platform, player):
        x_dist = min(abs(platform.hitbox.left - player.hitbox.right), abs(platform.hitbox.right - player.hitbox.left)) / self.game_manager.screen_width
        y_dist = abs((player.hitbox.bottom - platform.hitbox.top) / self.game_manager.screen_height)

        return sqrt(pow(x_dist,2) + pow(y_dist,2))

    def nearest_platform_angle(self, player, next_platform):
        px = player.hitbox.centerx
        py = player.hitbox.bottom

        # Rogi platformy
        left_x = next_platform.hitbox.left
        right_x = next_platform.hitbox.right
        top_y = next_platform.hitbox.top

        # Wybierz bliższy róg w poziomie
        target_x = left_x if abs(left_x - px) < abs(right_x - px) else right_x

        # Oblicz kąt do tego rogu
        angle = atan2(target_x - px, top_y - py) / pi
        return angle

    def create_new_generation_if_out_of_time(self, dt):
        self.gen_timer += dt
        if self.gen_timer >= self.max_gen_time:
            self.gen_timer = 0
            self.end_generation_calculations()
            self.game_manager.reset_transitions()
            #self.game_manager.generate_platforms()
            self.run_one_generation()

    def end_generation_calculations(self):
        for player in self.game_manager.players:
            player.ai.height_record_reward()

        self.collect_and_display_gen_stats()
        self.game_manager.players.clear()

    def collect_and_display_gen_stats(self):
        fitness_stats = []
        for player in self.game_manager.players:
            fitness_stats.append(player.ai.genome.fitness)
        fitness_stats.sort(reverse=True)

        for i, fitness in enumerate(fitness_stats[:10], start=1):
            print(f"{i}. {fitness:.2f}")


