from settings import *
from utils import *
if TYPE_CHECKING:
    from cam import Cam

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
        self.info = False
        self.moves = True

        self.old_pos = self.new_pos = (self.x, self.y)

        self.groups = groups
        super().__init__(groups)
        self.update_sprite()
    
    def update_sprite(self):
        """
        Update the particle's image and rect based on its radius.
        """
        self.radius = calculate_radius(self.mass, self.density)
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, "white", (self.radius, self.radius), self.radius)
        self.rect = self.image.get_frect(center = (self.x, self.y))

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

    def draw_highlight(self, cam):
        """
        Draw a highlight border around the particle when selected or dragged.
        Args:
            cam: Camera object for zoom.
        """
        radius = calculate_radius(self.mass, self.density)
        highlight_width = max(self.min_highlight_width / cam.zoom, radius*0.05)
        pygame.draw.circle(self.image, HIGHLIGHT_COLOR, (self.radius, self.radius), self.radius, int(highlight_width))

    def apply_forces(self, pseudo_particles: np.ndarray, dt: float) -> None:
        """
        Apply gravitational forces from neighboring particles.
        Args:
            pseudo_particles (np.ndarray): vectorized array of pseudo particles represented as (x, y, mass) tuples
            dt (float): Delta time since last frame.
        """
        epsilon = 1
        if len(pseudo_particles) == 0:
            return
        ppx, ppy, ppm = pseudo_particles[:, 0], pseudo_particles[:, 1], pseudo_particles[:, 2]
        dx = ppx - self.x
        dy = ppy - self.y
        d2 = dx*dx + dy*dy + epsilon

        self.a.x = np.sum(G * ppm * dx / (d2**1.5))
        self.a.y = np.sum(G * ppm * dy / (d2**1.5))
    
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
    
    def ccd_resolve(self, other, dt: float) -> None:
        """
        Continuous collision detection between 2 particles
        Args:
            particles (np.ndarray): shape (N,M) numpy array representing all particles (N) and their attributes (M attributes per particle)
            candidates (np.ndarray): shape (K,2) numpy array representing all possible collision pairs (K pairs per particle)
            dt (float): delta time over one frame
        """
        px = other.x - self.x
        py = other.y - self.y
        vx = other.v.x - self.v.x
        vy = other.v.y - self.v.y
        R  = other.radius + self.radius
        R2 = R*R
        
        # p_dot_p is effectively distance squared. if its less than R2, then theres a collision at t=0.
        p_dot_p = px*px + py*py
        if p_dot_p < R2:
            self.resolve(other, 0)
            return
        
        # if theres no collision already and velocities are zero, then there wont be a collision.
        v_dot_v = vx*vx + vy*vy
        if v_dot_v == 0:
            return
        
        # quadratic check
        a = v_dot_v
        b = 2*(px*vx + py*vy)
        c = p_dot_p - R2
        
        # if the discriminant is negative, there arent any real solutions.
        discriminant = b*b - 4*a*c
        if discriminant < 0:
            return

        sqrt_disc = discriminant**0.5
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        t = dt + 1.0 # sentinel time
        if 0 <= t1 <= dt:
            t = t1
        if 0 <= t2 <= dt and t2 < t:
            t = t2

        if t != dt + 1.0:
            self.resolve(other, t)

    def resolve(self, other, t: float) -> None:
        """
        Resolve 2D collision between particles i and j at time t.
        Args:
            t (float): the time of collision between particles p1 and p2.
        """
        # move to collision
        self.x += self.v.x * t
        self.y += self.v.y * t
        other.x += other.v.x * t
        other.y += other.v.y * t

        # relative position & velocity
        dx = other.x - self.x
        dy = other.y - self.y

        dist2 = dx*dx + dy*dy
        if dist2 == 0.0:
            return

        # normalize displacement
        dist = (dx**2 + dy**2)**0.5
        overlap = (self.radius + other.radius) - dist
        if overlap > 0:
            if not self.moves:
                self_correction = 0
                other_correction = overlap
            elif not other.moves:
                self_correction = overlap
                other_correction = 0
            else:
                self_correction = overlap / 2
                other_correction = overlap / 2
            
            # normalize displacement vector
            nx, ny = dx / dist, dy / dist
            self.x -= nx * self_correction
            self.y -= ny * self_correction
            other.x += nx * other_correction
            other.y += ny * other_correction

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
            self.ccd_resolve(other, dt)
        
        self.v += 0.5 * (old_a + self.a) * dt
        
        self.rect.center = (self.x, self.y)
    
    def one_info_particle(self):
        """
        Ensure only one particle is marked for info display at a time.
        """
        for particle in self.particles:
            if particle.info and particle != self:
                self.info = False
                return

    def update_physics(self, dt, quadtree, grid, counter):
        if self.moves:
            self.old_pos = (self.x, self.y)
            self.update_position(dt, quadtree, grid, counter)
            self.new_pos = (self.x, self.y)
    
    def update_drawing(self, cam):
        if self.info:
            self.one_info_particle()
            self.draw_highlight(cam)
        if self.being_dragged:
            self.draw_highlight(cam)
        if not self.info or not self.being_dragged:
            self.update_sprite()
    
    def update(self, dt, cam, grid, quadtree, counter):
        """
        Update the particle each frame: apply forces, update position, color, and highlight.
        Args:
            dt (float): Delta time since last frame.
            cam: Camera object.
            grid: the spatial grid for particle collisions
            quadtree: Quadtree for neighbor lookup.
        """
        self.update_physics(dt, quadtree, grid, counter)
        self.update_drawing(cam)
