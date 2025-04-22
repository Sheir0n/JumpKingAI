import pygame
from pygame.examples.moveit import HEIGHT


class Player:
    def __init__(self, posX, posY):
        self.WIDTH = 30
        self.HEIGHT = 50

        self.posX = float(posX)
        self.posY = float(posY-self.HEIGHT)

        self.hitbox = pygame.Rect((self.posX, self.posY, self.WIDTH, self.HEIGHT))

        # how many units plyer should be able to move per second
        self.GROUNDSPEED = 275
        self.AIRSPEED = 500

        self.inAir = False
        self.MAXJUMPCHARGE = 1000
        self.MINJUMPCHARGE = 25
        self.currJumpCharge = 0.0
        self.jumpChargeRatePerSec = 750
        self.jumpDirection = 0

        self.GRAVITYRATEPERSEC = 2000
        self.TERMINALVELOCITY = -1250
        self.upAcceleration = 0.0

        # player movement controls
        # later differentiate between ai and human
        # Zmodyfikowana metoda move w klasie Player
    def move(self, deltaTime):
        key = pygame.key.get_pressed()
        
        # Obsługa ruchu poziomego - niezależnie od tego czy gracz jest w powietrzu czy nie
        if key[pygame.K_a]:
            if self.inAir:
                self.posX -= self.AIRSPEED * 0.7 * deltaTime  # Nieco zmniejszona szybkość w powietrzu dla lepszej kontroli
            else:
                self.posX -= self.GROUNDSPEED * deltaTime
        if key[pygame.K_d]:
            if self.inAir:
                self.posX += self.AIRSPEED * 0.7 * deltaTime  # Nieco zmniejszona szybkość w powietrzu dla lepszej kontroli
            else:
                self.posX += self.GROUNDSPEED * deltaTime
        
        # Obsługa skoku tylko gdy gracz jest na ziemi
        if not self.inAir:
            if key[pygame.K_SPACE]:
                self.currJumpCharge = max(self.MINJUMPCHARGE, min(self.currJumpCharge + self.jumpChargeRatePerSec * deltaTime, self.MAXJUMPCHARGE))
                print("Jump Charge: ", self.currJumpCharge)
            elif self.currJumpCharge > 0:
                self.inAir = True
                self.upAcceleration = self.currJumpCharge
                
                self.jumpDirection = 0
                # Zapisujemy kierunek skoku, ale już poruszamy się w wybranym kierunku powyżej
                if key[pygame.K_a]:
                    self.jumpDirection -= 1
                if key[pygame.K_d]:
                    self.jumpDirection += 1
                
                print("Jump! With charge: ", self.currJumpCharge)
                print("Direction: ", self.jumpDirection)
                
                self.currJumpCharge = 0
        else:
            # Aktualizacja pozycji pionowej tylko gdy jesteśmy w powietrzu
            self.posY -= self.upAcceleration * deltaTime
            self.upAcceleration = max(self.TERMINALVELOCITY, self.upAcceleration - self.GRAVITYRATEPERSEC * deltaTime)
            print("Curr acceleration: ", self.upAcceleration)
        
        # update hitbox position
        self.hitbox.topleft = (int(self.posX), int(self.posY))

    # move position of player float x and y postion to new hitbox position
    def movePosToHitbox(self):
        self.posX = self.hitbox.topleft[0]
        self.posY = self.hitbox.topleft[1]

    def groundCollision(self):
        self.upAcceleration = 0
        self.inAir = False