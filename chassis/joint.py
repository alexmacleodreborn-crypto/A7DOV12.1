# chassis/joint.py

import numpy as np

class Joint:
    def __init__(self, parent_id, child_id, limits):
        self.parent_id = parent_id
        self.child_id = child_id
        self.limits = limits

    def apply_limits(self, rotation):
        clamped = np.zeros(3)

        for i, axis in enumerate(["x", "y", "z"]):
            low, high = self.limits[axis]
            clamped[i] = max(low, min(high, rotation[i]))

        return clamped
