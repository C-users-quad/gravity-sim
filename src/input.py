from settings import *
from utils import *
from menu import *


class Input:
    def __init__(self, game):
        self.dragged_particle = None
        self.info_particle = None
        self.particle_menu = None
        self.old_world_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        self.game = game

    def get_input(self, dt):
        """
        Handle user input for dragging, info display, menu toggling, particle deletion, and particle repopulation.
        Args:
            dt (float): Delta time since last frame.
            world_mouse_pos (Vector2): Mouse position in world coordinates.
            particles (pygame.sprite.Group()): All particle sprites.
        """
        world_mouse_pos = (pygame.Vector2(pygame.mouse.get_pos()) - self.game.particles.offset) / self.game.cam.zoom
        delta_mouse_pos = world_mouse_pos - self.old_world_mouse_pos
        
        mouse_presses = pygame.mouse.get_pressed()
        key_just_pressed = pygame.key.get_just_pressed()
        key_held = pygame.key.get_pressed()

        # drag particles with left click
        if mouse_presses[0]:
            if self.dragged_particle:
                # drag the particle
                self.dragged_particle.rect.center = world_mouse_pos
                self.dragged_particle.x = world_mouse_pos.x
                self.dragged_particle.y = world_mouse_pos.y
                self.dragged_particle.v = (world_mouse_pos - self.old_world_mouse_pos) / dt
            else:
                # find what particle (if any) was dragged and label it as the dragged particle
                particle = find_particle(self.game.particles, world_mouse_pos)
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
                self.dragged_particle.v = delta_mouse_pos / dt
                self.dragged_particle = None
                
        # display particle info with right click
        if mouse_presses[2]:
            if not self.info_particle:
                particle = find_particle(self.game.particles, world_mouse_pos)
                if particle:
                    self.info_particle = particle
                    self.info_particle.info = True
            if self.info_particle:
                if not self.info_particle.alive():
                    self.info_particle = None
                    return
                # RMB + LCTRL = camera follows info particle
                if key_held[pygame.K_LCTRL]:
                    particle_pos = self.info_particle.rect.center
                    self.game.cam.set_pos(particle_pos)
        
        # get rid of particle info
        if key_just_pressed[pygame.K_ESCAPE]:
            if self.particle_menu:
                self.particle_menu.exit_menu(self.logprinter, "dont create particle", self.game.cam)
                self.particle_menu = None
            
            elif self.info_particle:
                self.info_particle.info = False
                self.info_particle = None

        # opens + closes particle creation menu
        if key_just_pressed[pygame.K_RETURN]:
            if not self.particle_menu:
                if len(self.game.particles) >= MAX_PARTICLES:
                    self.game.logprinter.print(f"There are too many particles!", type="error")
                    return
                self.particle_menu = ParticleCreationMenu(self.game.font, self.game.manager, (self.game.particles, self.game.particles), self.game.particles)
            else:
                self.info_particle = self.particle_menu.menu_particle
                self.info_particle.info = True
                self.particle_menu.exit_menu(self.game.logprinter, "create particle", self.game.cam)
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
            if len(self.game.particles) >= NUM_PARTICLES:
                self.game.logprinter.print("Theres already enough particles!", type="error")
                return
            num_particles_to_make = NUM_PARTICLES - len(self.game.particles)
            self.game.make_particles(num_particles_to_make)
            self.game.logprinter.print(f"Made {num_particles_to_make} particles!", type="info")

        # sets debug mode on
        if key_just_pressed[pygame.K_PERIOD]:
            self.game.debug = not self.game.debug

        self.old_world_mouse_pos = world_mouse_pos
