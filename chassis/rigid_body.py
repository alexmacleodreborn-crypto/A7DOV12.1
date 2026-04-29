# chassis/rigid_body.py

import numpy as np

class RigidBody:
    def __init__(self, bone):
        self.bone = bone

        self.position = bone.center()
        self.velocity = np.zeros(3)
        self.acceleration = np.zeros(3)

        self.mass = bone.mass

    def apply_force(self, force):
        self.acceleration += force / (self.mass + 1e-6)

    def integrate(self, dt):
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        self.acceleration[:] = 0
