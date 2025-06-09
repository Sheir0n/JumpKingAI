from enum import Enum

import pygame
from InputController import PlayerInputController
from InputController import NEATInputController

class Player:
    def __init__(self, posX, posY, player_controlled):
        self.WIDTH = 30
        self.HEIGHT = 50

        self.posX = float(posX)
        self.posY = float(posY-self.HEIGHT)

        self.hitbox = pygame.Rect((self.posX, self.posY, self.WIDTH, self.HEIGHT))

        # how many units plyer should be able to move per second
        self.GROUNDSPEED = 275
        self.AIRSPEED = 500

        self.inAir = False
        self.MAXJUMPCHARGE = 1200
        self.MINJUMPCHARGE = 10
        self.currJumpCharge = 0.0
        self.jumpChargeRatePerSec = 800
        self.jumpDirection = 0

        self.GRAVITYRATEPERSEC = 2600
        self.TERMINALVELOCITY = -1500
        self.upAcceleration = 0.0

        self.highscore_platform_reward_level = 0
        self.curr_platform_reward_level = 0
        self.highscore_total_reward = 0

        self.curr_platform_id = 0

        self.was_jumping_last_frame = False
        self.jump_count = 0

        # used only in AI mode
        self.fitness = None
        self.genome = None

        if(player_controlled):
            self.controller = PlayerInputController()

    # used by AI Manager
    def AIInputs(self, neat_network, get_observation, genome):
        self.controller = NEATInputController(neat_network, get_observation)
        self.genome = genome
        self.genome.fitness = 0

    # player movement controls
    # later differentiate between ai and human
    def move(self, delta_time):
        #key = pygame.key.get_pressed()
        state = self.controller.get_input()
        self.was_jumping_last_frame = state.get("jump", False)

        if not self.inAir:
            if not state["jump"] and self.currJumpCharge == 0:
                if state["left"]:
                    self.posX -= self.GROUNDSPEED * delta_time
                if state["right"]:
                    self.posX += self.GROUNDSPEED * delta_time

            elif state["jump"]:
                self.currJumpCharge = max(self.MINJUMPCHARGE,
                                          min(self.currJumpCharge + self.jumpChargeRatePerSec * delta_time,
                                              self.MAXJUMPCHARGE))

            elif self.currJumpCharge > 0:
                self.inAir = True
                self.upAcceleration = self.currJumpCharge

                self.jumpDirection = 0
                if state["left"]:
                    self.jumpDirection -= 1
                if state["right"]:
                    self.jumpDirection += 1

                self.jump_count += 1

                self.currJumpCharge = 0
        else:
            self.posY -= self.upAcceleration * delta_time
            self.posX += self.AIRSPEED * self.jumpDirection * delta_time
            self.upAcceleration = max(self.TERMINALVELOCITY,
                                      self.upAcceleration - self.GRAVITYRATEPERSEC * delta_time)
            #print("Curr acceleration: ", self.upAcceleration)

        # update hitbox position
        self.hitbox.topleft = (int(self.posX), int(self.posY))

    # move position of player float x and y postion to new hitbox position
    def move_pos_to_hitbox(self):
        self.posX = self.hitbox.topleft[0]
        self.posY = self.hitbox.topleft[1]


    # methods performed on collision detection
    def platform_top_collision(self,platform_top_position):
        self.hitbox.bottom = platform_top_position
        self.upAcceleration = 0
        self.inAir = False
        self.jumpDirection = 0
        self.move_pos_to_hitbox()

    def platform_bot_collision(self,platform_bot_position):
        self.hitbox.top = platform_bot_position
        self.upAcceleration = 0
        self.move_pos_to_hitbox()

    def platform_left_collision(self,platform_left_position):
        self.hitbox.right = platform_left_position
        self.jumpDirection = abs(self.jumpDirection) * -0.75
        self.move_pos_to_hitbox()

    def platform_right_collision(self, platform_right_position):
        self.hitbox.left = platform_right_position
        self.jumpDirection = abs(self.jumpDirection) * 0.75
        self.move_pos_to_hitbox()


    # --- ai stuff here

    def calculate_curr_reward(self, new_level, platform_id):
        self.genome.fitness -= 0.001

        # Kara za czas (motywuje do szybszego przechodzenia poziomów)
        self.genome.fitness -= 0.001

        if self.curr_platform_id != platform_id:
            self.curr_platform_id = platform_id
            print("standing on id:", platform_id)

        if new_level > self.curr_platform_reward_level:
            self.curr_platform_reward_level = new_level
            if new_level > self.highscore_platform_reward_level:
                self.highscore_platform_reward_level = new_level
                # Większa nagroda za pobicie rekordu
                self.genome.fitness += 100 * new_level

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