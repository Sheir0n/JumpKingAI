import pygame
from Player import Player
class GameManager:
    def __init__(self, screen):
        #screen reference
        self.screen = screen
        self.player = None

        self.screenWidth = self.screen.get_width()
        self.screenHeight = self.screen.get_height()

        self.createPlayer()

    def createPlayer(self):
        #spawn player standing at position center
        self.player = Player( self.screenWidth/2, self.screenHeight-25)

    def update(self, deltaTime):
        # player movement controls
        self.player.move(deltaTime)

        # checking player collisions
        if self.player.hitbox.left < 0:
            self.player.hitbox.left = 0
            self.player.movePosToHitbox()

        if self.player.hitbox.right > self.screenWidth:
            self.player.hitbox.right = self.screenWidth
            self.player.movePosToHitbox()

        if self.player.hitbox.bottom > self.screenHeight-25:
            self.player.hitbox.bottom = self.screenHeight-25
            self.player.movePosToHitbox()
            self.player.groundCollision()


    # player and object graphics
    def updateDraw(self):
        pygame.draw.rect(self.screen, (250, 0, 0), self.player.hitbox)