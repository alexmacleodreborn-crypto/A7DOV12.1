# chassis/bone.py

import numpy as np

class Bone:
    def __init__(
        self,
        bone_id,
        name,
        parent_id,
        start,
        end,
        development
    ):
        self.id = bone_id
        self.name = name
        self.parent_id = parent_id

        # base geometry (never mutated)
        self.base_start = np.array(start, dtype=float)
        self.base_end = np.array(end, dtype=float)

        # runtime geometry
        self.start = self.base_start.copy()
        self.end = self.base_end.copy()

        # development profile
        self.dev = development

        # physics
        self.mass = 0.0

        # rotation state
        self.rotation = np.zeros(3)  # rx, ry, rz
        self.angular_velocity = np.zeros(3)

        # activation state
        self.exists = False
        self.controllable = False
        self.load_bearing = False


    def direction(self):
        vec = self.end - self.start
        norm = np.linalg.norm(vec)
        if norm == 0:
            return np.zeros(3)
        return vec / norm

    def length(self):
        return np.linalg.norm(self.end - self.start)

    def center(self):
        return (self.start + self.end) / 2

    def update(self, t, global_scale):
        """
        Update bone based on biological time
        """

        # --- DEVELOPMENT GATING ---
        if t < self.dev["t_start"]:
            self.exists = False
            return

        self.exists = True

        # --- LOCAL GROWTH ---
        growth = self.dev["growth_curve"](t)

        scale = global_scale * growth

        # non-uniform scaling (height emphasis)
        scale_vec = np.array([scale * 0.7, scale * 1.2, scale * 0.7])

        self.start = self.base_start * scale_vec
        self.end = self.base_end * scale_vec

        # --- MASS (cube law) ---
        self.mass = np.linalg.norm(scale_vec) ** 3

        # --- ACTIVATION STATES ---
        self.controllable = t >= self.dev["t_control"]
        self.load_bearing = t >= self.dev["t_load"]
