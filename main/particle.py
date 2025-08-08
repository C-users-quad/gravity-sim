from settings import *
from utils import *


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, mass, density, groups, particles):
        self.x = x
        self.y = y
        self.v = pygame.Vector2(vx, vy)
        self.mass = mass # mass in kilograms (kg)
        self.density = density
        self.radius = calculate_radius(self.mass, self.density)
        self.highlight_border_width = 5

        self.particles = particles # all other particles

        self.much = 1000

        self.update_color()

        self.being_dragged = False
        self.in_menu = False
        self.info = False

        self.groups = groups
        super().__init__(groups)
        self.update_sprite()
    
    def update_sprite(self):
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA).convert_alpha()
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_frect(center = (self.x, self.y))

    def draw_highlight(self, cam):
        highlight_width = int(self.highlight_border_width / cam.zoom) if int(self.highlight_border_width / cam.zoom) > self.highlight_border_width else self.highlight_border_width
        pygame.draw.circle(self.image, HIGHLIGHT_COLOR, (self.radius, self.radius), self.radius, highlight_width)
    
    def apply_forces(self, dt, grid):
        for other in grid.get_neighbors(self):
            if other == self or other.being_dragged:
                continue

            dx = other.rect.centerx - self.rect.centerx
            dy = other.rect.centery - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance <= (self.radius + other.radius) / 1.2:
                self.combine_with(other)
                return

            if distance > 0:
                direction = pygame.Vector2(dx, dy).normalize()
                force = G * self.mass * other.mass / distance ** 2
                self.v += (direction * force / self.mass) * dt

    def combine_with(self, other):
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
        self.x += self.v.x * dt
        self.window_collisions("horizontal")
        
        self.y += self.v.y * dt
        self.window_collisions("vertical")
        
        self.rect.center = (self.x, self.y)
        
    def update_color(self):
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
        return (self.rect.centerx - cam.pos.x)**2 + (self.rect.centery - cam.pos.y)**2 < (RENDER_DISTANCE / cam.zoom)**2
    
    def one_info_particle(self):
        for particle in self.particles:
            if particle.info and particle != self:
                self.info = False
                return

    def update(self, dt, cam, grid):
        if self.being_dragged != True and self.is_within_render_distance(cam) and not self.in_menu:
            self.apply_forces(dt, grid)
            self.update_sprite()
            self.update_position(dt)
            self.update_color()
    
        if self.info:
            self.draw_highlight(cam)
            self.one_info_particle()
