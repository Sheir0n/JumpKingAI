from math import sqrt

from pygame.math import clamp

from NEATInputController import NEATInputController

class PlayerAi:
    def __init__(self, player, neat_network, get_observation, genome):
        self.player = player
        self.genome = genome
        self.genome.fitness = 10

        self.height_bonus_per_unit = 0.2

        self.max_moves = 5
        self.previous_jump_dir = 0
        self.same_dir_count = 0

        self.edge_bounce_count = 0

        self.height_reward_per_unit = 0.05
        self.height_reward_per_unit = 0
        self.height_enabled = False

    #kiedy wskoczy wyżej
    def apply_on_higher_platform_reward(self, platform_score):
        base_reward = 10
        enabled = True
        if enabled:
            self.edge_bounce_count = 0
            self.genome.fitness += base_reward * sqrt(platform_score)

    #jeśli osiągnie highscore
    def apply_highscore_reward(self, platform_score):
        base_reward = 20
        enabled = False
        if enabled:
            self.genome.fitness += base_reward * sqrt(platform_score)

    def height_record_reward(self):
        if self.height_enabled:
            if self.edge_bounce_count <= 2:
                self.genome.fitness += self.height_reward_per_unit * (self.player.record_height + self.player.total_screen_height)

    #jeśli spadnie niżej
    def fall_penalty(self):
        enabled = False
        if enabled:
            self.genome.fitness *= 3 / 5

    #jeśli skoczy wyżej
    def jump_bonus(self):
        enabled = True
        if enabled:
            self.genome.fitness += 10

    #jeśli skoczy niżej
    def jump_penalty(self):
        enabled = True
        if enabled:
            self.genome.fitness -= 8

    #jeśli skacze na tej samej wysokości
    def same_height_jump(self):
        enabled = True
        if enabled:
            self.genome.fitness -= 5

    #odbicie się od krawędzi ekranu
    def screen_edge_bounce(self):
        enabled = False
        if enabled:
            self.edge_bounce_count += 1
            if self.edge_bounce_count > 1:
                self.genome.fitness -= 10

    #nagroda/kara za zmianę kierunku skoku
    def reward_jump_direction_change(self, current_dir):
        enabled = False
        if enabled:
            if self.previous_jump_dir != current_dir:
                if self.previous_jump_dir != 0:
                    self.genome.fitness += 5
                    self.edge_bounce_count = 0
                    #print("new jump dir!")
                self.previous_jump_dir = current_dir
            else:
                self.same_dir_count += 1
                if self.same_dir_count > 3:
                    self.genome.fitness -= self.same_dir_count * 2

    def walk_bonus(self,dt):
        enabled = True
        if enabled:
            base_walk_bonus = 3
            self.genome.fitness += base_walk_bonus * dt

    def change_fitness_color(self,record):
        if record <= 0:
            fitness_color = 0
        elif self.height_enabled:
            fitness_color = 255 * clamp((self.genome.fitness + (self.height_reward_per_unit * self.player.record_height))
                                        /record,0,1)
        else:
            fitness_color = 255 * clamp(self.genome.fitness / record, 0, 1)

        self.player.color = (255,fitness_color,fitness_color)

