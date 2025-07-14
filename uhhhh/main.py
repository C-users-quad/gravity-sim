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
        
        # sprites (camera not in use, if u wanna u can add camm functionality. gotta learn spatial partitioning first tho xd)
        self.cam = Cam()
        self.font = pygame.font.Font(None, 20)
        
        # spatial partitioning stuffs
        self.grid = SpatialGrid(CELL_SIZE)
    
    def get_input(self, dt, world_mouse_pos, delta_mouse_pos):
        mouse_presses = self.mouse.get_pressed()
        key_presses = pygame.key.get_pressed()
        pygame.draw.circle(self.display_surf, "yellow", world_mouse_pos, 10)

        # drag the mouse if its left click
        if mouse_presses[0]:
            if self.dragged_particle:
                # drag the fucking particle
                self.dragged_particle.rect.center = world_mouse_pos
                self.dragged_particle.x = world_mouse_pos.x
                self.dragged_particle.y = world_mouse_pos.y
                self.dragged_particle.v = delta_mouse_pos / dt
            else:
                for particle in self.particles:
                    if particle.rect.collidepoint(world_mouse_pos):
                        self.dragged_particle = particle
                        particle.being_interacted_with = True
                        break
        else:
            if self.dragged_particle:
                self.dragged_particle.being_interacted_with = False
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
                f"mass = {self.info_particle.mass}",
                f"velocity = {self.info_particle.v}",
                f"radius = {self.info_particle.radius}",
                f"position = {self.info_particle.rect.center}"
            ]

            y_offset = 10
            padding = 4
            spacing = 4

            for info in particle_info:
                # Render text
                text_surf = self.font.render(info, True, "white")
                text_rect = text_surf.get_rect(topleft=(10 + padding, y_offset + padding))

                # Draw translucent background rect
                rect_width = text_rect.width + padding * 2
                rect_height = text_rect.height + padding * 2
                rect_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
                rect_surf.fill(INFO_RECT_COLOR)  # translucent gray
                
                self.display_surf.blit(rect_surf, (10, y_offset))
                self.display_surf.blit(text_surf, text_rect)

                y_offset += rect_height + spacing
        else:
            self.info_particle = None
    
    def run(self):
        # creates a buncha particles
        for _ in range(NUM_PARTICLES):
            x = randint(-HALF_WORLD_WIDTH, HALF_WORLD_WIDTH)
            y = randint(-HALF_WORLD_HEIGHT, HALF_WORLD_HEIGHT)
            vx = randint(0, MAX_STARTING_VELOCITY)
            vy = randint(0, MAX_STARTING_VELOCITY)
            mass = randint(1, MAX_STARTING_MASS)
            Particle(x, y, vx, vy, mass, (self.all_sprites, self.particles), self.particles)
        
        while self.on:
            self.grid.clear_grid()
            for particle in self.particles:
                self.grid.add_particle(particle)
            
            dt = self.clock.tick(FPS) / 1000

            self.cam.update(dt)
            self.event_handler()
            self.all_sprites.update(dt, self.cam.pos, self.grid)

            world_mouse_pos = (pygame.Vector2(self.mouse.get_pos()) - self.all_sprites.offset) / self.cam.zoom
            delta_mouse_pos = world_mouse_pos - self.old_world_mouse_pos

            self.get_input(dt, world_mouse_pos, delta_mouse_pos)

            self.old_world_mouse_pos = world_mouse_pos

            self.display_surf.fill('#17171a')
            self.all_sprites.draw(self.cam.pos, self.cam.zoom)
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
