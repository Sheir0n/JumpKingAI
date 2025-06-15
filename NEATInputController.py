from InputController import InputController

class NEATInputController(InputController):
    def __init__(self, neat_network, get_observation, thr=0.5, hold_frames=3):
        super().__init__()
        self.net = neat_network
        self.obs_fn = get_observation
        self.thr = thr
        self.hold_frames = hold_frames
        self._jump_buffer = 0   # licznik „przytrzymania”

    def get_input(self):
        inputs = self.obs_fn()
        direction, jump_direction, jump_trigger, jump_strength = self.net.activate(inputs)

        raw_strength = (jump_strength + 1) / 2
        if raw_strength < 0.2:
            final_strength = 0.2
        elif raw_strength < 0.4:
            final_strength = 0.4
        elif raw_strength < 0.6:
            final_strength = 0.6
        elif raw_strength < 0.8:
            final_strength = 0.8
        else:
            final_strength = 1.0

        return {
            "left": direction > 0.2,
            "right": direction <= 0.2,
            "jump_left": jump_direction > 0.1,
            "jump_right": jump_direction < -0.1,
            "jump_trigger": jump_trigger > 0.5,
            "jump_strength":  final_strength
        }

    def get_empty_input(self):
        return {
            "left": False,
            "right": False,
            "jump_trigger": False,
            "jump_strength": 0
        }