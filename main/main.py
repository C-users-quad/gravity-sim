from settings import *
from cam import Cam
from sprites import *
from groups import *
from menu import *


class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surf = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('atomic')
        self.on = True
        self.clock = pygame.time.Clock()
        self.mouse = pygame.mouse
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # settings
        self.dragged_particle = None
        self.info_particle = None
        self.old_world_mouse_pos = pygame.Vector2(self.mouse.get_pos())
        self.menu_open = False
        self.particle_menu = None
        
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
        key_presses = pygame.key.get_just_pressed()

        # drag particles with left click
        if mouse_presses[0]:
            if self.dragged_particle:
                # drag the particle
                self.dragged_particle.rect.center = world_mouse_pos
                self.dragged_particle.x = world_mouse_pos.x
                self.dragged_particle.y = world_mouse_pos.y
                self.dragged_particle.v = delta_mouse_pos / dt
            else:
                # find what particle (if any) was dragged and label it as the dragged particle
                particle = find_particle(self.particles, world_mouse_pos)
                if self.particle_menu:
                    if particle == self.particle_menu.menu_particle:
                        particle = None
                if particle:
                    self.dragged_particle = particle
                    particle.being_dragged = True
        else:
            # if the LMB is let go and a particle was previously dragged, it strips that particle of its label.
            if self.dragged_particle:
                self.dragged_particle.being_dragged = False
                if not PARTICLE_SPEED_AFTER_DRAGGING_UNCHANGED:
                    self.dragged_particle.v = self.dragged_particle.v.normalize() * PARTICLE_SPEED_AFTER_DRAGGING if self.dragged_particle.v else self.dragged_particle.v
                self.dragged_particle = None
                
        # display particle info with right click
        if mouse_presses[2]:
            if not self.info_particle:
                particle = find_particle(self.particles, world_mouse_pos)
                if particle:
                    self.info_particle = particle
            if self.info_particle:
                # RMB + LCTRL = tp to info particle
                if key_presses[pygame.K_LCTRL]:
                    particle_pos = pygame.Vector2(self.info_particle.rect.center)
                    self.cam.zoom = 1
                    self.cam.pos = particle_pos
        
        # get rid of particle info
        if key_presses[pygame.K_ESCAPE]:
            if self.menu_open:
                self.menu_open = False
                if self.particle_menu:
                    for input_box in self.particle_menu.input_boxes:
                        input_box.kill()
                    self.particle_menu = None
            
            elif self.info_particle:
                self.info_particle = None
                
            

        # opens particle creation menu
        if key_presses[pygame.K_RETURN]:
            if not self.menu_open:
                self.particle_menu = ParticleCreationMenu(self.display_surf, self.font, self.manager, (self.all_sprites, self.particles), self.particles)
                self.menu_open = True
            
        
        # deletes particle thats being interacted with
        if key_presses[pygame.K_BACKSPACE]:
            if self.info_particle:
                self.info_particle.kill()
                self.info_particle = None
            if self.dragged_particle:
                self.dragged_particle.kill()
                self.dragged_particle = None

    def draw_particle_info(self):
        if self.info_particle and self.info_particle.alive():
            particle_info = [
                "----------[PARTICLE INFO]----------",
                f"mass = {self.info_particle.mass}",
                f"velocity = {self.info_particle.v}",
                f"density = {self.info_particle.density}",
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
            density = randint(1, MAX_STARTING_DENSITY)
            Particle(x, y, vx, vy, mass, density, (self.all_sprites, self.particles), self.particles)
    
    def draw_world_border(self):
        x = -HALF_WORLD_WIDTH - BORDER_WIDTH
        y = -HALF_WORLD_HEIGHT - BORDER_WIDTH
        width = HALF_WORLD_WIDTH * 2 + BORDER_WIDTH * 2
        height = HALF_WORLD_HEIGHT * 2 + BORDER_WIDTH * 2
        border_width = math.ceil(BORDER_WIDTH * self.cam.zoom)

        rect = pygame.FRect(x, y, width, height)
        # Apply cam transformation:
        screen_rect = pygame.FRect(
            (rect.x - self.cam.pos.x) * self.cam.zoom + WINDOW_WIDTH // 2,
            (rect.y - self.cam.pos.y) * self.cam.zoom + WINDOW_HEIGHT // 2,
            rect.width * self.cam.zoom,
            rect.height * self.cam.zoom
        )

        pygame.draw.rect(self.display_surf, (240, 240, 240), screen_rect, border_width if border_width > 0 else 1)
    
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

            self.display_surf.fill(BG_COLOR)
            if not self.menu_open:
                self.all_sprites.draw(self.cam)
                self.draw_cam_info()
                self.draw_world_border()
                self.draw_particle_info()
            
            self.manager.update(dt)
            if self.menu_open:
                self.particle_menu.update()
                self.manager.draw_ui(self.display_surf)

            pygame.display.update()
            
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            self.manager.process_events(event)
                
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
                    
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                for i, box in enumerate(self.particle_menu.input_boxes):
                    if box == event.ui_element:
                        input = box.get_text()
                        if input[0] == '-':
                            box.set_text('-'.join(filter(str.isdigit, input)))
                        else:
                            box.set_text(''.join(filter(str.isdigit, input)))


if __name__ == '__main__':
    game = Game()
    game.run()
