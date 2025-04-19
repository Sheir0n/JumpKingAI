import pygame
from Player import Player
import os
class GameManager:
    def __init__(self, screen):
        #screen reference
        self.screen = screen
        self.player = None

        self.screenWidth = self.screen.get_width()
        self.screenHeight = self.screen.get_height()

        self.createPlayer()
        self.platforms = []
        self.generatePlatforms()

    def createPlayer(self):
        #spawn player standing at position center
        self.player = Player( self.screenWidth/2, self.screenHeight-25)

    def generatePlatforms(self):
        self.platforms.clear()

        max_jump_height = 100  # max height which player can jump into

        file_path = os.path.join(os.path.dirname(__file__), "platformData.txt")
    
        try:
            with open(file_path, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 3:
                        width = int(parts[0])
                        x = int(parts[1])
                        y = int(parts[2])
                        platform = pygame.Rect(x, y, width, 20)
                        self.platforms.append(platform)
        except FileNotFoundError:
            print("platformData.txt not found.")

    def update(self, deltaTime):
        self.player.move(deltaTime)

        # Ograniczenia krawędzi ekranu
        if self.player.hitbox.left < 0:
            self.player.hitbox.left = 0
            self.player.movePosToHitbox()

        if self.player.hitbox.right > self.screenWidth:
            self.player.hitbox.right = self.screenWidth
            self.player.movePosToHitbox()

        if self.player.hitbox.bottom > self.screenHeight - 25:
            self.player.hitbox.bottom = self.screenHeight - 25
            self.player.movePosToHitbox()
            self.player.groundCollision()

       # Detekcja kolizji z platformami (gracz ląduje od góry)

        for platform in self.platforms:
            if self.player.posY < platform.top:
                if ((self.player.posX > platform.left and self.player.posX < (platform.left + platform.width)) 
                    or ((self.player.posX + platform.width)>platform.left 
                        and (self.player.posX + platform.width)<(platform.left + platform.width))):
                    self.player.posY=platform.top

           


    
    def drawBoard(self):
        ground = pygame.Rect((0, self.screenHeight - 25, self.screenWidth, 25))
        pygame.draw.rect(self.screen, (0, 200, 100), ground)

        for platform in self.platforms:
            pygame.draw.rect(self.screen, (0, 200, 100), platform)

    # player and object graphics
    def updateDraw(self):
        pygame.draw.rect(self.screen, (250, 0, 0), self.player.hitbox)