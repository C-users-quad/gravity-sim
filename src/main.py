from settings import *
from cam import Cam
from particle import *
from groups import *
from utils import *
from hints import *
from input import *


class Game:
    """
    Main game class for the gravity simulation. Handles initialization,
    rendering, game loop, and event management.
    """
    def __init__(self):
        """
        Initialize the game, set up display, state variables, groups, sprites, and grid.
        """
        # setup
        pygame.init()
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Gravity Sim')
        # pygame.display.set_icon(pygame.image.load(join('assets', 'icon.ico')))
        self.on = True
        self.clock = pygame.time.Clock()
        self.mouse = pygame.mouse
        self.manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # game state variables
        self.old_world_mouse_pos = pygame.Vector2(self.mouse.get_pos())
        self.particle_menu = None
        self.dt = self.clock.tick(FPS) / 1000

        # groups
        self.particles = ParticleDrawing()
        self.logtext = pygame.sprite.Group()
        
        # sprites
        self.cam = Cam()
        self.font = pygame.font.Font(None, 20)
        self.info_particle = None
        self.dragged_particle = None
        
        # quadtree (lag killer)
        self.quadtree = QuadTree(pygame.FRect(-HALF_WORLD_WIDTH, -HALF_WORLD_HEIGHT, HALF_WORLD_WIDTH * 2, HALF_WORLD_HEIGHT * 2), 1, self.cam)

        # singleton utility objects
        self.logprinter = LogPrinter(self.font, self.logtext, self.logtext)
        self.input = Input(self)
        self.accelerator = Accelerator()

    def draw_particle_info(self):
        """
        Draw information about the selected particle on the screen.
        """
        # if any info particle exists, draw its info
        if self.info_particle and self.info_particle.alive():
            particle_info = [
                "----------[PARTICLE INFO]----------",
                f"mass = {format(self.info_particle.mass, ",")} kg",
                f"velocity = {self.info_particle.v}",
                f"density = {truncate_decimal(self.info_particle.density, 1)}",
                f"radius = {truncate_decimal(self.info_particle.radius, 1)} m",
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
            f"speed = {truncate_decimal(self.cam.speed, 1)}",
            f"zoom = {truncate_decimal(self.cam.zoom, 1)}x",
            f"fps = {truncate_decimal(self.clock.get_fps(), 0)}"
        ]
        draw_info(cam_info, self.font, self.display_surf, "topright")
    
    def make_particles(self, num=None):
        """
        Create and initialize all particles for the simulation.
        """
        for _ in range(NUM_PARTICLES if num == None else num):
            args = (
                randint(-HALF_WORLD_WIDTH, HALF_WORLD_WIDTH),   # x
                randint(-HALF_WORLD_HEIGHT, HALF_WORLD_HEIGHT), # y
                choice([-1, 1]) * randint(1, MAX_STARTING_VELOCITY),  # vx
                choice([-1, 1]) * randint(1, MAX_STARTING_VELOCITY),  # vy
                randint(1, MAX_STARTING_MASS),  # mass
                randint(1, MAX_STARTING_DENSITY),   # density
                self.particles, # groups
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
            (rect.x - self.cam.pos.x) * self.cam.zoom + win_w / 2,
            (rect.y - self.cam.pos.y) * self.cam.zoom + win_h / 2,
            rect.width * self.cam.zoom,
            rect.height * self.cam.zoom
        )

        pygame.draw.rect(self.display_surf, BORDER_COLOR, screen_rect, border_width if border_width > 0 else 1)

    def pass_in_vars(self):
        """Passes in certain variables used in both files to avoid runtime errors."""
        self.info_particle = self.input.info_particle
        self.dragged_particle = self.input.dragged_particle
        self.particle_menu = self.input.particle_menu

    def run(self):
        """
        Main game loop. Handles updates, drawing, and event processing.
        """
        self.make_particles()
        frame_count = 0
        while self.on:
            frame_count += 1
            self.quadtree.clear()
            self.dt = self.clock.tick(FPS) / 1000

            percentiles = calculate_color_bins(self.particles, frame_count)
            particles = find_particles_in_render_distance(self.particles, self.cam)

            for particle in particles:
                self.quadtree.insert(particle)

            update_particles(particles, self.dt, self.cam, percentiles, self.quadtree)

            self.logtext.update(self.dt)
            self.input.get_input(self.dt)
            self.event_handler()
            self.cam.update(self.dt)

            self.pass_in_vars()

            self.display_surf.fill(BG_COLOR)
            if not self.particle_menu:
                self.quadtree.visualize(self.cam.zoom, self.particles.offset)
                self.particles.draw(self.cam)
                # Draw lines between neighboring particles [DEBUG]
                for particle in particles:
                    if particle.alive():
                        particle.draw_neighbor_lines(self.display_surf, self.cam, self.quadtree)
                self.draw_cam_info()
                self.draw_world_border()
                self.draw_particle_info()
                self.logtext.draw(self.display_surf)
                display_hints(self.logprinter)

            self.manager.update(self.dt)
            if self.particle_menu:
                self.particle_menu.update(self.manager, percentiles)
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
                    self.cam.zoom = self.accelerator.accelerate(self.cam.zoom, event.y, self.dt, "cam zoom")
                    continue
                # SCROLL = CAM SPEED
                self.cam.speed = self.accelerator.accelerate(self.cam.speed, event.y, self.dt, "cam speed")
                    
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
