from math import sqrt

from pygame.math import clamp
import weakref

class PlayerAi:
    instance_count = 0
    def __init__(self, player, genome):
        self.player = weakref.ref(player)
        self.genome = weakref.ref(genome)
        self.genome().fitness = 0

        self.height_bonus_per_unit = 0.025

        self.max_moves = 5
        self.previous_jump_dir = 0
        self.same_dir_count = 0

        self.edge_bounce_count = 0

        self.height_reward_per_unit = 0.1
        #self.height_reward_per_unit = 0
        self.height_enabled = True

        PlayerAi.instance_count += 1
        #print("PlayerAi count:", PlayerAi.instance_count)

    #kiedy wskoczy wyżej
    def apply_on_higher_platform_reward(self, platform_score):
        base_reward = 10
        enabled = True
        if enabled:
            self.edge_bounce_count = 0
            self.genome().fitness += base_reward * sqrt(platform_score)

    #jeśli osiągnie highscore
    def apply_highscore_reward(self, platform_score):
        base_reward = 30
        enabled = False
        if enabled:
            self.genome().fitness += base_reward * sqrt(platform_score)

    def height_record_reward(self):
        if self.height_enabled:
            #self.genome().fitness += self.height_reward_per_unit * (self.player().record_height + self.player().screen_count * self.player().screen_height)
            self.genome().fitness += self.height_reward_per_unit * (
                        self.player().record_height)

    #jeśli spadnie niżej
    def fall_penalty(self):
        enabled = False
        mul_penalty = 5/6
        add_penalty = 10
        if enabled:
            self.genome().fitness *= mul_penalty
            self.genome().fitness -= add_penalty

    #jeśli skoczy wyżej
    def jump_bonus(self):
        enabled = False
        if enabled:
            self.genome().fitness += 10

    #jeśli skoczy niżej
    def jump_penalty(self):
        enabled = False
        if enabled:
            self.genome().fitness -= 10

    #jeśli skacze na tej samej wysokości
    def same_height_jump(self):
        enabled = False
        if enabled:
            self.genome().fitness -= 8

    #odbicie się od krawędzi ekranu
    def screen_edge_bounce(self):
        enabled = False
        base_penalty = 3
        if enabled:
            self.edge_bounce_count += 1
            if self.edge_bounce_count > 1:
                self.genome().fitness -= base_penalty

    def walk_bonus(self,dt):
        enabled = False
        if enabled:
            base_walk_bonus = 4
            self.genome().fitness += base_walk_bonus * dt

    def jump_in_correct_direction(self, is_correct):
        enabled_bonus = True
        enabled_penalty = True

        if enabled_bonus:
            if is_correct:
                base_bonus = 1
                self.genome().fitness += base_bonus


        if enabled_penalty:
            if not is_correct:
                base_penalty = 1/2
                self.genome().fitness *= base_penalty

    def change_fitness_color(self,record):
        if record <= 0:
            return

        if self.height_enabled:
            height_record_fitness = self.height_reward_per_unit * self.player().record_height
            calculated_fitness = (self.genome().fitness + height_record_fitness) / record
        else:
            calculated_fitness = self.genome().fitness / record


        if calculated_fitness > 1.25:
            self.player().color = (0, 255, 200)
            return
        elif calculated_fitness > 1:
            self.player().color = (64,255,64)
            return
        else:
            fitness_color = 255 * clamp(calculated_fitness,0,1)
            self.player().color = (255,fitness_color,fitness_color)

    def __del__(self):
        PlayerAi.instance_count -= 1
        #print("PlayerAi deleted. Remaining:", PlayerAi.instance_count)

