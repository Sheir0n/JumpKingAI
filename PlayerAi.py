from math import sqrt

from NEATInputController import NEATInputController

class PlayerAi:
    def __init__(self, player, neat_network, get_observation, genome):
        self.player = player
        self.genome = genome
        self.genome.fitness = 0

        self.highscore_platform_reward_per_level = 10
        self.height_bonus_per_unit = 0.2

    # wywoływana po uzyskaniu nowego highscore platformy
    def add_platform_reward(self, platform_score):
        self.genome.fitness += self.highscore_platform_reward_per_level * platform_score

    # redukcja fitnessu w przypadku długiego czasu bez skoku (tylko po wskoczeniu na 1 platformę)
    # raz na klatkę skalowane przez dt
    def apply_fitness_decline(self, dt):
        if self.player.time_since_last_jump > 3.5 and self.player.platform_highscore > 0:
            self.genome.fitness -= ((self.player.time_since_last_jump-3.5) /2000) / (self.player.curr_platform_score+1)
            if self.genome.fitness <= 0:
                self.genome.fitness = 0

    # jeśli nie było żadnego skoku duża redukcja
    def no_jump_penalty(self):
         if self.player.jump_count == 0:
             self.genome.fitness = max(self.genome.fitness-15,0)

    # bonus za poprawny skok
    def add_jump_bonus(self):
        self.genome.fitness += 3 * (self.player.platform_highscore+1)

    # kara za upadek
    def fall_penalty(self):
        self.genome.fitness *= 2/3

    # bonus za osiągnięty dystans do kolejnej platformy
    def distance_to_next_platform_bonus(self,platforms, screen_width, screen_height):
        curr_id = self.player.curr_platform_id
        next_platforms = platforms[curr_id:curr_id + 2]
        if len(next_platforms) < 2 and next_platforms:
            last = next_platforms[-1]
            next_platforms.extend([last] * (2 - len(next_platforms)))

        #normalized distance to next platform
        norm_distance = sqrt(pow(min(
            abs(self.player.hitbox.centerx - next_platforms[1].hitbox.left),abs(self.player.hitbox.centerx - next_platforms[1].hitbox.right))/screen_width,2
        ) + pow((self.player.hitbox.bottom - next_platforms[1].hitbox.top) / screen_height,2))

        bonus_score = (1 - norm_distance) * 10 * (self.player.platform_highscore+1)
        #print(norm_distance)

        self.genome.fitness += bonus_score

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