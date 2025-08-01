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
        half_viewport_width = (WINDOW_WIDTH / 2) / self.zoom
        half_viewport_height = (WINDOW_HEIGHT / 2) / self.zoom
        
        padding = 200
        
        min_x = -HALF_WORLD_WIDTH + half_viewport_width - padding
        max_x= HALF_WORLD_WIDTH - half_viewport_width + padding
        
        if direction == "horizontal":
            if self.pos.x > max_x:
                self.pos.x = max_x
            if self.pos.x < min_x:
                self.pos.x = min_x
        
        min_y = -HALF_WORLD_HEIGHT + half_viewport_height - padding
        max_y = HALF_WORLD_HEIGHT - half_viewport_height + padding
        
        if direction == "vertical":
            if self.pos.y > max_y:
                self.pos.y = max_y
            if self.pos.y < min_y:
                self.pos.y = min_y
    
    def move(self, dt):
        self.world_clamp("horizontal")
        self.pos.x += self.direction.x * self.speed * dt
        
        self.world_clamp("vertical")
        self.pos.y += self.direction.y * self.speed * dt
        
    def update(self, dt):
        self.input()
        self.move(dt)
