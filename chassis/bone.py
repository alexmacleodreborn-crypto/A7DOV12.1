# chassis/bone.py

import numpy as np

class Bone:
    def __init__(self, bone_id, name, parent_id, start, end, mass=1.0):
        self.id = bone_id
        self.name = name
        self.parent_id = parent_id

        self.start = np.array(start, dtype=float)
        self.end = np.array(end, dtype=float)

        self.mass = mass

    def length(self):
        return np.linalg.norm(self.end - self.start)

    def direction(self):
        vec = self.end - self.start
        norm = np.linalg.norm(vec)
        return vec / norm if norm != 0 else vec

    def scale(self, factor):
        self.start *= factor
        self.end *= factor
        self.mass *= factor ** 3  # cube law (critical) :contentReference[oaicite:3]{index=3}

    def center(self):
        return (self.start + self.end) / 2
