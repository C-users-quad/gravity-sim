from settings import *
from chatlog import LogText
if TYPE_CHECKING:
    from particle import Particle
    from cam import Cam

def combined_masses(p1: "Particle", p2: "Particle") -> float:
    """
    Return the sum of the masses of two particles.
    Args:
        p1, p2: Particle objects with a mass attribute.
    Returns:
        float: Combined mass.
    """
    return p1.mass + p2.mass

def velocity_of_combined_particles(p1: "Particle", p2: "Particle") -> pygame.Vector2:
    """
    Calculate the velocity of two combined particles using conservation of momentum.
    Args:
        p1, p2: Particle objects with mass and velocity attributes.
    Returns:
        Vector2: Resulting velocity.
    """
    return ((p1.mass * p1.v) + (p2.mass * p2.v)) / (p1.mass + p2.mass)

def combined_density(p1: "Particle", p2: "Particle") -> float:
    """
    Calculates the density of two combined particles.
    Args:
        p1, p2 (Particle): Particles with mass and density attributes.
    Returns:
        float: Calculated density.
    """
    # Area = pi * r^2 for each particle
    area1 = math.pi * p1.radius**2
    area2 = math.pi * p2.radius**2
    total_mass = p1.mass + p2.mass
    total_area = area1 + area2
    # density = total_mass / total_area
    density = total_mass / total_area if total_area > 0 else 1.0
    # Clamp to simulation range
    min_density = 0.01
    max_density = 1000
    return max(min_density, min(density, max_density))

def draw_info(infos: list[str], font: pygame.Font, display: pygame.display, corner: Literal["topleft", "topright"]) -> None:
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
        
def truncate_decimal(decimal: float, decimal_places: int) -> float:
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

class QuadTree:
    """
    Quadtree that partitions the game and helps it render fast.
    Args:
            boundary (pygame.FRect or pygame.Rect): Bounding rectangle that represents the topleft and width+height of the Quadtree node.
            capacity (int): Number of particles that can fit in any one node. Can be bypassed if certain conditions are met.
            level (int): The level that the node rests at. The root node's level is 0.
            maxlevel (int): The maximum level a node can be.
    """
    def __init__(self, boundary: pygame.FRect | pygame.Rect, capacity: int, cam: object, level: int=0, maxlevel: int=7) -> None:
        # self.boundary = (left, top, length, width) of bounding rect.
        self.boundary = boundary
        self.capacity = capacity
        self.particles_in_node = []
        self.divided = False
        self.level = level
        self.maxlevel = maxlevel

        self.nw = self.ne = self.sw = self.se = None
        self.children = []

        # used for visualization scaled with camera manipulations
        self.cam = cam

        # CoM stuff, used for barnes hut approximations
        self.mass = 0.0
        self.x_com = 0.0
        self.y_com = 0.0
        self.theta = 0.75

    def clear(self) -> None:
        """
        Clears the Quadtree and resets every node.
        """
        self.particles_in_node = []
        if not self.divided:
            return
        for node in self.children:
            node.clear()
        self.children = []
        self.divided = False

    def insert(self, particle: "Particle") -> None:
        """
        Inserts a particle into the Quadtree.
        Args:
            particle (Particle): The particle you wish to insert.
        """
        if not self.boundary.collidepoint((particle.x, particle.y)):
            return

        if len(self.particles_in_node) < self.capacity:
            self.particles_in_node.append(particle)
        else:
            if self.level >= self.maxlevel:
                self.particles_in_node.append(particle)
                return
            
            if not self.divided:
                self.divide_node()
                self.place_particle(particle)
            elif self.divided:
                self.place_particle(particle)

    def divide_node(self) -> None:
        """
        Divides a Quadtree node into 4 smaller nodes.
        """
        w_div_2 = self.boundary.width / 2
        h_div_2 = self.boundary.height / 2
        left = self.boundary.left
        top = self.boundary.top
        new_level = self.level + 1

        self.nw = QuadTree(pygame.FRect(left, top, w_div_2, h_div_2), self.capacity, self.cam, new_level)
        self.ne = QuadTree(pygame.FRect(left + w_div_2, top, w_div_2, h_div_2), self.capacity, self.cam, new_level)
        self.sw = QuadTree(pygame.FRect(left, top + h_div_2, w_div_2, h_div_2), self.capacity, self.cam, new_level)
        self.se = QuadTree(pygame.FRect(left + w_div_2, top + h_div_2, w_div_2, h_div_2), self.capacity, self.cam, new_level)
        self.children = [self.nw, self.ne, self.sw, self.se]

        self.divided = True

        old_particles = self.particles_in_node
        self.particles_in_node = []
        for particle in old_particles:
            self.place_particle(particle)

    def place_particle(self, particle: "Particle"):
        """
        Recursively looks through the Quadtree to find the node the particle belongs in.
        Args:
            particle (Particle): the particle you wish to place into the Quadtree.
        """
        for node in self.children:
            if node.boundary.collidepoint((particle.x, particle.y)):
                node.insert(particle)
                return
        self.particles_in_node.append(particle)

    def calculate_CoM(self) -> tuple[float, tuple[float, float]]:
        """
        Calculates the center of mass for every node in the quadtree.
        Returns:
            tuple:
                - mass (float): The total mass of this node and of its children.
                - com (tuple[float, float]): The (x, y) coordinates of the center of mass.
        """
        if not self.divided:
            self.mass = sum(p.mass for p in self.particles_in_node)
            if self.mass:
                self.x_com = sum(p.mass * p.x for p in self.particles_in_node) / self.mass
                self.y_com = sum(p.mass * p.y for p in self.particles_in_node) / self.mass
            return self.mass, (self.x_com, self.y_com)
        
        self.mass = self.x_com = self.y_com = 0.0
        for node in self.children:
            mass, (cx, cy) = node.calculate_CoM()
            self.mass += mass
            self.x_com += mass * cx
            self.y_com += mass * cy
        if self.mass:
            self.x_com /= self.mass
            self.y_com /= self.mass

        return self.mass, (self.x_com, self.y_com)

    def query_bh(self, particle: "Particle", pseudo_particles=None) -> list[tuple[float, float, float]]:
        """
        Queries the quadtree for barnes-hut pseudo-particles to approximate forces.
        Args:
            particle (Particle) : The particle you want to find the forces of.
        Returns:
            list[tuple[float, float, float] :
                A list of pseudo-particles represented as tuples:
                - x (float): the x coordinate of the center of mass
                - y (float): the y coordinate of the center of mass
                - mass (float): total mass of the pseudo-particle
        """
        if not pseudo_particles:
            pseudo_particles = []

        s = max(self.boundary.width, self.boundary.height)
        dx = self.x_com - particle.x
        dy = self.y_com - particle.y
        d2 = dx*dx + dy*dy
        epsilon = 1e-5
        d2 = max(d2, epsilon) # avoid division by zero

        if s*s < self.theta*self.theta * d2:
            if self.mass:
                pseudo_particles.append((self.x_com, self.y_com, self.mass))
        else:
            if not self.divided:
                return pseudo_particles
            for node in self.children:
                node.query_bh(particle, pseudo_particles)

        return pseudo_particles

    def query_circle(self, particle: "Particle") -> list["Particle"]:
        """
        DEPRECATED... SPATIALGRID USED FOR COLLISIONS INSTEAD.
        Queries a circular area around the particle in order to find what particles (or so-called "neighbors") it may collide with.
        Args:
            particle (Particle): The particle you want to find the neighbors of.
        Returns:
            found_particles[Particle]: A list of all the neighbors your queried particle may collide with.
        """
        center = (particle.x, particle.y)
        radius = particle.radius + MAX_RADIUS * 2
        query_rect = pygame.FRect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
        found_particles = []

        if not self.boundary.colliderect(particle.rect):
            return found_particles
        
        for p in self.particles_in_node:
            dx = p.x - center[0]
            dy = p.y - center[1]
            distance2 = dx**2 + dy**2
            if distance2 <= radius**2:
                found_particles.append(p)

        if not self.divided:
            return found_particles
        
        for node in self.children:
            found_particles.extend(node.query_circle(particle))

        return found_particles

    def draw_line(self, p1: "Particle", p2: "Particle", zoom: float, offset: pygame.Vector2):
        pygame.draw.line(
            pygame.display.get_surface(), 
            "white", 
            (p1.x * zoom + offset.x, p1.y * zoom + offset.y), 
            (p2.x * zoom + offset.x, p2.y * zoom + offset.y), 
            5
        )

    def visualize(self, zoom: float, offset: pygame.Vector2) -> None:
        """
        Draws a highlight on the edges of a Quadtree node.
        Args:
            zoom (int or float): Your camera's zoom.
            offset (pygame.math.Vector2): Your camera's offset.
        """
        args = (
            pygame.display.get_surface(), # Surface to draw on
            "white", # Color of highlight
            pygame.FRect(self.boundary.left * zoom + offset.x, # Rect
             self.boundary.top * zoom + offset.y,
             self.boundary.width * zoom,
             self.boundary.height * zoom),
             3 # Highlight width
        )
        pygame.draw.rect(*args)
        if not self.divided:
            return
        for node in self.children:
            node.visualize(zoom, offset)


class SpatialGrid:
    """
    Spatial partitioning grid used for particle collisions.
    """
    def __init__(self) -> None:
        """
        Initialize the grid with a given cell size.
        """
        self.grid = {}
        self.cell_size = MAX_RADIUS

    def clear_grid(self) -> None:
        """
        Clear all cells in the grid.
        """
        self.grid = {}
    
    def draw_lines_to_neighbors(self, particle: "Particle", zoom: float, offset: pygame.Vector2) -> None:
        """
        Draws lines from one particle's center to its neighbors' centers.
        Args:
            p1 (Particle): Particle that you draw from to neighbors.
            zoom (float): Camera zoom.
            offset (pygame.math.Vector2): Camera offset.
        """
        neighbors = self.get_neighbors(particle)
        for n in neighbors:
            args = (
                pygame.display.get_surface(),
                "white",
                (particle.x * zoom + offset.x, particle.y * zoom + offset.y),
                (n.x * zoom + offset.x, n.y * zoom + offset.y),
                5
            )
            pygame.draw.line(*args)

    # adds a particle to a cell. if cell does not exist, it creates a cell.
    def add_particle(self, particle: "Particle") -> None:
        """
        Add a particle to the appropriate cell in the grid.
        Args:
            particle: Particle object with x and y attributes.
        """
        cell = self.get_cell(particle.x, particle.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(particle)

    def get_cell(self, x: float, y: float) -> tuple[int, int]:
        """
        Get the cell coordinates for a given position.
        Args:
            x (float): X position.
            y (float): Y position.
        Returns:
            tuple: (cell_x, cell_y)
        """
        return int(x // self.cell_size), int(y // self.cell_size)

    def get_neighbors(self, particle: "Particle") -> list["Particle"]:
        """
        Get neighboring particles from adjacent cells, and particles in the same cell as particle.
        Args:
            particle: Particle object with x and y attributes.
        Returns:
            list: Neighboring particles + particles in same cell as particle.
        """
        neighbors = []
        cx, cy = self.get_cell(particle.x, particle.y)
        directions = [
            (cx - 1, cy - 1), (cx, cy - 1), (cx + 1, cy- 1),
            (cx - 1, cy),     (cx, cy),        (cx + 1, cy),
            (cx - 1, cy + 1),(cx, cy + 1), (cx + 1, cy + 1)
        ]
        for direction in directions:
            if direction not in self.grid:
                continue
            neighbors.extend(self.grid[direction])

        return neighbors
    
def find_particle(particles: list["Particle"], mouse_pos: tuple[float, float]) -> "Particle | None":
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
        
def calculate_radius(mass: float, density: float) -> float:
    """
    Calculate the radius of a particle based on its mass and density.
    Args:
        mass (float): Particle mass.
        density (float): Particle density.
    Returns:
        float: Calculated radius.
    """
    epsilon = 1e-5
    density = max(epsilon, density)
    area = mass / density
    radius = math.sqrt(area / math.pi)
    return max(MIN_RADIUS, min(radius, MAX_RADIUS))

def split_string_every_n_chars(string: str, n: int) -> list[str]:
    """
    Split a string into chunks of n characters.
    Args:
        string (str): String to split.
        n (int): Number of characters per chunk.
    Returns:
        list: List of string chunks.
    """
    return [string[i:i+n] for i in range(0, len(string), n)]

class LogPrinter:
    """
    Print a string to the chat log, splitting it if necessary.
    Args:
        string (str): Message to print.
        font: Font object for rendering.
        groups: Sprite groups for the log text.
        logtext: Log text group.
        type (str): Type of message ('normal', 'error').
    """
    def __init__(self, font: pygame.Font, groups: list[pygame.sprite.Group], logtext: pygame.sprite.Group) -> None:
        self.font = font
        self.groups = groups
        self.logtext = logtext

    def add_prefix(self, string: str, type: Literal["normal", "error", "hint", "info"]) -> str:
        if type == "normal":
            return string
        elif type == "error":
            return "[ERROR]" + " " + string
        elif type == "hint":
            return "[HINT]" + " " + string
        elif type == "info":
            return "[INFO]" + " " + string

    def print(self, string: str, type: Literal["normal", "error", "hint", "info"] = "normal") -> None:
        string = self.add_prefix(string, type)
        strings = split_string_every_n_chars(string, MAX_LOG_TEXT_CHAR_WIDTH)
        for string in strings:
            LogText(string, self.font, self.groups, self.logtext, type)


class Accelerator:
    """Accelerates a value using physics equations for smooth incrementation."""
    def __init__(self) -> None:
        self.velocity = 0.0
        self.max_velocity = 0.0
        self.acceleration = 0.0
        self.accel_when_scrolled = 0.0 # The acceleration you get if theres a scroll event.
        self.old_event_y = 0

    def accelerate(self, value: float, event_y: Literal[-1, 1], dt: float, type: Literal["cam speed", "cam zoom"]) -> float:
        """
        Accelerates a value.
        Args:
            dt (float): Time between frames in seconds.
            value (float): Value you wish to accelerate.
            event_y (int): 1 if scrolled up, -1 if scrolled down.
            type (string): The type of value you are accelerating.
        Returns:
            float: The accelerated value.
        """
        if type == "cam speed":
            starting_velocity = 100 * (max(HALF_WORLD_HEIGHT, HALF_WORLD_WIDTH) / 5000)
            self.accel_when_scrolled = 100 * (max(HALF_WORLD_HEIGHT, HALF_WORLD_WIDTH) / 5000)
            self.max_velocity = 5000 * (max(HALF_WORLD_HEIGHT, HALF_WORLD_WIDTH) / 5000)
            min_return = MIN_CAM_SPEED * (max(HALF_WORLD_HEIGHT, HALF_WORLD_WIDTH) / 5000)
            max_return = MAX_CAM_SPEED * (max(HALF_WORLD_HEIGHT, HALF_WORLD_WIDTH) / 5000)
        elif type == "cam zoom":
            starting_velocity = 0.7
            self.accel_when_scrolled = 0.5
            self.max_velocity = 2
            min_return = MIN_ZOOM 
            max_return = MAX_ZOOM 

        if event_y != self.old_event_y:
            self.velocity = starting_velocity / dt * event_y

        if abs(self.velocity) < 1e-99:
            self.velocity = starting_velocity / dt * event_y
            
        self.acceleration = event_y * self.accel_when_scrolled 
        self.velocity += self.acceleration * dt
        self.velocity = max(-self.max_velocity, min(self.velocity, self.max_velocity)) # clamps velocity
        self.old_event_y = event_y

        return max(min_return, min(value + self.velocity * dt, max_return))
    
_cached_color_bins = None

def calculate_color_bins(particles: pygame.sprite.Group, frame_count: int) -> np.ndarray:
    global _cached_color_bins

    skip_frames = 10 # [int] frames are skipped for calculations
    if frame_count % skip_frames != 0:
        if _cached_color_bins is not None:
            return _cached_color_bins
        
    if len(particles) < 1:
        return
    
    masses = np.array([p.mass for p in particles])
    percentiles = np.percentile(masses, np.linspace(0, 100, 11))  # 10 intervals
    _cached_color_bins = percentiles

    return percentiles

starting_split_index = 0
split_size = MAX_PARTICLE_UPDATES

def split_particles_not_in_render(particles: Sequence["Particle"], n_particles_rendered: int) -> Sequence["Particle"]:
    """DEPRECATED..."""
    global starting_split_index
    global split_size
    split_size = MAX_PARTICLE_UPDATES - n_particles_rendered
    if starting_split_index >= MAX_PARTICLE_UPDATES:
            starting_split_index = 0
    particles = particles[starting_split_index:starting_split_index + split_size]
    starting_split_index += split_size

    return particles
    
def update_particles(particles: Sequence["Particle"], dt: float, cam: "Cam", percentiles: np.ndarray, grid: SpatialGrid, quadtree: QuadTree) -> None:
    for particle in particles:
        particle.update(dt, cam, percentiles, grid, quadtree)

