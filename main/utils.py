from settings import *

def combined_masses(p1, p2):
    return p1.mass + p2.mass

def velocity_of_combined_particles(p1, p2):
    return ((p1.mass * p1.v) + (p2.mass * p2.v)) / (p1.mass + p2.mass)

def draw_info(infos, font, display, corner):
    display_rect = display.get_bounding_rect()

    y_offset = 10
    padding = 4
    spacing = 4
    
    if corner == "topleft": x = 10
    if corner == "topright": x = display_rect.right - 10

    for info in infos:
        text_surf = font.render(info, True, "white")
        text_rect = text_surf.get_frect()

        rect_width = text_rect.width + padding * 2
        rect_height = text_rect.height + padding * 2
        rect_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        rect_surf.fill(INFO_RECT_COLOR)

        if corner == "topleft":
            rect_pos = (x, y_offset)
            text_rect.topleft = (rect_pos[0] + padding, rect_pos[1] + padding)
        elif corner == "topright":
            rect_pos = (x - rect_width, y_offset)
            text_rect.topleft = (rect_pos[0] + padding, rect_pos[1] + padding)

        display.blit(rect_surf, rect_pos)
        display.blit(text_surf, text_rect)
        y_offset += rect_height + spacing
        
def truncate_decimal(decimal, decimal_places):
    factor = 10 ** decimal_places
    truncated_value = int(decimal * factor) / factor
    return truncated_value

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
    
def find_particle(particles, mouse_pos):
    for particle in particles:
        if particle.rect.collidepoint(mouse_pos):    
            return particle
        
def calculate_radius(mass, density):
    return max(MIN_RADIUS, int((mass**(1/3)) / density)) if max(MIN_RADIUS, int((mass**(1/3)) / density)) <= MAX_RADIUS else MAX_RADIUS
