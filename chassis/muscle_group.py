# chassis/muscle_group.py

class MuscleGroup:
    def __init__(self, name, muscles):
        self.name = name
        self.muscles = muscles

    def activate(self, level):
        for m in self.muscles:
            if m.active:
                m.activation = level

    def total_force(self, atp):
        return sum(m.compute_force(atp) for m in self.muscles)
