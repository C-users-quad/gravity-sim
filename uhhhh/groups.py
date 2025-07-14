from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos, zoom):
        # updates the offset to the target positions current coordinates
        self.offset.x = -target_pos[0] + (WINDOW_WIDTH / 2)
        self.offset.y = -target_pos[1] + (WINDOW_HEIGHT / 2)    
        
        other_particles = [particle for particle in self if particle.being_interacted_with == False]
        interacted_particle = [particle for particle in self if particle.being_interacted_with ==  True]
        
        for layer in [other_particles, interacted_particle]:
            for sprite in layer:
                if hasattr(sprite, "is_within_render_distance") and not sprite.is_within_render_distance(target_pos):
                    continue
                
                zoomed_image = pygame.transform.rotozoom(sprite.image, 0, zoom)
                zoomed_rect = zoomed_image.get_frect(center = (sprite.rect.center + self.offset) * zoom)
                
                self.display_surface.blit(zoomed_image, zoomed_rect)
        
