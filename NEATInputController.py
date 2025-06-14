from InputController import InputController

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
        inputs = self.obs_fn()
        direction, jump_direction, jump_trigger, jump_strength = self.net.activate(inputs)
        return {
            "left": direction > 0.2,
            "right": direction <= 0.2,
            "jump_left": jump_direction > 0.2,
            "jump_right": jump_direction < -0.2,
            "jump_trigger": jump_trigger > 0.5,
            "jump_strength":  (jump_strength + 1) / 2
        }

    def get_empty_input(self):
        return {
            "left": False,
            "right": False,
            "jump_trigger": False,
            "jump_strength": 0
        }