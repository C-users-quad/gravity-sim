from settings import *
from particle import *
from utils import *


class ParticleCreationMenu:
    def __init__(self, font, ui_manager, groups, particles, display):
        self.display = display
        self.font = font
        self.ui_manager = ui_manager
        
        self.values = ["x", "y", "mass", "vx", "vy", "density"]
        
        # calculates the positions for the ui elements
        win_w, win_h = self.display.get_size()
        mid_screen_width = win_w / 2
        mid_screen_height = win_h / 2
        
        self.circle_radius = mid_screen_width - (mid_screen_width / 4)
        half = len(self.values) // 2
        
        self.vertical_spacing = self.circle_radius / half
        self.padding = 4
        
        y_vals_half = [
            mid_screen_height - self.vertical_spacing,
            mid_screen_height,
            mid_screen_height + self.vertical_spacing
        ]
        y_values = y_vals_half + y_vals_half
        
        self.points = []
        for i, y in enumerate(y_values):
            if i < half:
                x = mid_screen_width - math.sqrt(self.circle_radius**2 - (y - mid_screen_height)**2)
            else:
                x = mid_screen_width + math.sqrt(self.circle_radius**2 - (y - mid_screen_height)**2)
            self.points.append(pygame.FRect(x, y, 0, 0)) 
        
        self.input_boxes = []
        self.input_box_width = 60
        
        # default values for when an invalid value is inputted or input box is left empty
        self.default_mass = 1000
        self.default_density = 1
        self.default_x = 0
        self.default_y = 0
        self.default_vx = 0
        self.default_vy = -10
        
        self.default_values = [self.default_x, self.default_y, self.default_mass, self.default_vx, self.default_vy, self.default_density]

        # Create input boxes with height matching label text height
        for i, point in enumerate(self.points):
            # Get label text height
            text_surf = self.font.render(self.values[i], True, "white")
            text_height = text_surf.get_height()
            text_width = text_surf.get_width()
            
            height_adjustment = 6
            
            # Input box rect positioned relative to label center
            input_rect = pygame.FRect(
                0, # dummy positions, repositioned in self.draw_labels()
                0,
                self.input_box_width,
                text_height + height_adjustment
            )
            input_box = pygame_gui.elements.UITextEntryLine(
                relative_rect=input_rect,
                manager=self.ui_manager
            )

            input_box.set_text(str(self.default_values[i]))
            self.input_boxes.append(input_box)

        self.menu_particle = Particle(mid_screen_width, mid_screen_height, 0, 0, self.default_mass, self.default_density, groups, particles)
        self.menu_particle.in_menu = True

    def draw_labels(self):
        for i, value in enumerate(self.values):
            # text rect dimensions and setup
            text_surf = self.font.render(value, True, "black")
            text_rect = text_surf.get_frect()
            text_rect_width, text_rect_height = text_rect.size
            
            # input rect dimensions
            input_box = self.input_boxes[i]
            input_box_width, input_box_height = input_box.relative_rect.size

            # Background rect
            rect_width = text_rect_width + input_box_width + self.padding * 3
            rect_height = text_rect.height + self.padding * 2
            rect_surf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
            bg_rect = rect_surf.get_frect(center = (self.points[i].x, self.points[i].y))
            rect_surf.fill(BUTTON_COLOR)

            # adjust text rect and input rect's positions
            text_rect.left = bg_rect.left + self.padding
            text_rect.top = bg_rect.top + self.padding
            input_rect_left = text_rect.right + self.padding
            input_rect_top = bg_rect.centery - input_box.relative_rect.height / 2
            input_box.set_relative_position((input_rect_left, input_rect_top))
            
            self.display.blit(rect_surf, bg_rect)
            self.display.blit(text_surf, text_rect)

            # border
            pygame.draw.rect(self.display, BORDER_COLOR, bg_rect, 1, 2)
            
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
        
        self.menu_particle.radius = calculate_radius(mass, density)
        self.menu_particle.update_color()
        self.menu_particle.update_sprite()
        
        display_surf = pygame.display.get_surface()
        display_surf.blit(self.menu_particle.image, self.menu_particle.rect)
    
    def limit_values(self):
        # positional values (x, y)
        try:
            x_input = int(self.input_boxes[0].get_text())
            if not -HALF_WORLD_WIDTH < x_input < HALF_WORLD_WIDTH:
                self.input_boxes[0].set_text(str(self.default_x))
        except ValueError:
            text = self.input_boxes[0].get_text()
            if text and not text[0] == '-':
                self.input_boxes[0].set_text('')

        try:
            y_input = int(self.input_boxes[1].get_text())
            if not -HALF_WORLD_HEIGHT < y_input < HALF_WORLD_HEIGHT:
                self.input_boxes[1].set_text(str(self.default_y))
        except ValueError:
            text = self.input_boxes[1].get_text()
            if text and not text[0] == '-':
                self.input_boxes[1].set_text('')

        # velocity values (vx, vy)
        try:
            vx_input = int(self.input_boxes[3].get_text())
        except ValueError:
            text = self.input_boxes[3].get_text()
            if text and not text[0] == '-':
                self.input_boxes[3].set_text('')
        try:
            vy_input = int(self.input_boxes[4].get_text())
        except ValueError:
            text = self.input_boxes[4].get_text()
            if text and not text[0] == '-':
                self.input_boxes[4].set_text('')

        # mass and density
        try:
            mass_input = int(self.input_boxes[2].get_text())
            if mass_input <= 0:
                self.input_boxes[2].set_text(str(self.default_values[2]))
        except ValueError:
            text = self.input_boxes[2].get_text()
            if text and not text[0] == '-':
                self.input_boxes[2].set_text('')
        
        try:
            density_input = int(self.input_boxes[5].get_text())
            if density_input <= 0:
                self.input_boxes[5].set_text(str(self.default_values[5]))
        except ValueError:
            text = self.input_boxes[5].get_text()
            if text and not text[0] == '-':
                self.input_boxes[5].set_text('')
    
    def exit_menu(self):
        # get particle values from input boxes
        pos = (int(self.input_boxes[0].get_text()), int(self.input_boxes[1].get_text()))
        velocity = (int(self.input_boxes[3].get_text()), int(self.input_boxes[4].get_text()))
        mass = int(self.input_boxes[2].get_text())
        density = int(self.input_boxes[5].get_text())

        # add values to the menu particle
        self.menu_particle.rect.center = pos
        self.menu_particle.v = pygame.Vector2(velocity)
        self.menu_particle.mass = mass
        self.menu_particle.density = density

        # update particle status
        self.menu_particle.in_menu = False
    
    def draw_border(self):
        rect = self.display.get_rect().inflate(-20, -20)
        pygame.draw.rect(self.display, BORDER_COLOR, rect, 5, 5)

    def update(self):
        self.draw_labels()
        self.limit_values()
        self.draw_particle()
        self.draw_border()
