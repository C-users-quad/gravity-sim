from settings import *
from utils import *


class Particle(pygame.sprite.Sprite):
    """
    Represents a particle in the gravity simulation. Handles physics, rendering, and interactions.
    """
    def __init__(self, x, y, vx, vy, mass, density, groups, particles):
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
        self.mass = mass # mass in kilograms (kg)
        self.density = density
        self.radius = calculate_radius(self.mass, self.density)
        self.particles = particles # all other particles
        self.min_highlight_width = 5

        self.much = 1000 # if the particle's mass does not change by this value in a frame, then dont update the color.
        self.update_color()

        self.being_dragged = False
        self.in_menu = False
        self.info = False

        self.old_pos = self.new_pos = (self.x, self.y)

        self.groups = groups
        super().__init__(groups)
        self.update_sprite()
    
    def update_sprite(self):
        """
        Update the particle's image and rect based on its radius and color.
        """
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA).convert_alpha()
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_frect(center = (self.x, self.y))

    def draw_highlight(self, cam):
        """
        Draw a highlight border around the particle when selected or dragged.
        Args:
            cam: Camera object for zoom.
        """
        highlight_width = int(self.radius*0.05)
        highlight_width = self.min_highlight_width if highlight_width < self.min_highlight_width else highlight_width
        highlight_width = int(highlight_width / cam.zoom)
        pygame.draw.circle(self.image, HIGHLIGHT_COLOR, (self.radius, self.radius), self.radius, highlight_width)
    
    def handle_particle_interactions(self, dt, grid):
        for other in grid.get_neighbors(self):
            if other == self or other.being_dragged:
                continue
            # force application and distance collision check
            self.apply_forces(other, dt)
            # collision check  
            self.check_collision_and_merge(other)

    def check_collision_and_merge(self, other):
        """Continuous collision detection for two moving circles in one frame."""
        # Relative motion
        ### rel_vx = (distance moved by self particle on x axis) - (distance moved by other particle on x axis)
        ### rel_vy = (distance moved by self particle on y axis) - (distance moved by other particle on y axis)
        rel_vx = (self.new_pos[0] - self.old_pos[0]) - (other.new_pos[0] - other.old_pos[0])
        rel_vy = (self.new_pos[1] - self.old_pos[1]) - (other.new_pos[1] - other.old_pos[1])

        # Starting offset
        dx = self.old_pos[0] - other.old_pos[0]
        dy = self.old_pos[1] - other.old_pos[1]

        # Combined radius
        R = self.radius + other.radius

        # Quadratic equation for time of collision: |(dx, dy) + t*(rel_vx, rel_vy)|^2 = R^2
        a = rel_vx**2 + rel_vy**2 # velocity of self toward other
        b = 2 * (dx * rel_vx + dy * rel_vy) # 
        c = dx**2 + dy**2 - R**2 # distance squared minus combined radius squared

        # if a is 0, then the particles arent moving.
        if a == 0:  # No relative motion — static overlap check
            # if c is less than or equal to zero, then the particles are closer than their radiuses combined, or at that distance.
            if c <= 0:
                self.combine_with(other)
            return

        discriminant = b**2 - 4*a*c
        # negative discriminant = no solutions = no intersections.
        if discriminant < 0:
            return  # No intersection

        sqrt_disc = math.sqrt(discriminant)
        # the 2 solutions to the quadratic are t1 and t2. the values of t between these 2 are the time during this frame.
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)

        # If any collision happens within this frame [0,1]
        if (0 <= t1 <= 1) or (0 <= t2 <= 1):
            self.combine_with(other)

    def apply_forces(self, other, dt):
        """
        Apply gravitational forces from neighboring particles.
        Args:
            dt (float): Delta time since last frame.
        """
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            direction = pygame.Vector2(dx, dy).normalize()
            force = G * self.mass * other.mass / distance ** 2
            self.v += (direction * force / self.mass) * dt

    def combine_with(self, other):
        """
        Combine this particle with another, updating mass, velocity, and position.
        Args:
            other: Another Particle object.
        """
        new_v = velocity_of_combined_particles(self, other)
        new_mass = self.mass + other.mass
        new_pos = self.rect.center if self.mass >= other.mass else other.rect.center

        if self.mass >= other.mass:
            self.x, self.y = new_pos
            self.v = new_v
            self.mass = new_mass
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
    
    def update_position(self, dt):
        """
        Update the particle's position based on velocity and handle window collisions.
        Args:
            dt (float): Delta time since last frame.
        """
        self.x += self.v.x * dt
        self.window_collisions("horizontal")
        
        self.y += self.v.y * dt
        self.window_collisions("vertical")
        
        self.rect.center = (self.x, self.y)

    def update_color(self):
        """
        Update the particle's color based on its mass percentile among all particles.
        """
        if hasattr(self, "old_mass"):
            if self.mass == self.old_mass:
                return
            elif abs(self.mass - self.old_mass) < self.much:
                return
        
        masses = np.array([p.mass for p in self.particles] + [self.mass])
        percentiles = np.percentile(masses, np.linspace(0, 100, 11))  # 10 intervals

        colors = [
            "#05d1ff", "#35c5ff", "#6bb7ff", "#92a7ff", "#be8bff",
            "#ea66f3", "#ff37c5", "#ff2e8f", "#ff0b58", "#ff0000"
        ]

        # Find which percentile bin this particle's mass falls into
        for i in range(len(percentiles) - 1):
            if percentiles[i] <= self.mass < percentiles[i + 1]:
                self.color = colors[i]
                break
        else:
            self.color = colors[-1]
        self.old_mass = self.mass
    
    def is_within_render_distance(self, cam):
        """
        Check if the particle is within render distance of the camera.
        Args:
            cam: Camera object.
        Returns:
            bool: True if within render distance, else False.
        """
        return (self.rect.centerx - cam.pos.x)**2 + (self.rect.centery - cam.pos.y)**2 < (RENDER_DISTANCE / cam.zoom)**2
    
    def one_info_particle(self):
        """
        Ensure only one particle is marked for info display at a time.
        """
        for particle in self.particles:
            if particle.info and particle != self:
                self.info = False
                return

    def update(self, dt, cam, grid):
        """
        Update the particle each frame: apply forces, update position, color, and highlight.
        Args:
            dt (float): Delta time since last frame.
            cam: Camera object.
            grid: SpatialGrid for neighbor lookup.
        """
        if self.being_dragged != True and self.is_within_render_distance(cam) and not self.in_menu:
            self.old_pos = (self.x, self.y)
            self.update_sprite()
            self.update_position(dt)
            self.new_pos = (self.x, self.y)
            self.handle_particle_interactions(dt, grid)
            self.update_color()
        if self.info:
            self.draw_highlight(cam)
            self.one_info_particle()
        if self.being_dragged:
            self.draw_highlight(cam)
