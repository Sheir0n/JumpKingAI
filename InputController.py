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

# TODO: NEAT inputs
class NEATInputController(InputController):
    def __init__(self, neat_network, get_observation, thr=0.5, hold_frames=3):
        """
        neat_network  –  obiekt sieci (neat.nn.FeedForwardNetwork)
        get_observation() -> tuple/list – funkcja zwracająca wejścia dla sieci
        thr            –  próg aktywacji (0-1) zamieniający wyjście sieci na bool
        hold_frames    –  ile klatek ma trwać 'przytrzymanie' skoku,
                          gdy wyjście jump > thr
        """
        self.net = neat_network
        self.obs_fn = get_observation
        self.thr = thr
        self.hold_frames = hold_frames
        self._jump_buffer = 0   # licznik „przytrzymania”

    def get_input(self):
        inputs = self.obs_fn()                 # pobieramy aktualny stan gry
        left_out, right_out, jump_out = self.net.activate(inputs)

        # --- skok z buforem przytrzymania ---------------------------------
        
        #print(f"inputs={inputs}")
        #print(f"outputs: left={left_out:.2f}, right={right_out:.2f}, jump={jump_out:.2f}, buffer={self._jump_buffer}")
        if jump_out > self.thr:
            self._jump_buffer = self.hold_frames
        else:
            self._jump_buffer = max(0, self._jump_buffer - 1)
    
        return {
            "left":  left_out  > self.thr,
            "right": right_out > self.thr,
            "jump":  self._jump_buffer > 0
        }

