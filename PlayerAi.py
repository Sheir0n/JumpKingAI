from math import sqrt

from NEATInputController import NEATInputController

class PlayerAi:
    def __init__(self, player, neat_network, get_observation, genome):
        self.player = player
        self.genome = genome
        self.genome.fitness = 0

        self.height_bonus_per_unit = 0.2

        self.max_moves = 5
        self.previous_jump_dir = 0
        self.same_dir_count = 0

    #kiedy wskoczy wyżej
    def apply_on_higher_platform_reward(self, platform_score):
        base_reward = 10
        base_reward = 0
        self.genome.fitness += base_reward * sqrt(platform_score)

    #jeśli osiągnie highscore
    def apply_highscore_reward(self, platform_score):
        base_reward = 20
        base_reward = 0
        self.genome.fitness += base_reward * sqrt(platform_score)

    def height_record_reward(self):
        height_reward_per_unit = 0.05
        self.genome.fitness += height_reward_per_unit * self.player.record_height

    #jeśli spadnie niżej
    def fall_penalty(self):
        #self.genome.fitness *= 4 / 5
        self.genome.fitness *= 1

    def jump_bonus(self):
        self.genome.fitness += 20

    def jump_penalty(self):
        self.genome.fitness -= 5

    def same_height_jump(self):
        self.genome.fitness -= 1

    def screen_edge_bounce(self):
        self.genome.fitness -= 20
        #print("edge")

    def reward_jump_direction_change(self, current_dir):
        if self.previous_jump_dir != current_dir:
            if self.previous_jump_dir != 0:
                self.genome.fitness += 5
                #print("new jump dir!")
            self.previous_jump_dir = current_dir
        else:
            self.same_dir_count += 1
            if self.same_dir_count > 3:
                self.genome.fitness -= self.same_dir_count * 10
