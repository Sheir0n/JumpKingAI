from enum import Enum

import pygame
from InputController import PlayerInputController
from NEATInputController import NEATInputController
from PlayerAi import PlayerAi


class Player:
    def __init__(self, posX, posY, player_controlled, player_id):
        self.WIDTH = 30
        self.HEIGHT = 50

        self.posX = float(posX)
        self.posY = float(posY-self.HEIGHT)

        self.hitbox = pygame.Rect((self.posX, self.posY, self.WIDTH, self.HEIGHT))
        self.id = player_id
        self.player_controlled = player_controlled

        # how many units plyer should be able to move per second
        self.GROUNDSPEED = 275
        self.AIRSPEED = 500

        self.in_air = False
        self.MAXJUMPCHARGE = 1200
        self.MINJUMPCHARGE = 10
        self.currJumpCharge = 0.0
        self.jumpChargeRatePerSec = 800
        self.jumpDirection = 0

        self.GRAVITYRATEPERSEC = 2600
        self.TERMINALVELOCITY = -1500
        self.upAcceleration = 0.0

        self.curr_platform_id = 0
        self.curr_platform_score = 0
        self.platform_highscore = 0

        self.was_jumping_last_frame = False
        self.jump_count = 0
        self.time_since_last_jump = 0

        if self.player_controlled:
            self.controller = PlayerInputController()
        else:
            self.ai = None


    # used by AI Manager
    def create_player_ai(self, neat_network, get_observation, genome):
        self.controller = NEATInputController(neat_network, get_observation)
        self.ai = PlayerAi(self, neat_network, get_observation, genome)

    # player movement controls
    def move_player(self, delta_time):
        state = self.controller.get_input()

        self.was_jumping_last_frame = state.get("jump", False)

        if not self.in_air:
            self.time_since_last_jump += delta_time
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
                self.in_air = True
                self.upAcceleration = self.currJumpCharge

                self.jumpDirection = 0
                if state["left"]:
                    self.jumpDirection -= 1
                if state["right"]:
                    self.jumpDirection += 1

                self.jump_count += 1
                self.time_since_last_jump = 0

                if not self.player_controlled:
                    self.ai.add_jump_bonus()

                self.currJumpCharge = 0
        else:
            self.posY -= self.upAcceleration * delta_time
            self.posX += self.AIRSPEED * self.jumpDirection * delta_time
            self.upAcceleration = max(self.TERMINALVELOCITY,
                                      self.upAcceleration - self.GRAVITYRATEPERSEC * delta_time)
            #print("Curr acceleration: ", self.upAcceleration)

        # update hitbox position
        self.hitbox.topleft = (int(self.posX), int(self.posY))

    def move_ai(self, delta_time):
        state = self.controller.get_input()

        self.was_jumping_last_frame = state.get("charge_jump", False)

        if not self.in_air:
            self.time_since_last_jump += delta_time

            if not state.get("charge_jump", False) and self.currJumpCharge == 0:
                if state.get("left", False):
                    self.posX -= self.GROUNDSPEED * delta_time
                if state.get("right", False):
                    self.posX += self.GROUNDSPEED * delta_time

            elif state.get("charge_jump", False):
                self.currJumpCharge = max(
                    self.MINJUMPCHARGE,
                    min(self.currJumpCharge + self.jumpChargeRatePerSec * delta_time, self.MAXJUMPCHARGE)
                )

            elif self.currJumpCharge > 0 and state.get("release_jump", False):
                self.in_air = True
                self.upAcceleration = self.currJumpCharge

                self.jumpDirection = 0
                if state.get("left", False):
                    self.jumpDirection -= 1
                if state.get("right", False):
                    self.jumpDirection += 1

                self.jump_count += 1
                self.time_since_last_jump = 0

                if not self.player_controlled:
                    self.ai.add_jump_bonus()

                self.currJumpCharge = 0

        else:
            self.posY -= self.upAcceleration * delta_time
            self.posX += self.AIRSPEED * self.jumpDirection * delta_time
            self.upAcceleration = max(
                self.TERMINALVELOCITY,
                self.upAcceleration - self.GRAVITYRATEPERSEC * delta_time
            )
        self.hitbox.topleft = (int(self.posX), int(self.posY))

    # move position of player float x and y postion to new hitbox position
    def move_pos_to_hitbox(self):
        self.posX = self.hitbox.topleft[0]
        self.posY = self.hitbox.topleft[1]


    # methods performed on collision detection
    def platform_top_collision(self,platform_top_position):
        self.hitbox.bottom = platform_top_position
        self.upAcceleration = 0
        self.in_air = False
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

    def check_new_platform(self, new_id, new_score):
        if new_id != self.curr_platform_id:
            if self.curr_platform_score < new_score:
                self.ai.fall_penalty()

            self.curr_platform_score = new_score
            if self.curr_platform_score > self.platform_highscore:
                self.platform_highscore = self.curr_platform_score
                print("id: ", self.id, " - new highscore! ", self.platform_highscore)

                if not self.player_controlled:
                    self.ai.add_platform_reward(new_score)

