import pygame
from pygame.math import clamp

from Player import Player
from Platform import Platform
from LevelManager import LevelManager
from AIManager import AIManager
from Background import Background
import os
import gc

class GameManager:
    def __init__(self, screen, is_player_controlled):
        #screen reference
        self.screen = screen
        self.players = []
        self.isPlayerControlled = is_player_controlled

        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        self.curr_platform_rotation = 0

        self.platforms = []
        self.rotating_platforms = False
        self.generate_platforms()
        self.level_manager = LevelManager(self.screen_height,self.screen_width, self.platforms,self.rotating_platforms)

        if is_player_controlled:
            self.create_player(0)
        else:
            self.ai_manager = AIManager(self)

        self.maxScore = self.platforms[-1].reward_level
        self.win = False
        gc.enable()

        self.background = Background("textures/bg.png", self.screen_width, self.screen_height,4)

        self.disable_players_on_checkpoint = False
        self.end_generation_early = False

    #player controlled
    def create_player(self, id):
        #spawn player standing at position center
        player = Player(self.level_manager.checkpoint_starting_posx, self.level_manager.checkpoint_starting_posy, self.isPlayerControlled, id, self.screen_height)
        self.players.append(player)
        return player

    #ai_controlled
    def create_player_ai(self, player_id, net, genome):
        #spawn player standing at position center
        self.level_manager.reset_screens_to_zero(self.players, self.platforms)
        player = Player(self.level_manager.checkpoint_starting_posx, self.level_manager.checkpoint_starting_posy, self.isPlayerControlled, player_id, self.screen_height)
        player.create_player_ai(net, self.ai_manager.observation_func, genome)
        self.players.append(player)
        #print("spawned at: ", self.level_manager.checkpoint_starting_posx, "", self.level_manager.checkpoint_starting_posy)
        return player

    def generate_platforms(self):
        self.curr_platform_rotation += 1
        self.platforms.clear()

        file_path = os.path.join(os.path.dirname(__file__), "platformData1.txt")

        if self.curr_platform_rotation % 2 == 0 or not self.rotating_platforms:
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
        else:
            try:
                with open(file_path, "r") as file:
                    platform_id = 0
                    for line in file:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            original_x = int(parts[0])
                            y_from_bottom = int(parts[1])
                            width = int(parts[2])
                            height = int(parts[3])
                            reward_level = int(parts[4])

                            # Lustro w osi X
                            x = self.screen_width - (original_x + width)

                            # Odwrócenie osi Y tak jak wcześniej
                            y = self.screen_height - y_from_bottom - height

                            platform = Platform(x, y, width, height, reward_level, platform_id)
                            platform_id += 1
                            self.platforms.append(platform)
            except FileNotFoundError:
                print("platformData1.txt not found.")

            self.platforms.sort(key=lambda p: p.reward_level)

    #update function executes each frame
    def update(self, delta_time):
        # checking player reaching checkpoints
        first_player = self.level_manager.check_checkpoint_platform_id(self.players, self.platforms)
        if first_player != None:
            if not self.isPlayerControlled:
                self.ai_manager.best_genomes.append(first_player.ai.genome())
            if self.disable_players_on_checkpoint:
                for player in self.players:
                    print("disabling player")
                    player.disable_jumping = True
                    self.end_generation_early = True

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
                    player.check_new_platform(platform.id, platform.reward_level)
                    if platform.reward_level == self.maxScore:
                        self.win=True
                        if self.isPlayerControlled:
                            self.victory_window()
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
            
        # off screen offset adjustment
        self.level_manager.adjust_offscreen_pos(self.players, self.platforms)



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

    def move_to_checkpoint(self):
        self.level_manager.move_objects_to_checkpoint(self.players,self.platforms,self.curr_platform_rotation)

    def draw_bg(self):
        self.background.update_offset(self.level_manager.curr_screen_id)
        self.screen.blit(self.background.image, (0, 0), self.background.rect)

    def draw_board(self):
        for platform in self.platforms:
            self.screen.blit(platform.image, platform.hitbox.topleft)

    # player and object graphics
    def update_draw(self):
        if not self.isPlayerControlled:
            for p in self.players:
                p.ai.change_fitness_color(self.ai_manager.fitness_record)
               # print("im colorful")

        for p in self.players:
            pygame.draw.rect(self.screen, p.color, p.hitbox)

    def victory_window(self):
        SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Victory - Jump King AI")

        # Kolory w stylu pixel-art
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        YELLOW = (255, 230, 0)

        # Styl retro: czcionka pixel-art
        title_font = pygame.font.Font("pixel_font.ttf", 64)
        message_font = pygame.font.Font("pixel_font.ttf", 48)
        footer_font = pygame.font.Font("pixel_font.ttf", 24)

        title = title_font.render("JUMP KING AI", True, YELLOW)
        win_msg = message_font.render("YOU WIN!", True, WHITE)

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        win_msg_rect = win_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
        running = True
        while running:
            screen.fill(BLACK)
            screen.blit(title, title_rect)
            screen.blit(win_msg, win_msg_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
