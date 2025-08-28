from settings import *
if TYPE_CHECKING:
    from particle import Particle

class Cam:
    """
    Camera class for handling position, movement, and zoom in the simulation world.
    """
    def __init__(self):
        """
        Initialize the camera with default position, speed, direction, and zoom.
        """
        self.pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.speed = MIN_CAM_SPEED
        self.direction = pygame.Vector2()
        self.zoom = 1
        
    def input(self):
        """
        Process keyboard input to set camera movement direction.
        """
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction
    
    def world_clamp(self, direction):
        """
        Clamp the camera position to stay within the world boundaries.
        Args:
            direction (str): 'horizontal' or 'vertical' axis to clamp.
        """
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
        """
        Move the camera based on direction, speed, and delta time.
        Args:
            dt (float): Delta time since last frame.
        """
        self.pos.x += self.direction.x * self.speed * dt
        self.world_clamp("horizontal")
        
        self.pos.y += self.direction.y * self.speed * dt
        self.world_clamp("vertical")
    
    def set_pos(self, pos: Sequence[float]):
        self.pos = pygame.Vector2(pos[0], pos[1])

    def filter_rendered_particles(self, particles: Sequence["Particle"]):
        camx, camy = self.pos
        buffer_factor = 1.2
        screen_size = pygame.display.get_surface().get_size()
        render_distance = (max(MIN_RENDER_DISTANCE, max(screen_size[0], screen_size[1]) / self.zoom)) * buffer_factor
        return [ p for p in particles if (p.x - camx)**2 + (p.y - camy)**2 <= render_distance**2 ]

    def update(self, dt):
        """
        Update the camera each frame: process input and move.
        Args:
            dt (float): Delta time since last frame.
        """
        self.input()
        self.move(dt)
