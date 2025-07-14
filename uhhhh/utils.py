import math

def combined_masses(p1, p2):
    return p1.mass + p2.mass

def velocity_of_combined_particles(p1, p2):
    return ((p1.mass * p1.v) + (p2.mass * p2.v)) / (p1.mass + p2.mass)

class SpatialGrid:
    def __init__(self, cell_size):
        self.grid = {}
        self.cell_size = cell_size

    def clear_grid(self):
        self.grid = {}
    
    # adds a particle to a cell. if cell does not exist, it creates a cell.
    def add_particle(self, particle):
        cell = self.get_cell(particle.x, particle.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(particle)

    # returns position of cell in self.grid dictionary (cell_x, cell_y)
    def get_cell(self, x, y):
        return int(x // self.cell_size), int(y // self.cell_size)

    def get_neighbors(self, particle):
        neighbors = []
        cx, cy = self.get_cell(particle.x, particle.y)
        directions = [
            (cx - 1, cy - 1), (cx, cy - 1), (cx + 1, cy- 1),
            (cx - 1, cy),                      (cx + 1, cy), 
            (cx - 1, cy + 1),(cx, cy + 1), (cx + 1, cy + 1)
        ]
        for direction in directions:
            if direction not in self.grid:
                continue
            neighbors.extend(self.grid[direction])
        return neighbors
    