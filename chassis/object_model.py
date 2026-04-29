# chassis/object_model.py

import numpy as np

class Object:
    def __init__(self, obj_id, position, mass=1.0):
        self.id = obj_id
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(3)

        self.mass = mass
        self.held = False

        self.friction = 0.6
        self.grip_required = self.mass * 9.81 * 0.5  # slip threshold

    def update(self, dt):
        if not self.held:
            self.position += self.velocity * dt
