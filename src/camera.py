from settings import *

class Camera:
    def __init__(self):
        self.zoom = 1.0
        self.zoom_speed = 0.2

        self.pos = np.array([0.0, 0.0], dtype=np.float32)
        self.pan_speed = 10

    def update_pos(self, key, dt):
        if key == "W": # up
            self.pos[1] -= self.pan_speed * dt
        elif key == "A": # left
            self.pos[0] -= self.pan_speed * dt
        elif key == "S": # down
            self.pos[1] += self.pan_speed * dt
        elif key == "D": # right
            self.pos[0] += self.pan_speed * dt

    def update_zoom(self, event_y):
        self.zoom += self.zoom_speed * event_y

    def update(self, key, dt):
        self.update_pos(key, dt)