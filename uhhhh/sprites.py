from settings import *


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, mass, groups, particles):
        self.x = x
        self.y = y
        self.v = pygame.Vector2(vx, vy)
        self.mass = mass # mass in kilograms (kg)
        self.radius = max(MIN_RADIUS, int(self.mass**(1/3))) if max(MIN_RADIUS, int(self.mass**(1/3))) <= MAX_RADIUS else MAX_RADIUS
        self.particles = particles # all other particles
        self.color_interval = int(MAX_STARTING_MASS / 10)
        self.update_color()
        self.being_interacted_with = False
        
        self.groups = groups
        super().__init__(self.groups)
        self.update_sprite()
    
    def update_sprite(self):
        self.image = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_frect(center = (self.x, self.y))
    
    def update_direction(self, dt):
        for particle in self.particles:
            if particle == self or particle.being_interacted_with == True:
                continue

            dx = particle.rect.centerx - self.rect.centerx
            dy = particle.rect.centery - self.rect.centery
            
            distance = math.sqrt((dx)**2 + (dy)**2)
            
            if distance > MAX_GRAVITY_DISTANCE:
                continue
            
            if distance <= (self.radius + particle.radius) / 3:
                new_v = velocity_of_combined_particles(self, particle)
                new_mass = combined_masses(self, particle)
                new_pos = (self.rect.centerx, self.rect.centery) if self.mass >= particle.mass else (particle.rect.centerx, particle.rect.centery)
                if self.mass > particle.mass:
                    (self.x, self.y), self.v, self.mass = (new_pos[0], new_pos[1]), pygame.Vector2(new_v.x, new_v.y), new_mass
                    self.radius = max(MIN_RADIUS, int(self.mass**(1/3))) if max(MIN_RADIUS, int(self.mass**(1/3))) <= MAX_RADIUS else MAX_RADIUS
                    self.update_sprite()
                    particle.kill()
                else:
                    (self.x, self.y), particle.v, particle.mass = (new_pos[0], new_pos[1]), pygame.Vector2(new_v.x, new_v.y), new_mass
                    particle.radius = max(MIN_RADIUS, int(particle.mass**(1/3))) if max(MIN_RADIUS, int(particle.mass**(1/3))) <= MAX_RADIUS else MAX_RADIUS
                    particle.update_sprite()
                    self.kill()
                return
            
            direction_to_particle = pygame.Vector2(dx, dy).normalize() if distance > 0 else pygame.Vector2()
            force_of_gravity = (G * self.mass * particle.mass) / distance**2
            acceleration = (direction_to_particle * force_of_gravity) / self.mass
            
            self.v += acceleration * dt
    
    def window_collisions(self, direction):
        if direction == "vertical":
            if self.rect.top < 0:
                self.rect.top = 0
                self.v.y *= -1
                self.y = self.rect.centery
            if self.rect.bottom > WINDOW_HEIGHT:
                self.rect.bottom = WINDOW_HEIGHT
                self.v.y *= -1
                self.y = self.rect.centery
        if direction == "horizontal":
            if self.rect.left < 0:
                self.rect.left = 0
                self.v.x *= -1
                self.x = self.rect.centerx
            if self.rect.right > WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
                self.v.x *= -1
                self.x = self.rect.centerx
    
    def update_position(self, dt):
        self.x += self.v.x * dt
        # self.window_collisions("horizontal")
        
        self.y += self.v.y * dt
        # self.window_collisions("vertical")
        
        self.rect.center = (self.x, self.y)
        
    def update_color(self):
        if self.mass in range(0, self.color_interval):
            self.color = "#05d1ff"
        elif self.mass in range(self.color_interval, self.color_interval*2):
            self.color = "#35c5ff"
        elif self.mass in range(self.color_interval*2, self.color_interval*3):
            self.color = "#6bb7ff"
        elif self.mass in range(self.color_interval*3, self.color_interval*4):
            self.color = "#92a7ff"
        elif self.mass in range(self.color_interval*4, self.color_interval*5):
            self.color = "#be8bff"
        elif self.mass in range(self.color_interval*5, self.color_interval*6):
            self.color = "#ea66f3"
        elif self.mass in range(self.color_interval*6, self.color_interval*7):
            self.color = "#ff37c5"
        elif self.mass in range(self.color_interval*7, self.color_interval*8):
            self.color = "#ff2e8f"
        elif self.mass in range(self.color_interval*8, self.color_interval*9):
            self.color = "#ff0b58"
        else:
            self.color = "#ff0000"
    
    def is_within_render_distance(self, cam_pos):
        return (self.rect.centerx - cam_pos.x) ** 2 + (self.rect.centery - cam_pos.y) ** 2 < RENDER_DISTANCE ** 2
    
    def update(self, dt, cam_pos):
        if self.being_interacted_with != True or self.is_within_render_distance(cam_pos):
            self.update_direction(dt)
            self.update_color()
            self.update_position(dt)
            