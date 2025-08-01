from settings import *
from sprites import *
from utils import *


class ParticleCreationMenu:
    def __init__(self, display, font, ui_manager, groups, particles):
        self.display = display
        self.font = font
        self.ui_manager = ui_manager
        
        self.values = ["x", "y", "mass", "vx", "vy", "density"]
        
        mid_screen_width = WINDOW_WIDTH / 2
        mid_screen_height = WINDOW_HEIGHT / 2
        
        self.circle_radius = mid_screen_width - (mid_screen_width / 4)
        half = len(self.values) // 2
        
        self.spacing = self.circle_radius / half
        self.padding = 4
        
        y_vals_half = [
            mid_screen_height - self.spacing,
            mid_screen_height,
            mid_screen_height + self.spacing
        ]
        y_values = y_vals_half + y_vals_half
        
        self.points = []
        for i, y in enumerate(y_values):
            if i < half:
                x = mid_screen_width - math.sqrt(self.circle_radius**2 - (y - mid_screen_height)**2)
            else:
                x = mid_screen_width + math.sqrt(self.circle_radius**2 - (y - mid_screen_height)**2)
            self.points.append(pygame.FRect(x, y, 0, 0))  # Use FRect for positions (width/height 0 for now)
        
        self.input_boxes = []
        self.input_box_width = 60
        
        # Create input boxes with height matching label text height
        for i, point in enumerate(self.points):
            # Get label text height
            label_surf = self.font.render(self.values[i], True, "white")
            text_height = label_surf.get_height() + 5
            text_width = label_surf.get_width()
            
            offset = (text_width / 2) + self.padding
            
            # Input box rect positioned relative to label center
            input_rect = pygame.FRect(
                point.x + offset,
                point.y - text_height / 2,
                self.input_box_width,
                text_height
            )
            
            input_box = pygame_gui.elements.UITextEntryLine(
                relative_rect=input_rect,
                manager=self.ui_manager
            )
            self.input_boxes.append(input_box)
            
        self.default_mass = 100
        self.default_density = 1
        self.default_x = 0
        self.default_y = 0
        self.default_vx = randint(MAX_STARTING_VELOCITY)
        self.default_vy = randint(MAX_STARTING_VELOCITY)
        
        self.menu_particle = Particle(mid_screen_width, mid_screen_height, 0, 0, self.default_mass, self.default_density, groups, particles)
        self.menu_particle.in_menu = True

    def draw_labels(self):
        for i, value in enumerate(self.values):
            text_surf = self.font.render(value, True, "white")
            text_rect = text_surf.get_frect(center=(self.points[i].x, self.points[i].y))
            
            # Background rect
            rect_width = text_rect.width + self.padding * 2 + self.input_box_width
            rect_height = text_rect.height + self.padding * 2
            rect_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
            rect_surf.fill(INFO_RECT_COLOR)
            bg_rect = rect_surf.get_frect(center=(self.points[i].x + self.input_box_width / 2, self.points[i].y))
            
            self.display.blit(rect_surf, bg_rect)
            self.display.blit(text_surf, text_rect)        
            
    def draw_particle(self):
        try:
            mass = int(self.input_boxes[2].get_text()) 
        except ValueError:
            mass = self.default_mass
            
        try:
            density = int(self.input_boxes[5].get_text())
        except ValueError:
            density = self.default_density
            
        self.menu_particle.mass = mass
        self.menu_particle.density = density
        print(self.menu_particle.mass, self.menu_particle.density)
        
        self.menu_particle.radius = calculate_radius(mass, density)
        self.menu_particle.update_color()
        self.menu_particle.update_sprite()
        
        display_surf = pygame.display.get_surface()
        display_surf.blit(self.menu_particle.image, self.menu_particle.rect)
    
    def limit_values(self):
        # positional values (x, y)
        try:
            x_input = int(self.input_boxes[0].get_text())
        except ValueError:
            x_input = self.default_x
        try:
            y_input = int(self.input_boxes[1].get_text())
        except ValueError:
            y_input = self.default_y
        if not -HALF_WORLD_WIDTH < x_input < HALF_WORLD_WIDTH:
            self.input_boxes[0].set_text(self.default_x)
        if not -HALF_WORLD_HEIGHT < y_input < HALF_WORLD_HEIGHT:
            self.input_boxes[1].set_text(self.default_y)
            
        # velocity values (vx, vy)
        
    
    def update(self):
        self.draw_labels()
        self.limit_values()
        self.draw_particle()
        