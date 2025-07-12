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
        self.fps = FPS
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
                f"radius = {self.info_particle.radius}"
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
            dt = self.clock.tick(self.fps) / 1000

            self.cam.update(dt)
            self.event_handler()
            self.all_sprites.update(dt, self.cam.pos)

            world_mouse_pos = pygame.Vector2(self.mouse.get_pos()) - self.all_sprites.offset
            delta_mouse_pos = world_mouse_pos - self.old_world_mouse_pos

            self.get_input(dt, world_mouse_pos, delta_mouse_pos)

            self.old_world_mouse_pos = world_mouse_pos

            self.display_surf.fill('#17171a')
            self.all_sprites.draw(self.cam.pos)
            self.draw_particle_info()

            pygame.display.update()
            
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # scrolling speeds up the camera movement speeds
            if event.type == pygame.MOUSEWHEEL:
                scroll_wheel_sensitivity = 50
                if event.y == 1:
                    self.cam.speed = self.cam.speed + scroll_wheel_sensitivity if self.cam.speed + scroll_wheel_sensitivity <= MAX_CAM_SPEED else self.cam.speed
                if event.y == -1:
                    self.cam.speed = self.cam.speed - scroll_wheel_sensitivity if self.cam.speed - scroll_wheel_sensitivity >= MIN_CAM_SPEED else self.cam.speed


if __name__ == '__main__':
    game = Game()
    game.run()
