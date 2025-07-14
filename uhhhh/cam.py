from settings import *

class Cam:
    def __init__(self):
        self.pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.speed = MIN_CAM_SPEED
        self.direction = pygame.Vector2()
        self.zoom = 1
        
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
    
    def world_clamp(self, direction):
        if direction == "vertical":
            if self.pos.y < -HALF_WORLD_HEIGHT: self.pos.y = -HALF_WORLD_HEIGHT
            if self.pos.y > HALF_WORLD_HEIGHT: self.pos.y = HALF_WORLD_HEIGHT
        if direction == "horizontal":
            if self.pos.x < -HALF_WORLD_WIDTH: self.pos.x = -HALF_WORLD_WIDTH
            if self.pos.x > HALF_WORLD_WIDTH: self.pos.x = HALF_WORLD_WIDTH
    
    def move(self, dt):
        self.world_clamp("horizontal")
        self.pos.x += self.direction.x * self.speed * dt * self.zoom
        
        self.world_clamp("vertical")
        self.pos.y += self.direction.y * self.speed * dt * self.zoom
        
    def update(self, dt):
        self.input()
        self.move(dt)
