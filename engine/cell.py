import numpy as np
import random

class Cell:
    def __init__(self, position):
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(3)

        self.type = "undifferentiated"
        self.age = 0
        self.division_timer = random.uniform(0.5, 1.5)

    def update(self, dt, field_force):
        self.age += dt
        self.velocity += field_force * dt
        self.position += self.velocity * dt
        self.velocity *= 0.9

    def should_divide(self):
        return self.age > self.division_timer

    def divide(self):
        offset = np.random.normal(0, 0.5, 3)
        new_cell = Cell(self.position + offset)
        self.age = 0
        return new_cell
