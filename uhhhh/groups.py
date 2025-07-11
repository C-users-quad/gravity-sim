from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        # # updates the offset to the target positions current coordinates
        # self.offset.x = -target_pos[0] + (WINDOW_WIDTH / 2)
        # self.offset.y = -target_pos[1] + (WINDOW_HEIGHT / 2)    
        
        other_particles = [particle for particle in self if particle.being_interacted_with == False]
        interacted_particle = [particle for particle in self if particle.being_interacted_with ==  True]
        particle_info_rects = [sprite for sprite in self if hasattr(sprite, "particle_info_rectangle")]
        
        for layer in [other_particles, interacted_particle, particle_info_rects]:
            for sprite in layer:
                self.display_surface.blit(sprite.image, sprite.rect.center + self.offset)
