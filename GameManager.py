import pygame
from pygame.math import clamp

from Player import Player
from Platform import Platform
from ScreenTransitionManager import ScreenTransitionManager
from AIManager import AIManager
import os

class GameManager:
    def __init__(self, screen, is_player_controlled):
        #screen reference
        self.screen = screen
        self.players = []
        self.isPlayerControlled = is_player_controlled

        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.transition_manager = ScreenTransitionManager(self.screen_height)
        self.ai_manager = AIManager(self)

        self.curr_platform_rotation = 0

        if is_player_controlled:
            self.create_player(0)

        self.platforms = []
        self.generate_platforms()
        self.maxScore = 11
        self.win = False

    def create_player(self, id):
        #spawn player standing at position center
        self.players.append(Player(self.screen_width * 1/2, self.screen_height - 128, self.isPlayerControlled, id))

    def generate_platforms(self):
        self.curr_platform_rotation += 1
        self.platforms.clear()

        file_path = os.path.join(os.path.dirname(__file__), "platformData1.txt")

        #if self.curr_platform_rotation % 2 == 0:
            #file_path = os.path.join(os.path.dirname(__file__), "platformData1.txt")
        #else:
        #    file_path = os.path.join(os.path.dirname(__file__), "platformData2.txt")

        try:
            with open(file_path, "r") as file:
                platform_id = 0
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        x = int(parts[0])
                        # fixed y value so now larger numbers means higher in the level
                        y = self.screen_height - int(parts[1]) - int(parts[3])
                        width = int(parts[2])
                        height = int(parts[3])
                        reward_level = int(parts[4])
                        platform = Platform(x, y, width, height, reward_level, platform_id)
                        platform_id += 1
                        self.platforms.append(platform)
        except FileNotFoundError:
            print("platformData1.txt not found.")
        self.platforms.sort(key=lambda p: p.reward_level)


    #update function executes each frame
    def update(self, delta_time):
        for player in self.players:
            if not self.isPlayerControlled:
                player.move_ai(delta_time)
            else:
                player.move_player(delta_time)

            #screen edge detection
            if player.hitbox.left < 0:
                player.screen_left_edge_collision()

            if player.hitbox.right > self.screen_width:
                player.screen_right_edge_collision(self.screen_width)

            # Standing on platform detection flag
            on_platform = False

            # Detection when player walks off the platform
            for platform in self.platforms:
                if self.player_over_platform_horizontally(platform, player) and platform.hitbox.top >= player.hitbox.bottom > platform.hitbox.top - 5:
                    on_platform = True

                    #run player platform check function
                    #in case of ai control also adds fitness points
                    player.check_new_platform(platform.id, platform.reward_level)

                    if platform.reward_level == self.maxScore:
                        if self.isPlayerControlled:
                            self.victory_window()
                            self.win=True
                            return
                    break

            if not on_platform:
                player.in_air = True

            # Jumping collision detection
            for platform in self.platforms:

                if self.player_colliding(platform, player):
                    top_overlap_distance = player.hitbox.bottom - platform.hitbox.top
                    bot_overlap_distance = platform.hitbox.bottom - player.hitbox.top
                    left_overlap_distance = player.hitbox.right - platform.hitbox.left
                    right_overlap_distance = platform.hitbox.right - player.hitbox.left

                    min_overlap = min(top_overlap_distance, bot_overlap_distance, left_overlap_distance, right_overlap_distance)

                    if top_overlap_distance <= min_overlap:
                        player.platform_top_collision(platform.hitbox.top)

                    elif bot_overlap_distance <= min_overlap:
                        player.platform_bot_collision(platform.hitbox.bottom)

                    elif left_overlap_distance <= min_overlap:
                        player.platform_left_collision(platform.hitbox.left)

                    elif right_overlap_distance <= min_overlap:
                        player.platform_right_collision(platform.hitbox.right)

        #running ai generation check
        if not self.isPlayerControlled:
            self.ai_manager.create_new_generation_if_out_of_time(delta_time)

        # off screen offset adjustment
        self.transition_manager.adjust_offscreen_pos(self.players, self.platforms)

    def player_over_platform_horizontally(self, platform, player):
        if player.hitbox.right > platform.hitbox.left and player.hitbox.left < platform.hitbox.right:
            return True
        else:
            return False

    def player_colliding(self, platform, player):
        if (player.hitbox.bottom > platform.hitbox.top and player.hitbox.top < platform.hitbox.bottom) and (player.hitbox.right > platform.hitbox.left and player.hitbox.left < platform.hitbox.right):
            return True
        else:
            return False

    def draw_board(self):
        for platform in self.platforms:
            pygame.draw.rect(self.screen, (0, 200, 100), platform.hitbox)

    def reset_transitions(self):
        self.transition_manager.reset(self.players,self.platforms)

    # player and object graphics
    def update_draw(self):
        for p in self.players:
            pygame.draw.rect(self.screen, (250, 0, 0), p.hitbox)

    def victory_window(self):
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