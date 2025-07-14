from settings import *
from cam import Cam
from sprites import *
from groups import *


class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surf = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('atomic')
        self.on = True
        self.clock = pygame.time.Clock()
        self.mouse = pygame.mouse
        
        # settings
        self.dragged_particle = None
        self.info_particle = None
        self.old_world_mouse_pos = pygame.Vector2(self.mouse.get_pos())
        
        # groups
        self.all_sprites = AllSprites()
        self.particles = pygame.sprite.Group()
        
        # sprites
        self.cam = Cam()
        self.font = pygame.font.Font(None, 20)
        
        # spatial partitioning grid
        self.grid = SpatialGrid(CELL_SIZE)
    
    def get_input(self, dt, world_mouse_pos, delta_mouse_pos):
        mouse_presses = self.mouse.get_pressed()
        key_presses = pygame.key.get_pressed()
        pygame.draw.circle(self.display_surf, "yellow", world_mouse_pos, 10)

        # drag the mouse if its left click
        if mouse_presses[0]:
            if self.dragged_particle:
                # drag the particle
                self.dragged_particle.rect.center = world_mouse_pos
                self.dragged_particle.x = world_mouse_pos.x
                self.dragged_particle.y = world_mouse_pos.y
                self.dragged_particle.v = delta_mouse_pos / dt
            else:
                # find what particle (if any) was dragged and label it as the dragged particle
                for particle in self.particles:
                    if particle.rect.collidepoint(world_mouse_pos):
                        self.dragged_particle = particle
                        particle.being_interacted_with = True
                        break
        else:
            # if the LMB is let go and a particle was previously dragged, it strips that particle of its label.
            if self.dragged_particle:
                self.dragged_particle.being_interacted_with = False
                if not PARTICLE_SPEED_AFTER_DRAGGING_UNCHANGED:
                    self.dragged_particle.v = self.dragged_particle.v.normalize() * PARTICLE_SPEED_AFTER_DRAGGING if self.dragged_particle.v else self.dragged_particle.v
                self.dragged_particle = None
                
        # display particle info
        if mouse_presses[2]:
            for particle in self.particles:
                if particle.rect.collidepoint(world_mouse_pos):
                    self.info_particle = particle
                    break
        
        # get rid of particle info
        if key_presses[pygame.K_ESCAPE]:
            self.info_particle = None

    def draw_particle_info(self):
        if self.info_particle and self.info_particle.alive():
            particle_info = [
                "----------[PARTICLE INFO]----------",
                f"mass = {self.info_particle.mass}",
                f"velocity = {self.info_particle.v}",
                f"radius = {self.info_particle.radius}",
                f"position = {truncate_decimal(self.info_particle.rect.centerx, 1), truncate_decimal(self.info_particle.rect.centery, 1)}"
            ]
            draw_info(particle_info, self.font, self.display_surf, "topleft")
        else:
            self.info_particle = None
    
    def draw_cam_info(self):
        cam_info = [
            "----------[CAM INFO]----------",
            f"pos = {truncate_decimal(self.cam.pos.x, 1), truncate_decimal(self.cam.pos.y, 1)}",
            f"speed = {self.cam.speed}",
            f"zoom = {truncate_decimal(self.cam.zoom, 1)}x",
            f"fps = {truncate_decimal(self.clock.get_fps(), 0)}"
        ]
        draw_info(cam_info, self.font, self.display_surf, "topright")
    
    def make_particles(self):
        for _ in range(NUM_PARTICLES):
            x = randint(-HALF_WORLD_WIDTH, HALF_WORLD_WIDTH)
            y = randint(-HALF_WORLD_HEIGHT, HALF_WORLD_HEIGHT)
            vx = randint(0, MAX_STARTING_VELOCITY)
            vy = randint(0, MAX_STARTING_VELOCITY)
            mass = randint(1, MAX_STARTING_MASS)
            Particle(x, y, vx, vy, mass, (self.all_sprites, self.particles), self.particles)
    
    def draw_world_border(self):
        x = -HALF_WORLD_WIDTH - BORDER_WIDTH
        y = -HALF_WORLD_HEIGHT - BORDER_WIDTH
        width = HALF_WORLD_WIDTH * 2 + BORDER_WIDTH * 2
        height = HALF_WORLD_HEIGHT * 2 + BORDER_WIDTH * 2
        border_width = BORDER_WIDTH * self.cam.zoom

        rect = pygame.FRect(x, y, width, height)
        # Apply cam transformation:
        screen_rect = pygame.FRect(
            (rect.x - self.cam.pos.x) * self.cam.zoom + WINDOW_WIDTH // 2,
            (rect.y - self.cam.pos.y) * self.cam.zoom + WINDOW_HEIGHT // 2,
            rect.width * self.cam.zoom,
            rect.height * self.cam.zoom
        )

        pygame.draw.rect(self.display_surf, (240, 240, 240), screen_rect, int(border_width if border_width > 0 else 1), BORDER_WIDTH)
    
    def run(self):
        self.make_particles()
        while self.on:
            self.grid.clear_grid()
            for particle in self.particles:
                self.grid.add_particle(particle)
            
            dt = self.clock.tick(FPS) / 1000

            self.cam.update(dt)
            self.event_handler()
            self.all_sprites.update(dt, self.cam, self.grid)

            world_mouse_pos = (pygame.Vector2(self.mouse.get_pos()) - self.all_sprites.offset) / self.cam.zoom
            delta_mouse_pos = world_mouse_pos - self.old_world_mouse_pos

            self.get_input(dt, world_mouse_pos, delta_mouse_pos)

            self.old_world_mouse_pos = world_mouse_pos

            self.display_surf.fill('#17171a')
            self.all_sprites.draw(self.cam)
            self.draw_cam_info()
            self.draw_world_border()
            self.draw_particle_info()

            pygame.display.update()
            
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # scrolling speeds up the camera movement speeds
            if event.type == pygame.MOUSEWHEEL:
                # LCTRL+SCROLL = ZOOM
                if pygame.key.get_pressed()[pygame.K_LCTRL]:
                    if event.y == 1:
                        self.cam.zoom = min(self.cam.zoom + 0.1, MAX_ZOOM)
                    if event.y == -1:
                        self.cam.zoom = max(self.cam.zoom - 0.1, MIN_ZOOM)
                    continue
                # SCROLL = CAM SPEED
                if event.y == 1:
                    self.cam.speed = min(self.cam.speed + SCROLL_WHEEL_SENSITIVITY, MAX_CAM_SPEED)
                if event.y == -1:
                    self.cam.speed = max(self.cam.speed - SCROLL_WHEEL_SENSITIVITY, MIN_CAM_SPEED)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()


if __name__ == '__main__':
    game = Game()
    game.run()
