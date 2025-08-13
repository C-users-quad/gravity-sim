from settings import *
from cam import Cam
from particle import *
from groups import *
from menu import *
from utils import *
from hints import *


class Game:
    """
    Main game class for the gravity simulation. Handles initialization, input,
    rendering, game loop, and event management.
    """
    def __init__(self):
        """
        Initialize the game, set up display, state variables, groups, sprites, and grid.
        """
        # setup
        pygame.init()
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('atomic')
        self.on = True
        self.clock = pygame.time.Clock()
        self.mouse = pygame.mouse
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # game state variables
        self.dragged_particle = None
        self.info_particle = None
        self.old_world_mouse_pos = pygame.Vector2(self.mouse.get_pos())
        self.menu_open = False
        self.particle_menu = None
        
        # groups
        self.all_sprites = AllSprites()
        self.particles = pygame.sprite.Group()
        self.logtext = pygame.sprite.Group()
        
        # sprites
        self.cam = Cam()
        self.font = pygame.font.Font(None, 20)
        
        # spatial partitioning grid
        self.grid = SpatialGrid(CELL_SIZE)

        # logprinter object
        self.logprinter = LogPrinter(self.font, self.logtext, self.logtext)
    
    def get_input(self, dt, world_mouse_pos, delta_mouse_pos):
        """
        Handle user input for dragging, info display, menu toggling, particle deletion, and particle repopulation.
        Args:
            dt (float): Delta time since last frame.
            world_mouse_pos (Vector2): Mouse position in world coordinates.
            delta_mouse_pos (Vector2): Change in mouse position.
        """
        mouse_presses = self.mouse.get_pressed()
        key_just_pressed = pygame.key.get_just_pressed()
        key_held = pygame.key.get_pressed()

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
                    self.info_particle.info = True
            if self.info_particle:
                # RMB + LCTRL = camera follows info particle
                if key_held[pygame.K_LCTRL]:
                    particle_pos = pygame.Vector2(self.info_particle.rect.center)
                    # self.cam.zoom = 1
                    self.cam.pos = particle_pos
        
        # get rid of particle info
        if key_just_pressed[pygame.K_ESCAPE]:
            if self.particle_menu:
                self.particle_menu = None
                self.particle_menu.exit_menu(self.logprinter, "dont create particle")
            
            elif self.info_particle:
                self.info_particle.info = False
                self.info_particle = None

        # opens + closes particle creation menu
        if key_just_pressed[pygame.K_RETURN]:
            if not self.particle_menu:
                if len(self.particles) >= MAX_PARTICLES:
                    self.logprinter.print(f"There are too many particles!", type="error")
                    return
                self.particle_menu = ParticleCreationMenu(self.font, self.manager, (self.all_sprites, self.particles), self.particles)
            else:
                self.info_particle = self.particle_menu.menu_particle
                self.info_particle.info = True
                self.particle_menu.exit_menu(self.logprinter, "create particle")
                self.particle_menu = None
        
        # deletes particle thats being interacted with
        if key_just_pressed[pygame.K_BACKSPACE]:
            if self.info_particle:
                self.info_particle.kill()
                self.info_particle = None
            if self.dragged_particle:
                self.dragged_particle.kill()
                self.dragged_particle = None

        # repopulates the simulation until there are NUM_PARTICLES particles in it.
        if key_just_pressed[pygame.K_r]:
            if len(self.particles) >= NUM_PARTICLES:
                self.logprinter.print("Theres already enough particles!", type="error")
                return
            num_particles_to_make = NUM_PARTICLES - len(self.particles)
            self.make_particles(num_particles_to_make)
            self.logprinter.print(f"Made {num_particles_to_make} particles!", type="info")

    def draw_particle_info(self):
        """
        Draw information about the selected particle on the screen.
        """
        # if any info particle exists, draw its info
        if self.info_particle and self.info_particle.alive():
            particle_info = [
                "----------[PARTICLE INFO]----------",
                f"mass = {format(self.info_particle.mass, ",")} kg",
                f"velocity = {self.info_particle.v} m/s",
                f"density = {self.info_particle.density}",
                f"radius = {self.info_particle.radius} m",
                f"position = {truncate_decimal(self.info_particle.rect.centerx, 1), truncate_decimal(self.info_particle.rect.centery, 1)}"
            ]
            draw_info(particle_info, self.font, self.display_surf, "topleft")
        else:
            self.info_particle = None
    
    def draw_cam_info(self):
        """
        Draw camera information (position, speed, zoom, fps) on the screen.
        """
        cam_info = [
            "----------[CAM INFO]----------",
            f"pos = {truncate_decimal(self.cam.pos.x, 1), truncate_decimal(self.cam.pos.y, 1)}",
            f"speed = {self.cam.speed}",
            f"zoom = {truncate_decimal(self.cam.zoom, 1)}x",
            f"fps = {truncate_decimal(self.clock.get_fps(), 0)}"
        ]
        draw_info(cam_info, self.font, self.display_surf, "topright")
    
    # initializes the game with particles
    def make_particles(self, num):
        """
        Create and initialize all particles for the simulation.
        """
        for _ in range(num):
            args = (
                randint(-HALF_WORLD_WIDTH, HALF_WORLD_WIDTH),   # x
                randint(-HALF_WORLD_HEIGHT, HALF_WORLD_HEIGHT), # y
                randint(0, MAX_STARTING_VELOCITY),  # vx
                randint(0, MAX_STARTING_VELOCITY),  # vy
                randint(1, MAX_STARTING_MASS),  # mass
                randint(1, MAX_STARTING_DENSITY),   # density
                (self.all_sprites, self.particles), # groups
                self.particles  # particles
            )
            Particle(*args)
    
    def draw_world_border(self):
        """
        Draw the border of the simulated world on the screen.
        """
        x = -HALF_WORLD_WIDTH - BORDER_WIDTH
        y = -HALF_WORLD_HEIGHT - BORDER_WIDTH
        width = HALF_WORLD_WIDTH * 2 + BORDER_WIDTH * 2
        height = HALF_WORLD_HEIGHT * 2 + BORDER_WIDTH * 2
        border_width = math.ceil(BORDER_WIDTH * self.cam.zoom)

        rect = pygame.FRect(x, y, width, height)
        # Apply cam transformation:
        win_w, win_h = self.display_surf.get_size()
        screen_rect = pygame.FRect(
            (rect.x - self.cam.pos.x) * self.cam.zoom + win_w // 2,
            (rect.y - self.cam.pos.y) * self.cam.zoom + win_h // 2,
            rect.width * self.cam.zoom,
            rect.height * self.cam.zoom
        )

        pygame.draw.rect(self.display_surf, BORDER_COLOR, screen_rect, border_width if border_width > 0 else 1)
    
    def run(self):
        """
        Main game loop. Handles updates, drawing, and event processing.
        """
        self.make_particles(NUM_PARTICLES)
        while self.on:
            self.grid.clear_grid()
            for particle in self.particles:
                self.grid.add_particle(particle)
        
            dt = self.clock.tick(FPS) / 1000

            self.cam.update(dt)
            self.event_handler()
            self.all_sprites.update(dt, self.cam, self.grid)
            self.logtext.update(dt)

            world_mouse_pos = (pygame.Vector2(self.mouse.get_pos()) - self.all_sprites.offset) / self.cam.zoom
            delta_mouse_pos = world_mouse_pos - self.old_world_mouse_pos
            self.get_input(dt, world_mouse_pos, delta_mouse_pos)
            self.old_world_mouse_pos = world_mouse_pos

            self.display_surf.fill(BG_COLOR)
            if not self.particle_menu:
                self.all_sprites.draw(self.cam)
                self.draw_cam_info()
                self.draw_world_border()
                self.draw_particle_info()
                self.logtext.draw(self.display_surf)
                display_hints(self.logprinter)
            
            self.manager.update(dt)
            if self.particle_menu:
                self.particle_menu.update(self.manager)
                self.manager.draw_ui(self.display_surf)

            pygame.display.update()
            
    def event_handler(self):
        """
        Handle all pygame events, including quit, input, camera controls, and menu interactions.
        """
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

            # if a particle creation menu is open, filter its input boxes to only accept valid characters
            if self.particle_menu:
                if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    for i, box in enumerate(self.particle_menu.input_boxes):
                        if box == event.ui_element:
                            input = box.get_text()
                            if input:
                                if input[0] == '-':
                                    numbers = ''.join(filter(str.isdigit, input))
                                    box.set_text('-' + numbers)
                                else:
                                    box.set_text(''.join(filter(str.isdigit, input)))
            
            if event.type == pygame.VIDEORESIZE:
                self.manager.set_window_resolution((event.w, event.h))

if __name__ == '__main__':
    game = Game()
    game.run()
