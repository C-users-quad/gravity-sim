from settings import *
# from cam import Cam
from sprites import *
# from groups import *


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
        self.old_mouse_pos = pygame.Vector2(self.mouse.get_pos())
        
        # groups
        # self.all_sprites = AllSprites()
        self.all_sprites = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # sprites (camera not in use, if u wanna u can add camm functionality. gotta learn spatial partitioning first tho xd)
        # self.cam = Cam()
        self.font = pygame.font.Font(None, 20)
    
    def get_input(self, dt):
        mouse_presses = self.mouse.get_pressed()
        key_presses = pygame.key.get_pressed()
        mouse_pos = pygame.Vector2(self.mouse.get_pos())
        delta_mouse_pos = mouse_pos - self.old_mouse_pos

        # drag the mouse if its left click
        if mouse_presses[0]:
            if self.dragged_particle:
                # drag the fucking particle
                self.dragged_particle.rect.center = mouse_pos
                self.dragged_particle.v = delta_mouse_pos / dt
            else:
                for particle in self.particles:
                    if particle.rect.collidepoint(mouse_pos):
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
            if mouse_presses[2]:
                if not self.info_particle:
                    for particle in self.particles:
                        if particle.rect.collidepoint(mouse_pos):
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
        for _ in range(10):
            x = randint(0, WINDOW_WIDTH)
            y = randint(0, WINDOW_HEIGHT)
            vx = randint(0, MAX_STARTING_VELOCITY)
            vy = randint(0, MAX_STARTING_VELOCITY)
            mass = randint(1, MAX_STARTING_MASS)
            Particle(x, y, vx, vy, mass, (self.all_sprites, self.particles), self.particles)
        
        while self.on:
            dt = self.clock.tick(self.fps) / 1000
            self.old_mouse_pos = pygame.Vector2(self.mouse.get_pos())
            
            # self.cam.update(dt)
            
            self.event_handler()
            self.all_sprites.update(dt)
            self.get_input(dt)
            
            self.display_surf.fill('#17171a')
            self.all_sprites.draw(self.display_surf)
            self.draw_particle_info()
            
            pygame.display.update()
            
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
