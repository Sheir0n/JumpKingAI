import pygame
from Player import Player
import os

#class used to move screen up or down
class ScreenTransitionManager:
    def __init__(self, screen_height):
        self.screen_height = screen_height
        self.currScreenId = 0

    #checks if target is offscreen
    def adjust_offscreen_pos(self, players, platforms):
        #player is obove current screen
        if players[0].hitbox.bottom < 0:
            self.move_all(players, platforms, 1)
            self.currScreenId += 1

        elif players[0].hitbox.bottom > self.screen_height:
            self.move_all(players, platforms, -1)
            self.currScreenId -= 1

    #moves all objects relatively to screen transition
    def move_all(self, players, platforms, offset_direction):
        for player in players:
            player.posY += self.screen_height * offset_direction
            player.hitbox.top = int(player.posY)

        for platform in platforms:
            platform.hitbox.top += self.screen_height * offset_direction

    def reset(self,players,platforms):
        for platform in platforms:
            platform.reset_pos()
        self.currScreenId = 0