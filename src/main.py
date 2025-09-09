from settings import *
from shaders import vertex_shader, fragment_shader
from camera import Camera
from particle import make_particles, update_particles, get_args_for_particle_update, colors, radii, positions, masses
from quadtree import update_quadtree, get_args_for_quadtree_update

app.use_app('PyQt6')

class Canvas(app.Canvas):
    """
    vispy equivalent of a game class you would use in pygame games.
    on_draw: a function that is used for the drawing phase.
    on_timer: a function that updates the game state every frame.
    """
    def __init__(self):
        """initializes and shows the window with a size and title."""

        # === Initialize Window ===
        super().__init__(size=(WINDOW_WIDTH, WINDOW_HEIGHT), title="vispy canvas", keys='interactive')

        # === Initialize Camera ===
        self.cam = Camera()
        self.pressed_keys = set() # used to store key presses for continuous cam panning.

        # === Initialize Particles ===
        make_particles()

        # === Initialize Gloo ===
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.update_program()

        # === Initialize Timer ===
        self.timer = app.timer.Timer(interval=DT, connect=self.on_timer, start=True)

        self.show()

    def update_program(self):
        self.program['a_color'] = colors
        self.program['a_pos'] = positions
        self.program['a_radius'] = radii
        self.program['u_HALF_WORLD_LENGTH'] = HALF_WORLD_LENGTH
        self.program['u_CamPos'] = self.cam.pos
        self.program['u_CamZoom'] = self.cam.zoom

    def on_timer(self, event):
        """
        update phase goes here. this runs every interval seconds, as defined in self.timer.
        """
        self.dt = event.dt
        for key in self.pressed_keys:
            self.cam.update(key, self.dt)
        update_particles(*get_args_for_particle_update(self.dt))
        update_quadtree(*get_args_for_quadtree_update(positions, masses))
        self.update_program()
        self.update()
        print(HALF_WORLD_LENGTH)
        print(np.max(np.abs(positions)))

    def on_draw(self, event):
        """drawing phase updates go here"""
        self.context.clear('black')
        self.program.draw('points') # CRITICAL. DRAWS THE PARTICLES.

    def on_key_press(self, event):
        """use event.key.name to get the key pressed."""
        if event.key.name in MOVEMENT_KEY_NAMES:
            self.pressed_keys.add(event.key.name)
    
    def on_key_release(self, event):
        if event.key.name in MOVEMENT_KEY_NAMES:
            self.pressed_keys.discard(event.key.name)

    def on_mouse_wheel(self, event):
        self.cam.update_zoom(event.delta[1], self.dt)
    

if __name__ == "__main__":
    c = Canvas()
    app.run()
