from .cell import Cell
from .morphogen import MorphogenField

class Organism:
    def __init__(self):
        self.cells = [Cell([0, 0, 0])]
        self.field = MorphogenField()
        self.time = 0

    def update(self, dt):
        self.time += dt
        new_cells = []

        for cell in self.cells:
            force = self.field.get_force(cell.position)
            cell.update(dt, force)

            # differentiation
            if cell.position[1] > 5:
                cell.type = "neural"
            elif cell.position[1] < -2:
                cell.type = "endoderm"
            else:
                cell.type = "mesoderm"

            if cell.should_divide() and len(self.cells) < 2000:
                new_cells.append(cell.divide())

        self.cells.extend(new_cells)
