from settings import *
from shaders import vertex_shader, fragment_shader
from camera import Camera

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
        """
        note for self: create a function called make_particles in a separate file
        what it does:
            - initializes positions in a uniform disc
            - initializes velocity
            - stores positions and velocities in numpy arrays with shape (N, num_attributes)
        """
        # pos = make_particles(N)
        color = np.ones((N, 3), dtype=np.float32) # white.
        pos = np.zeros((N, 2), dtype=np.float32) # temp, delete this once u implement make_particles which returns np.array of pos.
        radius = np.ones(N, dtype=np.float32) * 10

        # === Initialize Gloo ===
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.program['a_color'] = color
        self.program['a_pos'] = pos
        self.program['a_radius'] = radius
        self.program['u_HALF_WORLD_LENGTH'] = HALF_WORLD_LENGTH

        # === Initialize Timer ===
        self.timer = app.timer.Timer(interval=DT, connect=self.on_timer, start=True)

        self.show()

    def update_program(self):
        self.program['u_CamPos'] = self.cam.pos
        self.program['u_CamZoom'] = self.cam.zoom

    def on_timer(self, event):
        """
        update phase goes here. this runs every interval seconds, as defined in self.timer.
        usual structure: 
            - get dt from event.dt, which is returned by self.timer every time it calls this function.
            - do your updates.
            - call self.update() which implicitly runs self.on_draw(). dont call self.on_draw() directly; breaks game.
        """
        dt = event.dt
        for key in self.pressed_keys:
            self.cam.update(key, dt)
        self.update_program()
        self.update()

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
        self.cam.update_zoom(event.delta[1])
    

if __name__ == "__main__":
    c = Canvas()
    app.run()
