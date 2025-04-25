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
        self.MAXJUMPCHARGE = 1200
        self.MINJUMPCHARGE = 10
        self.currJumpCharge = 0.0
        self.jumpChargeRatePerSec = 800
        self.jumpDirection = 0

        self.GRAVITYRATEPERSEC = 2500
        self.TERMINALVELOCITY = -1500
        self.upAcceleration = 0.0

    # player movement controls
    # later differentiate between ai and human
    def move(self, deltaTime):
        key = pygame.key.get_pressed()
        if not self.inAir:
            if not key[pygame.K_SPACE] and self.currJumpCharge == 0:
                if key[pygame.K_a]:
                    self.posX -= self.GROUNDSPEED * deltaTime
                if key[pygame.K_d]:
                    self.posX += self.GROUNDSPEED * deltaTime

            elif key[pygame.K_SPACE]:
                self.currJumpCharge = max(self.MINJUMPCHARGE,
                                          min(self.currJumpCharge + self.jumpChargeRatePerSec * deltaTime,
                                              self.MAXJUMPCHARGE))
                #print("Jump Charge: ", self.currJumpCharge)

            elif self.currJumpCharge > 0:
                self.inAir = True
                self.upAcceleration = self.currJumpCharge

                self.jumpDirection = 0
                if key[pygame.K_a]:
                    self.jumpDirection -= 1
                if key[pygame.K_d]:
                    self.jumpDirection += 1

                #print("Jump! With charge: ", self.currJumpCharge)
                #print("Direction: ", self.jumpDirection)

                self.currJumpCharge = 0
        else:
            self.posY -= self.upAcceleration * deltaTime
            self.posX += self.AIRSPEED * self.jumpDirection * deltaTime
            self.upAcceleration = max(self.TERMINALVELOCITY,
                                      self.upAcceleration - self.GRAVITYRATEPERSEC * deltaTime)
            #print("Curr acceleration: ", self.upAcceleration)

        # update hitbox position
        self.hitbox.topleft = (int(self.posX), int(self.posY))

    # move position of player float x and y postion to new hitbox position
    def move_pos_to_hitbox(self):
        self.posX = self.hitbox.topleft[0]
        self.posY = self.hitbox.topleft[1]


    # methods performed on collision detection
    def platform_top_collision(self,platform_top_position):
        self.hitbox.bottom = platform_top_position
        self.upAcceleration = 0
        self.inAir = False
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