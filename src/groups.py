from settings import *
if TYPE_CHECKING:
    from particle import Particle
    from cam import Cam

class ParticleDrawing(pygame.sprite.Group):
    """
    Custom sprite group for managing and drawing particles with camera offset and zoom.
    """
    def __init__(self):
        """
        Initialize the AllSprites group and set up display surface and offset.
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, particles_in_render: Sequence["Particle"], cam: "Cam"):
        """
        Draw all particles in the group, applying camera offset and zoom.
        Sprites being dragged are drawn on top of others.
        Args:
            particles_in_render: particles in render distance.
            cam: Camera object for position and zoom.
        """
        target_pos = cam.pos
        zoom = cam.zoom
        # updates the offset to the target positions current coordinates
        win_w, win_h = self.display_surface.get_size()
        self.offset.x = (-target_pos[0] * zoom) + (win_w / 2)
        self.offset.y = (-target_pos[1] * zoom) + (win_h / 2)    
        
        other_particles = [particle for particle in particles_in_render if hasattr(particle, 'being_dragged') and particle.being_dragged == False]
        dragged_particle = [particle for particle in particles_in_render if hasattr(particle, 'being_dragged') and particle.being_dragged ==  True]
        
        for layer in [other_particles, dragged_particle]:
            for sprite in layer:
                if not sprite.alive():
                    continue
                
                zoomed_image = pygame.transform.rotozoom(sprite.image, 0, zoom)
                zoomed_rect = zoomed_image.get_frect(center = (sprite.rect.centerx * zoom, sprite.rect.centery * zoom) + self.offset)
                
                self.display_surface.blit(zoomed_image, zoomed_rect)
