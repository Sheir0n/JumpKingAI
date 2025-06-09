import pygame

class Platform:
    def __init__(self, x_pos, y_pos, width, height, reward_level, id):
        self.hitbox = pygame.Rect(x_pos, y_pos, width, height)
        self.reward_level = reward_level
        self.id = id

        self.base_pos = (x_pos,y_pos)

    def reset_pos(self):
        self.hitbox.x = self.base_pos[0]
        self.hitbox.y = self.base_pos[1]