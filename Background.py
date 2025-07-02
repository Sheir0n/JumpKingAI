import pygame


class Background:
    def __init__(self, bg_source, screen_width, screen_height, max_screens):
        self.image = pygame.image.load(bg_source).convert()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.max_screens = max_screens
        self.curr_screen = 0

        self.bg_w, self.bg_h = self.image.get_size()
        self.background_y_offset = self.bg_h - self.screen_height
        self.background_x_offset = 0
        self.rect = pygame.Rect(self.background_x_offset, self.background_y_offset, self.screen_width, self.screen_height)

    def update_offset(self, curr_screen):
        self.curr_screen = curr_screen
        factor = self.curr_screen / self.max_screens
        self.background_y_offset = (1 - factor) * (self.bg_h - self.screen_height)

        self.rect = pygame.Rect(
            self.background_x_offset,
            int(self.background_y_offset),
            self.screen_width,
            self.screen_height
        )