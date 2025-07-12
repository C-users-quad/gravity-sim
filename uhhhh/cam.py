from settings import *

class Cam:
    def __init__(self):
        self.pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.speed = MIN_CAM_SPEED
        self.direction = pygame.Vector2()
        
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
        
    def move(self, dt):
        self.pos += self.direction * self.speed * dt
        
    def update(self, dt):
        self.input()
        self.move(dt)
