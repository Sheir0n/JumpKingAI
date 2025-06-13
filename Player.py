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
        self.id = player_id
        self.player_controlled = player_controlled

        # how many units plyer should be able to move per second
        self.GROUNDSPEED = 275
        self.AIRSPEED = 600

        self.in_air = False
        self.MAXJUMPCHARGE = 1150
        self.MINJUMPCHARGE = 10
        self.currJumpCharge = 0.0
        self.jumpChargeRatePerSec = 862.5
        self.jumpDirection = 0

        self.GRAVITYRATEPERSEC = 2600
        self.TERMINALVELOCITY = -1500
        self.upAcceleration = 0.0

        self.curr_platform_id = 0
        self.curr_platform_score = 0
        self.platform_highscore = 0

        self.jump_count = 0
        self.time_since_last_jump = 0

        self.check_ai_jump_stack = 0
        self.prev_jump_strength = 0
        self.jump_start_posx = 0
        self.jump_start_posy = 0
        self.prev_jump_dist_difference = 0

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

                self.jump_start_posx = self.hitbox.centerx
                self.jump_start_posy = self.hitbox.bottom
                self.prev_jump_strength = self.currJumpCharge

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
        self.ai.apply_stuck_fitness_decline(delta_time)
        self.ai.no_side_movement_penalty(delta_time)

        state = self.controller.get_input()

        # Ruch w poziomie tylko gdy gracz jest na ziemi
        if not self.in_air:
            self.time_since_last_jump += delta_time
            if not state.get("jump_trigger"):
                if state["left"]:
                    self.posX -= self.GROUNDSPEED * delta_time
                if state["right"]:
                    self.posX += self.GROUNDSPEED * delta_time

            # Jeśli AI chce skakać
            if state.get("jump_trigger"):
                # Ładownie skoku
                self.currJumpCharge = max(self.MINJUMPCHARGE,
                                          min(self.currJumpCharge + self.jumpChargeRatePerSec * delta_time,
                                              self.MAXJUMPCHARGE))
                # Inicjacja skoku
                if self.currJumpCharge >= state.get("jump_strength", 0.0) * self.MAXJUMPCHARGE:
                    self.jump_start_posx = self.hitbox.centerx
                    self.jump_start_posy = self.hitbox.bottom
                    self.prev_jump_strength = self.currJumpCharge
                    self.in_air = True
                    self.upAcceleration = max(self.MINJUMPCHARGE, state.get("jump_strength", 0.0) * self.MAXJUMPCHARGE)
                    self.currJumpCharge = 0

                    # Kierunek skoku
                    self.jumpDirection = -1 if state["left"] else 1 if state["right"] else 0

                    self.jump_count += 1
                    self.time_since_last_jump = 0

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
        self.check_ai_jump_stack = 1
        self.jumpDirection = 0
        self.move_pos_to_hitbox()
        self.calculate_jump_distance()

    def calculate_jump_distance(self):
        dx = self.hitbox.centerx - self.jump_start_posx
        dy = self.hitbox.bottom - self.jump_start_posy
        self.prev_jump_dist_difference = sqrt(dx ** 2 + dy ** 2)
        if not self.player_controlled:
            self.ai.jump_distance_penalty(self.prev_jump_dist_difference)

    def platform_bot_collision(self,platform_bot_position):
        self.hitbox.top = platform_bot_position
        self.upAcceleration = 0
        self.move_pos_to_hitbox()

    def platform_left_collision(self,platform_left_position):
        self.hitbox.right = platform_left_position
        self.jumpDirection = abs(self.jumpDirection) * -0.75
        self.move_pos_to_hitbox()
        if not self.player_controlled:
            self.ai.hitbox_edge_push_penalty()

    def platform_right_collision(self, platform_right_position):
        self.hitbox.left = platform_right_position
        self.jumpDirection = abs(self.jumpDirection) * 0.75
        self.move_pos_to_hitbox()
        if not self.player_controlled:
            self.ai.hitbox_edge_push_penalty()

    def screen_left_edge_collision(self):
        self.hitbox.left = 0
        self.move_pos_to_hitbox()
        self.jumpDirection = abs(self.jumpDirection) * 0.25
        if not self.player_controlled:
            self.ai.hitbox_edge_push_penalty()

    def screen_right_edge_collision(self, screen_width):
        self.hitbox.right = screen_width
        self.move_pos_to_hitbox()
        self.jumpDirection = abs(self.jumpDirection) * -0.25
        if not self.player_controlled:
            self.ai.hitbox_edge_push_penalty()

    def check_new_platform(self, new_id, new_score):
        if new_id != self.curr_platform_id and not self.player_controlled:
            if self.curr_platform_score > new_score:
                self.ai.fall_penalty()
            elif self.curr_platform_score < new_score:
                self.ai.apply_on_higher_platform_reward(new_score)
            elif self.check_ai_jump_stack and self.curr_platform_score == new_score:
                self.check_ai_jump_stack = 0
                self.ai.jump_on_same_platform_penalty(self.prev_jump_strength / self.MAXJUMPCHARGE)

            self.curr_platform_score = new_score

            if self.curr_platform_score > self.platform_highscore:
                self.platform_highscore = self.curr_platform_score
                #print("id: ", self.id, " - new highscore! ", self.platform_highscore)

                if not self.player_controlled:
                    self.ai.apply_highscore_reward(new_score)

