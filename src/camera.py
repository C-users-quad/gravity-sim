from settings import *

class Camera:
    def __init__(self):
        self.zoom = 1.0

        self.pos = np.array([0.0, 0.0], dtype=np.float32)
        self.pan_speed = 100

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
        self.zoom *= max(MIN_ZOOM, 1.1 ** event_y)

    def update_speed(self, event_y, dt):
        new_speed = self.pan_speed + 100 * event_y * dt
        self.pan_speed = min(MAX_SPEED, max(new_speed, MIN_SPEED))

    def update(self, pressed_keys, dt):
        for key in pressed_keys:
            self.update_pos(key, dt)
