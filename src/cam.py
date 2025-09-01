from settings import *

class Camera:
    def __init__(self):
        self.zoom = 1
        self.speed = 10
        self.zoom_increment = 0.1 # how much zoom changes by when u scroll
        self.pos = np.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], dtype=np.float32)
        self.direction = pygame.Vector2()

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        self.pos[0] += self.direction.x * self.speed * dt
        self.pos[1] += self.direction.y * self.speed * dt
        
    def update_zoom(self, scroll_direction):
        new_zoom = self.zoom + scroll_direction * self.zoom_increment
        self.zoom = max(MIN_ZOOM, min(new_zoom, MAX_ZOOM))
        print(self.zoom)

    def update(self, dt):
        self.input()
        self.move(dt)


