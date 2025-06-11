from NEATInputController import NEATInputController

class PlayerAi:
    def __init__(self, player, neat_network, get_observation, genome):
        self.player = player
        self.genome = genome
        self.genome.fitness = 75

        self.highscore_platform_reward_per_level = 200
        self.height_bonus_per_unit = 1

    def add_platform_reward(self, platform_score):
        self.genome.fitness += self.highscore_platform_reward_per_level * platform_score

    def apply_fitness_decline(self, dt):
        self.genome.fitness -= self.player.time_since_last_jump / 10 / (self.player.curr_platform_score+1)
        if self.genome.fitness <= 0:
            self.genome.fitness = 0

    def no_jump_penalty(self):
        if self.player.jump_count == 0:
            self.genome.fitness = 0

    def add_jump_bonus(self):
        self.genome.fitness += 10 * self.player.platform_highscore

    # def calculate_total_reward(self, scaled_y_reward):
    #     total_reward = 10 + self.curr_platform_reward_level * 50 + scaled_y_reward * 5 + self.jump_count*0.5
    #
    #     if self.highscore_total_reward < total_reward:
    #         self.highscore_total_reward = total_reward
    #
    #         print("Highscore!: ", total_reward)
    #
    #     if self.genome != None:
    #         self.genome.fitness = self.highscore_total_reward

    # def calculate_total_reward(self, scaled_y_reward):
    #     if self.genome != None:
    #         self.genome.fitness += scaled_y_reward * 5