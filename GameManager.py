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

    # Poprawiony fragment metody update w gamemanager.py
    def update(self, deltaTime):
        # Zapisujemy poprzednią pozycję Y przed ruchem
        old_y = self.player.posY
        
        # Wykonujemy ruch gracza
        self.player.move(deltaTime)

        # Ograniczenia krawędzi ekranu
        if self.player.hitbox.left < 0:
            self.player.hitbox.left = 0
            self.player.movePosToHitbox()

        if self.player.hitbox.right > self.screenWidth:
            self.player.hitbox.right = self.screenWidth
            self.player.movePosToHitbox()

        # Sprawdzamy kolizję z ziemią
        if self.player.hitbox.bottom > self.screenHeight - 25:
            self.player.hitbox.bottom = self.screenHeight - 25
            self.player.movePosToHitbox()
            self.player.groundCollision()
        
        # Flaga do śledzenia, czy gracz stoi na platformie
        on_platform = False
        
        # Detekcja kolizji z platformami
        for platform in self.platforms:
            # Sprawdzamy czy gracz jest nad platformą (poziomo)
            player_over_platform_horizontally = (
                self.player.hitbox.right > platform.left and
                self.player.hitbox.left < platform.right
            )
            
            # Sprawdzamy lądowanie na platformie (kolizja od góry)
            if player_over_platform_horizontally:
                # Gracz spadał (poprzednia pozycja była wyżej niż obecna)
                is_falling = old_y < self.player.posY
                
                # Sprawdzamy czy spód gracza jest w zakresie kolizji z górą platformy
                feet_at_platform_level = (
                    self.player.hitbox.bottom >= platform.top and
                    self.player.hitbox.bottom <= platform.top + 20  # Tolerancja kolizji
                )
                
                if is_falling and feet_at_platform_level:
                    # Ustawiamy gracza na górze platformy
                    self.player.hitbox.bottom = platform.top
                    self.player.movePosToHitbox()
                    self.player.groundCollision()
                    on_platform = True
                    break  # Przerywamy pętlę, bo gracz już wylądował
        
        # Jeśli gracz nie stoi na ziemi ani na platformie, powinien spadać
        if not on_platform and self.player.hitbox.bottom < self.screenHeight - 25:
            if not self.player.inAir:
                self.player.inAir = True
                self.player.upAcceleration = 0  # Zaczynamy spadać

           


    
    def drawBoard(self):
        ground = pygame.Rect((0, self.screenHeight - 25, self.screenWidth, 25))
        pygame.draw.rect(self.screen, (0, 200, 100), ground)

        for platform in self.platforms:
            pygame.draw.rect(self.screen, (0, 200, 100), platform)

    # player and object graphics
    def updateDraw(self):
        pygame.draw.rect(self.screen, (250, 0, 0), self.player.hitbox)