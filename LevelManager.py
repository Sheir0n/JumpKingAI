import pygame
from Player import Player
from Platform import  Platform
import os

#class used to move screen up or down
class LevelManager:
    def __init__(self, screen_height, screen_width, platforms):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.curr_screen_id = 0

        self.curr_checkpoint_platform_id = 0

        self.checkpoints = {0,2}
        self.checkpoint_starting_posx = platforms[0].hitbox.centerx
        self.checkpoint_starting_posy = platforms[0].hitbox.top

    def check_checkpoint_platform_id(self,players,platforms):
        for player in players:
            if player.platform_highscore >= self.curr_checkpoint_platform_id:
                for checkpoint in self.checkpoints:
                    if player.platform_highscore >= checkpoint > self.curr_checkpoint_platform_id:
                        self.curr_checkpoint_platform_id = checkpoint
                        self.checkpoint_starting_posy = platforms[checkpoint].hitbox.top
                        self.checkpoint_starting_posx = platforms[checkpoint].hitbox.centerx
                        print("new checkpoint")

    def move_objects_to_checkpoint(self,players,platforms, curr_platform_rotation):
        for player in players:
            player.posY = platforms[self.curr_checkpoint_platform_id].hitbox.top
            if curr_platform_rotation % 2 == 1:
                player.posX = platforms[self.curr_checkpoint_platform_id].hitbox.centerx
            else:
                player.posX = self.screen_width - platforms[self.curr_checkpoint_platform_id].hitbox.centerx

            player.move_pos_to_hitbox()

        self.adjust_offscreen_pos(players, platforms)

    #checks if target is offscreen
    def adjust_offscreen_pos(self, players, platforms):
        #player is obove current screen
        while players[0].hitbox.bottom < 0:
            self.move_all(players, platforms, 1)
            self.curr_screen_id += 1
            for player in players:
                player.total_screen_height -= self.screen_height

        while players[0].hitbox.bottom > self.screen_height:
            self.move_all(players, platforms, -1)
            self.curr_screen_id -= 1
            for player in players:
                player.total_screen_height += self.screen_height

    #moves all objects relatively to screen transition
    def move_all(self, players, platforms, offset_direction):
        for player in players:
            player.posY += self.screen_height * offset_direction
            player.hitbox.top = int(player.posY)

        for platform in platforms:
            platform.hitbox.top += self.screen_height * offset_direction