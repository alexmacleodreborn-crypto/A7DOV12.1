import numpy as np

class MorphogenField:
    def get_force(self, position):
        x, y, z = position

        spine_force = np.array([0, 1.0, 0])
        center_force = -position * 0.05
        symmetry_force = np.array([-x * 0.1, 0, 0])

        return spine_force + center_force + symmetry_force
