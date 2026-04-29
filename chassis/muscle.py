# chassis/muscle.py

import numpy as np

class Muscle:
    def __init__(
        self,
        muscle_id,
        name,
        origin_bone,
        insertion_bone,
        max_force,
        development
    ):
        self.id = muscle_id
        self.name = name

        self.origin_bone = origin_bone
        self.insertion_bone = insertion_bone

        self.max_force = max_force

        # development profile
        self.dev = development

        # state
        self.activation = 0.0
        self.fatigue = 0.0
        self.exists = False
        self.active = False

    def compute_length(self):
        o = self.origin_bone.center()
        i = self.insertion_bone.center()
        return np.linalg.norm(i - o)

    def compute_force(self, atp):
        if not self.active:
            return 0.0

        length = self.compute_length()

        # simplified Hill-type
        volume = self.max_force
        fatigue_factor = 1.0 - self.fatigue

        force = (volume * fatigue_factor * self.activation) / (length + 1e-5)

        # energy constraint
        force *= atp

        return force

    def update(self, t, atp):
        # development gating
        if t < self.dev["t_start"]:
            self.exists = False
            return

        self.exists = True
        self.active = t >= self.dev["t_activation"]

        # fatigue recovery
        self.fatigue *= 0.95

        # clamp
        self.activation = max(0.0, min(1.0, self.activation))
