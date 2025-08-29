from settings import *
from utils import *
if TYPE_CHECKING:
    from cam import Cam

_cached_particle_surfs: dict[tuple, pygame.Surface] = {} # key = (radius, color), value = pygame.Surface()

def surf_lookup(radius: int, color: tuple) -> list[pygame.Surface]:
    """
    Looks up and caches surfaces for particles.
    Args:
        radius (float): the radius of your particle.
        color (ColorLike): the color of your particle
    Returns:
        particle_surf (pygame.Surface): the surface for the particle requested
    """
    key = (radius, color)
    if key not in _cached_particle_surfs:
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (radius, radius), radius)
        _cached_particle_surfs[key] = surf
    return _cached_particle_surfs[key]


class Particle(pygame.sprite.Sprite):
    """
    Represents a particle in the gravity simulation. Handles physics, rendering, and interactions.
    """
    def __init__(self, x: float, y: float, vx: float, vy: float, mass: float, 
                 density: float, groups: list[pygame.sprite.Group], particles: pygame.sprite.Group) -> None:
        """
        Initialize a particle with position, velocity, mass, density, and groups.
        Args:
            x, y (float): Initial position.
            vx, vy (float): Initial velocity components.
            mass (float): Particle mass.
            density (float): Particle density.
            groups: Sprite groups for rendering.
            particles: Group of all particles for interactions.
        """
        self.x = x
        self.y = y
        self.v = pygame.Vector2(vx, vy)
        self.a = pygame.Vector2(0, 0) # acceleration
        self.mass = mass # mass in kilograms (kg)
        self.density = density
        self.radius = calculate_radius(self.mass, self.density)
        self.particles = particles # all other particles
        self.min_highlight_width = 5

        self.much = 1000 # if the particle's mass does not change by this value in a frame, then dont update the color.
        self.color = "red"

        self.being_dragged = False
        self.in_menu = False
        self.info = False

        self.old_pos = self.new_pos = (self.x, self.y)

        self.groups = groups
        super().__init__(groups)
        self.update_sprite()
    
    def draw_neighbor_lines(self, surface, cam, grid: SpatialGrid):
        """
        Draw lines from this particle to all its neighbors found by the spatial grid.
        Args:
            surface (pygame.Surface): The pygame surface to draw on.
            cam: Camera object for zoom and position.
            grid: the grid for neighbor search
        """
        if grid is None:
            return
        neighbors = grid.get_neighbors(self)
        win_w, win_h = surface.get_size()
        offset_x = -cam.pos.x * cam.zoom + win_w / 2
        offset_y = -cam.pos.y * cam.zoom + win_h / 2
        for neighbor in neighbors:
            if neighbor is self or not neighbor.alive():
                continue
            x1 = self.x * cam.zoom + offset_x
            y1 = self.y * cam.zoom + offset_y
            x2 = neighbor.x * cam.zoom + offset_x
            y2 = neighbor.y * cam.zoom + offset_y
            pygame.draw.line(surface, (0,255,0), (x1, y1), (x2, y2), 2)
    
    def update_sprite(self):
        """
        Update the particle's image and rect based on its radius and color.
        """
        self.radius = calculate_radius(self.mass, self.density)
        image = surf_lookup(int(self.radius), self.color)
        self.image = image.copy()
        self.rect = self.image.get_frect(center = (self.x, self.y))

    def draw_highlight(self, cam):
        """
        Draw a highlight border around the particle when selected or dragged.
        Args:
            cam: Camera object for zoom.
        """
        radius = calculate_radius(self.mass, self.density)
        highlight_width = max(self.min_highlight_width / cam.zoom, radius*0.05)
        pygame.draw.circle(self.image, HIGHLIGHT_COLOR, (self.radius, self.radius), self.radius, int(highlight_width))

    def check_collision_and_merge(self, other: "Particle", dt: float) -> None:
        """deprecated..."""
        if not (self.alive() and other.alive()):
            return

        # relative position and velocity
        dx = self.x - other.x
        dy = self.y - other.y
        dvx = self.v.x - other.v.x
        dvy = self.v.y - other.v.y

        R = self.radius + other.radius

        # Quadratic coefficients
        a = dvx * dvx + dvy * dvy
        b = 2 * (dx * dvx + dy * dvy)
        c = dx * dx + dy * dy - R * R

        if a == 0.0:
            # no relative velocity → just check overlap
            if c <= 0:
                self.combine_with(other)
            return

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return  # no collision

        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)

        # choose the earliest valid collision time
        t_hit = None
        if 0 <= t1 <= dt:
            t_hit = t1
        elif 0 <= t2 <= dt:
            t_hit = t2

        if t_hit is not None:
            # move both particles to collision point
            self.x += self.v.x * t_hit
            self.y += self.v.y * t_hit
            other.x += other.v.x * t_hit
            other.y += other.v.y * t_hit

            # merge at the exact impact location
            self.combine_with(other)

    def apply_forces(self, pseudo_particles: np.ndarray, dt: float) -> None:
        """
        Apply gravitational forces from neighboring particles.
        Args:
            pseudo_particles (np.ndarray): vectorized array of pseudo particles represented as (x, y, mass) tuples
            dt (float): Delta time since last frame.
        """
        epsilon = 1e-5
        if len(pseudo_particles) == 0:
            return
        ppx, ppy, ppm = pseudo_particles[:, 0], pseudo_particles[:, 1], pseudo_particles[:, 2]
        dx = ppx - self.x
        dy = ppy - self.y
        d2 = dx*dx + dy*dy + epsilon

        self.a.x = np.sum(G * ppm * dx / (d2**1.5))
        self.a.y = np.sum(G * ppm * dy / (d2**1.5))

    def combine_with(self, other):
        """
        Combine this particle with another, updating mass, velocity, and position.
        Only the more massive particle (or lower id as tiebreaker) performs the merge to avoid double merging.
        Args:
            other: Another Particle object.
        """
        if not (self.alive() and other.alive()):
            return
        # Only allow the more massive (or lower id as tiebreaker) particle to perform the merge
        if self.mass < other.mass or (self.mass == other.mass and id(self) > id(other)):
            return
        new_v = velocity_of_combined_particles(self, other)
        new_mass = combined_masses(self, other)
        new_pos = self.x, self.y
        new_density = combined_density(self, other)

        if self.mass > other.mass:
            self.x, self.y = new_pos
            self.v = new_v
            self.mass = new_mass
            self.density = new_density
            self.radius = calculate_radius(self.mass, self.density)
            self.update_sprite()
            other.kill()
        else:
            other.x, other.y = new_pos
            other.v = new_v
            other.mass = new_mass
            other.radius = calculate_radius(other.mass, other.density)
            other.update_sprite()
            self.kill()
    
    def window_collisions(self, direction):
        """
        Handle collisions with the simulation window boundaries.
        Args:
            direction (str): 'horizontal' or 'vertical'.
        """
        if direction == "vertical":
            if self.rect.top < -HALF_WORLD_HEIGHT:
                self.rect.top = -HALF_WORLD_HEIGHT
                self.v.y *= -1
                self.y = self.rect.centery
            if self.rect.bottom > HALF_WORLD_HEIGHT:
                self.rect.bottom = HALF_WORLD_HEIGHT
                self.v.y *= -1
                self.y = self.rect.centery
        if direction == "horizontal":
            if self.rect.left < -HALF_WORLD_WIDTH:
                self.rect.left = -HALF_WORLD_WIDTH
                self.v.x *= -1
                self.x = self.rect.centerx
            if self.rect.right > HALF_WORLD_WIDTH:
                self.rect.right = HALF_WORLD_WIDTH
                self.v.x *= -1
                self.x = self.rect.centerx
    
    def update_position(self, dt: float, quadtree: QuadTree, grid: SpatialGrid, counter) -> None:
        """
        Update the particle's position based on velocity and handle window collisions.
        Args:
            dt (float): Delta time since last frame.
            quadtree: The game's quadtree.
        """
        self.x += self.v.x * dt + 0.5 * self.a.x * dt*dt
        self.window_collisions("horizontal")
        
        self.y += self.v.y * dt + 0.5 * self.a.y * dt*dt
        self.window_collisions("vertical")

        old_a = self.a
        self.a = pygame.Vector2(0, 0)

        
        pseudo_particles = quadtree.query_bh(self)
        self.apply_forces(pseudo_particles, dt)
        for other in grid.get_neighbors(self):
            if other is self or not other.alive() or other.being_dragged:
                continue
            dx = other.x - self.x
            dy = other.y - self.y
            d2 = dx**2 + dy**2
            R2 = (other.radius + self.radius)**2
            if R2 >= d2: # r2d2 yoooo
                self.combine_with(other)
        
        self.v += 0.5 * (old_a + self.a) * dt
        
        self.rect.center = (self.x, self.y)

    def update_color(self, percentiles):
        """
        Update the particle's color based on its mass percentile among all particles.
        Args:
            percentiles (np.ndarray): the color bins.
        """
        if hasattr(self, "old_mass"):
            if self.mass == self.old_mass:
                return
            elif abs(self.mass - self.old_mass) < self.much:
                return

        colors = [
            (5, 209, 255), (53, 197, 255), (107, 183, 255),
            (146, 167, 255), (190, 139, 255), (234, 102, 243),
            (255, 55, 197), (255, 46, 143), (255, 11, 88), (255, 0, 0)
        ]

        # Find which percentile bin this particle's mass falls into
        for i in range(len(percentiles) - 1):
            if percentiles[i] <= self.mass < percentiles[i + 1]:
                self.color = colors[i]
                break
        else:
            self.color = colors[-1]
        self.old_mass = self.mass
    
    def one_info_particle(self):
        """
        Ensure only one particle is marked for info display at a time.
        """
        for particle in self.particles:
            if particle.info and particle != self:
                self.info = False
                return

    def update_physics(self, dt, quadtree, grid, counter):
        self.old_pos = (self.x, self.y)
        self.update_position(dt, quadtree, grid, counter)
        self.new_pos = (self.x, self.y)
    
    def update_drawing(self, percentiles, cam):
        self.update_sprite()
        self.update_color(percentiles)
        if self.info:
            self.one_info_particle()
            self.draw_highlight(cam)
        if self.being_dragged:
            self.draw_highlight(cam)
    
    def update(self, dt, cam, percentiles, grid, quadtree, counter):
        """
        Update the particle each frame: apply forces, update position, color, and highlight.
        Args:
            dt (float): Delta time since last frame.
            cam: Camera object.
            percentiles: color bins for coloring particles based on mass
            grid: the spatial grid for particle collisions
            quadtree: Quadtree for neighbor lookup.
        """
        if not self.in_menu:
            self.update_physics(dt, quadtree, grid, counter)
            self.update_drawing(percentiles, cam)
