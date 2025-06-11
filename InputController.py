from abc import ABC, abstractmethod
import pygame
import neat

# base input controller class
class InputController(ABC):
    def __init__(self):
        # default bindings - empty inputs
        self.bindings = {
            "jump": [],
            "left": [],
            "right": [],
        }

    @abstractmethod
    def get_input(self):
        pass

# player inout controller, returns table of inputs
class PlayerInputController(InputController):
    def __init__(self):
        super().__init__()
        # adding player input directions
        self.bindings["jump"] = [pygame.K_SPACE, pygame.K_UP, pygame.K_w]
        self.bindings["left"] = [pygame.K_a, pygame.K_LEFT]
        self.bindings["right"] = [pygame.K_d, pygame.K_RIGHT]

    # checking each input and returning them as dictionary
    def get_input(self):
        keys = pygame.key.get_pressed()
        state = {}
        for action, key_list in self.bindings.items():
            state[action] = any(keys[key] for key in key_list)
        return state

