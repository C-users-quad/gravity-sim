from settings import *
from shaders import vertex_shader, fragment_shader
from camera import Camera
from particle import (make_particles, update_particles, get_args_for_particle_update, 
    colors, radii, positions, masses, old_positions)
from quadtree import update_quadtree, get_args_for_quadtree_update
from utils import interpolate

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
        super().__init__(size=(WINDOW_WIDTH, WINDOW_HEIGHT), title="n-body", keys='interactive')

        # === Initialize Camera ===
        self.cam = Camera()
        self.pressed_keys = set() # used to store key presses for continuous cam panning.

        # === Initialize Particles ===
        make_particles()

        # === Initialize Quadtree ===
        update_quadtree(*get_args_for_quadtree_update(positions, masses))

        # === Initialize Gloo ===
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.update_program(positions)
        self.program['a_color'] = colors
        self.program['a_radius'] = radii

        # === Initialize Timer ===
        self.timer = app.timer.Timer(interval=0, connect=self.on_timer, start=True)
        self.accumulator = 0.0
        self.show()

    def update_program(self, interp_positions):
        self.program['a_pos'] = interp_positions
        self.program['u_CamPos'] = self.cam.pos
        self.program['u_CamZoom'] = self.cam.zoom
        self.program['u_WindowSize'] = self.size

    def on_timer(self, event):
        """
        update phase goes here. this runs every interval seconds, as defined in self.timer.
        """
        self.dt = event.dt
        self.cam.update(self.pressed_keys, self.dt)    

        self.accumulator += self.dt
        self.accumulator = min(self.accumulator, MAX_ACCUMULATOR)
        np.copyto(old_positions, positions)
        physics_update_count = 0
        while self.accumulator >= DT_PHYSICS and physics_update_count <= MAX_PHYSICS_UPDATES:
            update_particles(*get_args_for_particle_update(DT_PHYSICS))
            self.accumulator -= DT_PHYSICS
            physics_update_count += 1
        update_quadtree(*get_args_for_quadtree_update(positions, masses))
        self.update_program(interpolate(self.accumulator, positions, old_positions))
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
        mods = event.modifiers
        if 'Control' in mods:
            self.cam.update_speed(event.delta[1], self.dt)
        else:
            self.cam.update_zoom(event.delta[1])

if __name__ == "__main__":
    c = Canvas()
    app.run()
