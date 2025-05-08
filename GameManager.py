import pygame
from Player import Player
from Platform import Platform
from ScreenTransitionManager import ScreenTransitionManager
import os
class GameManager:
    def __init__(self, screen, isPlayerControlled):
        #screen reference
        self.screen = screen
        self.player = None
        self.isPlayerControlled = isPlayerControlled

        self.screenWidth = self.screen.get_width()
        self.screenHeight = self.screen.get_height()

        self.transition_manager = ScreenTransitionManager(self.screenHeight)

        self.createPlayer()
        self.platforms = []
        self.generatePlatforms()
        self.maxScore = len(self.platforms)-3
        print(self.maxScore)
        self.win = False

    def createPlayer(self):
        #spawn player standing at position center
        self.player = Player( self.screenWidth/2, self.screenHeight-128, self.isPlayerControlled)

    def generatePlatforms(self):
        self.platforms.clear()

        max_jump_height = 100  # max height which player can jump into

        file_path = os.path.join(os.path.dirname(__file__), "platformData.txt")
    
        try:
            with open(file_path, "r") as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        x = int(parts[0])
                        # fixed y value so now larger numbers means higher in the level
                        y = self.screenHeight - int(parts[1]) - int(parts[3])
                        width = int(parts[2])
                        height = int(parts[3])
                        reward_level = int(parts[4])
                        platform = Platform(x, y, width, height, reward_level)
                        self.platforms.append(platform)
        except FileNotFoundError:
            print("platformData.txt not found.")

    #update function executes each frame
    def update(self, delta_time):
        self.player.move(delta_time)

        #screen edge detection
        if self.player.hitbox.left < 0:
            self.player.hitbox.left = 0
            self.player.move_pos_to_hitbox()

        if self.player.hitbox.right > self.screenWidth:
            self.player.hitbox.right = self.screenWidth
            self.player.move_pos_to_hitbox()


        # Standing on platform detection flag
        on_platform = False

        # Detection when player walks off the platform
        for platform in self.platforms:

            if self.player_over_platform_horizontally(platform) and platform.hitbox.top >= self.player.hitbox.bottom > platform.hitbox.top - 5:
                on_platform = True
                self.player.check_reward(platform.reward_level)
                if platform.reward_level == self.maxScore:
                    if self.isPlayerControlled:
                        self.victoryWindow()
                        self.win=True
                        return
                    else:
                        self.player = None
                break

        if not on_platform:
            self.player.inAir = True

        # Jumping collision detection
        for platform in self.platforms:

            if self.player_colliding(platform):
                top_overlap_distance = self.player.hitbox.bottom - platform.hitbox.top
                bot_overlap_distance = platform.hitbox.bottom - self.player.hitbox.top
                left_overlap_distance = self.player.hitbox.right - platform.hitbox.left
                right_overlap_distance = platform.hitbox.right - self.player.hitbox.left

                min_overlap = min(top_overlap_distance, bot_overlap_distance, left_overlap_distance, right_overlap_distance)

                if top_overlap_distance <= min_overlap:
                    self.player.platform_top_collision(platform.hitbox.top)

                elif bot_overlap_distance <= min_overlap:
                   self.player.platform_bot_collision(platform.hitbox.bottom)

                elif left_overlap_distance <= min_overlap:
                    self.player.platform_left_collision(platform.hitbox.left)

                elif right_overlap_distance <= min_overlap:
                    self.player.platform_right_collision(platform.hitbox.right)

        # off screen offset adjustment
        self.transition_manager.adjust_offscreen_pos(self.player,self.platforms)

    def player_over_platform_horizontally(self, platform):
        if self.player.hitbox.right > platform.hitbox.left and self.player.hitbox.left < platform.hitbox.right:
            return True
        else:
            return False

    def player_colliding(self, platform):
        if (self.player.hitbox.bottom > platform.hitbox.top and self.player.hitbox.top < platform.hitbox.bottom) and (self.player.hitbox.right > platform.hitbox.left and self.player.hitbox.left < platform.hitbox.right):
            return True
        else:
            return False

    def drawBoard(self):
        for platform in self.platforms:
            pygame.draw.rect(self.screen, (0, 200, 100), platform.hitbox)

    # player and object graphics
    def updateDraw(self):
        pygame.draw.rect(self.screen, (250, 0, 0), self.player.hitbox)

    def victoryWindow(self):
        SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Victory Screen")

        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        font = pygame.font.SysFont(None, 72)

        text = font.render("You win!", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        running = True
        while running:
            screen.fill(BLACK)
            screen.blit(text, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()