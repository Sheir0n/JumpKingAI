from enum import Enum
from math import sqrt

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
        self.color = (255,0,0)
        self.id = player_id
        self.player_controlled = player_controlled

        # how many units plyer should be able to move per second
        self.GROUNDSPEED = 275
        self.AIRSPEED = 600

        self.in_air = False
        self.MAXJUMPCHARGE = 1350
        self.MINJUMPCHARGE = 10
        self.currJumpCharge = 0.0
        self.jumpChargeRatePerSec = 1350
        self.jumpDirection = 0

        self.GRAVITYRATEPERSEC = 2600
        self.TERMINALVELOCITY = -1500
        self.upAcceleration = 0.0

        self.curr_platform_id = 0
        self.curr_platform_score = 0
        self.platform_highscore = 0

        self.jump_count = 0
        self.record_height = 0
        self.total_screen_height = 0
        self.jump_begin_height = 0

        self.ai_suggested_direction = 0

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

        if not self.in_air:
            if not state["jump"] and self.currJumpCharge == 0:
                if state["left"]:
                    self.posX -= self.GROUNDSPEED * delta_time
                if state["right"]:
                    self.posX += self.GROUNDSPEED * delta_time

                if (state["right"] ^ state["left"]) and not self.player_controlled:
                    self.ai.walk_bonus(delta_time)

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
        if self.jump_count < self.ai.max_moves:
            state = self.controller.get_input()
        else:
            state = self.controller.get_empty_input()

        if not self.in_air:
            if not state.get("jump_trigger"):
                if state["left"]:
                    self.posX -= self.GROUNDSPEED * delta_time
                if state["right"]:
                    self.posX += self.GROUNDSPEED * delta_time

            # Ładowanie skoku i inicjacja
            if state.get("jump_trigger"):
                target_charge = max(self.MINJUMPCHARGE, min(state.get("jump_strength", 0.0), 1.0) * self.MAXJUMPCHARGE)
                new_charge = self.currJumpCharge + self.jumpChargeRatePerSec * delta_time
                if new_charge < target_charge:
                    self.currJumpCharge = new_charge
                else:
                    # Zabezpieczenie przed przekroczeniem
                    self.currJumpCharge = target_charge

                    # Wykonaj skok dokładnie z target_charge
                    self.in_air = True
                    self.jump_begin_height = self.hitbox.bottom
                    self.upAcceleration = target_charge
                    #print("jump charge: ", self.currJumpCharge)
                    self.currJumpCharge = 0

                    # Kierunek skoku
                    self.jumpDirection = self.ai_suggested_direction
                    #print("jumping at", self.ai_suggested_direction)
                    self.ai.reward_jump_direction_change(self.jumpDirection)


                    self.jump_count += 1

        else:
            # Faza lotu
            self.posY -= self.upAcceleration * delta_time
            self.posX += self.AIRSPEED * self.jumpDirection * delta_time
            self.upAcceleration = max(self.TERMINALVELOCITY,
                                      self.upAcceleration - self.GRAVITYRATEPERSEC * delta_time)

        # update hitbox
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

        if not self.player_controlled:
            if self.hitbox.bottom < self.jump_begin_height:
                self.ai.jump_bonus()
                #print("bonus")
            elif self.hitbox.bottom > self.jump_begin_height:
                self.ai.jump_penalty()
            else:
                self.ai.same_height_jump()

    def platform_bot_collision(self,platform_bot_position):
        self.hitbox.top = platform_bot_position
        self.upAcceleration = 0
        self.move_pos_to_hitbox()

    def platform_left_collision(self,platform_left_position):
        self.hitbox.right = platform_left_position
        self.jumpDirection = abs(self.jumpDirection) * -0.5
        if self.upAcceleration > 0:
            self.upAcceleration *= 0.5
        self.move_pos_to_hitbox()

    def platform_right_collision(self, platform_right_position):
        self.hitbox.left = platform_right_position
        self.jumpDirection = abs(self.jumpDirection) * 0.5
        if self.upAcceleration > 0:
            self.upAcceleration *= 0.5
        self.move_pos_to_hitbox()

    def screen_left_edge_collision(self):
        self.hitbox.left = 0
        self.jumpDirection = abs(self.jumpDirection) * 0.05
        if self.upAcceleration > 0:
            self.upAcceleration *= 0.5
        self.move_pos_to_hitbox()
        if not self.player_controlled:
            self.ai.screen_edge_bounce()

    def screen_right_edge_collision(self, screen_width):
        self.hitbox.right = screen_width
        self.jumpDirection = abs(self.jumpDirection) * -0.05
        if self.upAcceleration > 0:
            self.upAcceleration *= 0.5
        self.move_pos_to_hitbox()
        if not self.player_controlled:
            self.ai.screen_edge_bounce()

    def check_new_platform(self, new_id, new_score):
        if new_id != self.curr_platform_id and not self.player_controlled:

            if self.curr_platform_score >= new_score:
                self.ai.fall_penalty()
            elif self.curr_platform_score + 1 == new_score:
                self.ai.apply_on_higher_platform_reward(new_score)

            self.curr_platform_score = new_score
            self.curr_platform_id = new_id

            if self.curr_platform_score + 1 == self.platform_highscore:
                self.platform_highscore = self.curr_platform_score
                #print("id: ", self.id, " - new highscore! ", self.platform_highscore)

                if not self.player_controlled:
                    self.ai.apply_highscore_reward(new_score)

    def update_record_height(self,screen_height):
        new_height = screen_height - self.hitbox.bottom
        if new_height > self.record_height:
            self.record_height = new_height

    def set_suggested_direction(self,direction):
        self.ai_suggested_direction = direction
        #print("ustawiam ", self.ai_suggested_direction)
