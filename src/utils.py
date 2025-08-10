from settings import *
from chatlog import LogText

def combined_masses(p1, p2):
    """
    Return the sum of the masses of two particles.
    Args:
        p1, p2: Particle objects with a mass attribute.
    Returns:
        float: Combined mass.
    """
    return p1.mass + p2.mass

def velocity_of_combined_particles(p1, p2):
    """
    Calculate the velocity of two combined particles using conservation of momentum.
    Args:
        p1, p2: Particle objects with mass and velocity attributes.
    Returns:
        Vector2: Resulting velocity.
    """
    return ((p1.mass * p1.v) + (p2.mass * p2.v)) / (p1.mass + p2.mass)

def draw_info(infos, font, display, corner):
    """
    Draw a list of info strings on the display surface at the specified corner.
    Args:
        infos (list): List of strings to display.
        font: Font object for rendering text.
        display: Surface to draw on.
        corner (str): 'topleft' or 'topright'.
    """
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
    """
    Truncate a decimal number to a fixed number of decimal places.
    Args:
        decimal (float): Number to truncate.
        decimal_places (int): Number of places to keep.
    Returns:
        float: Truncated value.
    """
    factor = 10 ** decimal_places
    truncated_value = int(decimal * factor) / factor
    return truncated_value

class SpatialGrid:
    """
    Spatial partitioning grid for efficient neighbor lookup in particle simulations.
    """
    def __init__(self, cell_size):
        """
        Initialize the grid with a given cell size.
        Args:
            cell_size (int): Size of each grid cell.
        """
        self.grid = {}
        self.cell_size = cell_size

    def clear_grid(self):
        """
        Clear all cells in the grid.
        """
        self.grid = {}
    
    # adds a particle to a cell. if cell does not exist, it creates a cell.
    def add_particle(self, particle):
        """
        Add a particle to the appropriate cell in the grid.
        Args:
            particle: Particle object with x and y attributes.
        """
        cell = self.get_cell(particle.x, particle.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(particle)

    # returns position of cell in self.grid dictionary (cell_x, cell_y)
    def get_cell(self, x, y):
        """
        Get the cell coordinates for a given position.
        Args:
            x (float): X position.
            y (float): Y position.
        Returns:
            tuple: (cell_x, cell_y)
        """
        return int(x // self.cell_size), int(y // self.cell_size)

    def get_neighbors(self, particle):
        """
        Get neighboring particles from adjacent cells.
        Args:
            particle: Particle object with x and y attributes.
        Returns:
            list: Neighboring particles.
        """
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
    """
    Find the first particle at the given mouse position.
    Args:
        particles (iterable): Collection of particles.
        mouse_pos (tuple): Mouse position.
    Returns:
        Particle or None: The found particle or None.
    """
    for particle in particles:
        if particle.rect.collidepoint(mouse_pos):    
            return particle
        
def calculate_radius(mass, density):
    """
    Calculate the radius of a particle based on its mass and density.
    Args:
        mass (float): Particle mass.
        density (float): Particle density.
    Returns:
        int: Calculated radius.
    """
    return max(MIN_RADIUS, int((mass**(1/3)) / density)) if max(MIN_RADIUS, int((mass**(1/3)) / density)) <= MAX_RADIUS else MAX_RADIUS

def split_string_every_n_chars(string, n):
    """
    Split a string into chunks of n characters.
    Args:
        string (str): String to split.
        n (int): Number of characters per chunk.
    Returns:
        list: List of string chunks.
    """
    return [string[i:i+n] for i in range(0, len(string), n)]

def print_to_log(string, font, groups, logtext, type="normal"):
    """
    Print a string to the chat log, splitting it if necessary.
    Args:
        string (str): Message to print.
        font: Font object for rendering.
        groups: Sprite groups for the log text.
        logtext: Log text group.
        type (str): Type of message ('normal', 'error').
    """
    strings = split_string_every_n_chars(string, MAX_LOG_TEXT_CHAR_WIDTH)
    for string in strings:
        LogText(string, font, groups, logtext, type)
