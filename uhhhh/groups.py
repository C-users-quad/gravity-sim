from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, cam):
        target_pos = cam.pos
        zoom = cam.zoom
        # updates the offset to the target positions current coordinates
        self.offset.x = (-target_pos[0] * zoom) + (WINDOW_WIDTH / 2)
        self.offset.y = (-target_pos[1] * zoom) + (WINDOW_HEIGHT / 2)    
        
        other_particles = [particle for particle in self if particle.being_dragged == False]
        dragged_particle = [particle for particle in self if particle.being_dragged ==  True]
    
        other_particles.sort(key = lambda particle: particle.mass)
        
        for layer in [other_particles, dragged_particle]:
            for sprite in layer:
                if hasattr(sprite, "is_within_render_distance") and not sprite.is_within_render_distance(cam):
                    continue
                
                zoomed_image = pygame.transform.rotozoom(sprite.image, 0, zoom)
                zoomed_rect = zoomed_image.get_frect(center = (sprite.rect.centerx * zoom, sprite.rect.centery * zoom) + self.offset)
                
                self.display_surface.blit(zoomed_image, zoomed_rect)
        
