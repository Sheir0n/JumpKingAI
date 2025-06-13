from math import sqrt

from NEATInputController import NEATInputController

class PlayerAi:
    def __init__(self, player, neat_network, get_observation, genome):
        self.player = player
        self.genome = genome
        self.genome.fitness = 0

        self.highscore_platform_reward_per_level = 10
        self.height_bonus_per_unit = 0.2

        self.curr_stuck_time_s = 0
        self.penalty_stuck_time_s = 3

        self.hitbox_side_hit_count = 0
        self.last_x_pos = 0

    #kiedy wskoczy wyżej
    def apply_on_higher_platform_reward(self, platform_score):
        base_reward = 20
        self.genome.fitness += base_reward * sqrt(platform_score)
        self.curr_stuck_time_s = 0

    #w każdej klatce
    def apply_stuck_fitness_decline(self, dt):
        base_decline_per_sec = 1

        self.curr_stuck_time_s += dt
        if self.curr_stuck_time_s > self.penalty_stuck_time_s:
            self.genome.fitness -= base_decline_per_sec * dt * sqrt(self.curr_stuck_time_s)

    #jeśli osiągnie highscore
    def apply_highscore_reward(self, platform_score):
        base_reward = 100
        self.genome.fitness += base_reward * sqrt(platform_score)

    #jeśli spadnie niżej
    def fall_penalty(self):
        self.genome.fitness *= 4 / 5
        self.curr_stuck_time_s = 0

    #na samym końcu generacji
    def distance_to_next_platform_bonus(self,platforms, screen_width, screen_height):
        curr_id = self.player.curr_platform_id
        next_platforms = platforms[curr_id:curr_id + 2]

        max_score = 10
        if len(next_platforms) < 2 and next_platforms:
            last = next_platforms[-1]
            next_platforms.extend([last] * (2 - len(next_platforms)))

        #normalized distance to next platform
        norm_distance = sqrt(pow(min(
            abs(self.player.hitbox.centerx - next_platforms[1].hitbox.left),abs(self.player.hitbox.centerx - next_platforms[1].hitbox.right))/screen_width,2
        ) + pow((self.player.hitbox.bottom - next_platforms[1].hitbox.top) / screen_height,2))

        bonus_score = (1 - norm_distance) * max_score
        self.genome.fitness += bonus_score

    #na samym końcu generacji jeśli nie skoczy ani raz
    def no_jump_penalty(self):
        self.genome.fitness -= 100

    #jeśli obije się o inny blok lub krawędź ekranu (test w każdej klatce)
    def hitbox_edge_push_penalty(self):
        base_penalty_per_air_push = 10

        base_penalty_per_air_push = 5

        if self.player.in_air:
            self.genome.fitness -= (base_penalty_per_air_push * sqrt(sqrt(self.hitbox_side_hit_count))) / (self.player.curr_platform_score + 1)
            self.hitbox_side_hit_count += 1
            #print("im edging (in air) ", self.hitbox_side_hit_count, " ", self.genome.fitness)

    def no_side_movement_penalty(self, dt):
        base_penalty_per_sec = 20
        if abs(self.player.hitbox.centerx - self.last_x_pos) < 1:
            self.genome.fitness -= base_penalty_per_sec * dt

    def jump_on_same_platform_penalty(self, jump_strength):
        if jump_strength <= 0.01:
            jump_strength = 0.01
        #self.genome.fitness -= jump_strength

    def jump_distance_penalty(self,distance):
        min_distance = 20
        if distance < min_distance:
            self.genome.fitness -= min_distance - distance
