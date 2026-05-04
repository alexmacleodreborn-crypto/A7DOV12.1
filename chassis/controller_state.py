# chassis/controller_state.py

class MotorState:
    def __init__(self):
        self.target_position = None
        self.end_effector = None  # e.g. "right_arm"
        self.error_vector = None
        self.active = False
