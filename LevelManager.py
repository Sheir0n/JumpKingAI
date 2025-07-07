import pygame
from Player import Player
from Platform import  Platform
import os

#class used to move screen up or down
class LevelManager:
    def __init__(self, screen_height, screen_width, platforms, is_rotating):
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.curr_screen_id = 0

        self.curr_checkpoint_platform_id = 0

        self.checkpoints = {0,3,7,11,15,18}
        self.checkpoint_starting_posy = platforms[self.curr_checkpoint_platform_id].total_y_pos
        self.checkpoint_starting_posx = platforms[self.curr_checkpoint_platform_id].hitbox.centerx

        self.rotating_platforms = False

    def check_checkpoint_platform_id(self,players,platforms):
        for player in players:
            if player.curr_platform_id > self.curr_checkpoint_platform_id:
                for checkpoint in self.checkpoints:
                    if player.curr_platform_id >= checkpoint > self.curr_checkpoint_platform_id:
                        self.curr_checkpoint_platform_id = checkpoint
                        self.checkpoint_starting_posy = platforms[self.curr_checkpoint_platform_id].total_y_pos
                        self.checkpoint_starting_posx = platforms[self.curr_checkpoint_platform_id].hitbox.centerx
                        print("new checkpoint", self.curr_checkpoint_platform_id)
                        #print("checkpint posy", platforms[checkpoint].total_y_pos)
                        return player
        return None

    def move_objects_to_checkpoint(self,players, platforms, curr_platform_rotation):
        for player in players:
            player.posY = platforms[self.curr_checkpoint_platform_id].hitbox.top
            if curr_platform_rotation % 2 == 0 or not self.rotating_platforms:
                player.posX = platforms[self.curr_checkpoint_platform_id].hitbox.centerx
            else:
                player.posX = self.screen_width - platforms[self.curr_checkpoint_platform_id].hitbox.centerx

            player.move_pos_to_hitbox()

    #checks if target is offscreen
    def adjust_offscreen_pos(self, players, platforms):
        #player is obove current screen
        highest_player = self.get_highest_player(players)

        while highest_player.hitbox.bottom < 0:
            self.move_all(players, platforms, 1)
            self.curr_screen_id += 1
            for player in players:
                player.screen_count += 1

        while highest_player.hitbox.bottom > self.screen_height:
            self.move_all(players, platforms, -1)
            self.curr_screen_id -= 1
            for player in players:
                player.screen_count -= 1

    def get_highest_player(self, players):
        highest_player = players[0]
        highest = (self.screen_height - players[0].hitbox.bottom) + players[0].screen_count * self.screen_height
        for player in players:
            height_value = (self.screen_height - player.hitbox.bottom) + player.screen_count * self.screen_height
            if highest < height_value:
                highest_player = player
                highest = height_value
        return highest_player

    #moves all objects relatively to screen transition
    def move_all(self, players, platforms, offset_direction):
        for player in players:
            player.posY += self.screen_height * offset_direction
            player.hitbox.top = int(player.posY)

        for platform in platforms:
            platform.hitbox.top += self.screen_height * offset_direction

    def reset_screens_to_zero(self, players, platforms):
        offset_direction = -self.curr_screen_id

        self.move_all(players, platforms, offset_direction)

        self.curr_screen_id = 0

        for player in players:
            player.screen_count += offset_direction