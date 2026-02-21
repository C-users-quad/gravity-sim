from settings import *

class Camera:
    def __init__(self):
        self.zoom = 1.0

        self.pos = np.array([0.0, 0.0], dtype=np.float32)
        self.pan_speed = 100

    def update_pos(self, key, dt):
        if key == MOVEMENT_KEY_NAMES[0]: # up
            self.pos[1] -= self.pan_speed * dt
        elif key == MOVEMENT_KEY_NAMES[1]: # left
            self.pos[0] -= self.pan_speed * dt
        elif key == MOVEMENT_KEY_NAMES[2]: # down
            self.pos[1] += self.pan_speed * dt
        elif key == MOVEMENT_KEY_NAMES[3]: # right
            self.pos[0] += self.pan_speed * dt

    def update_zoom(self, event_y):
        self.zoom *= max(MIN_ZOOM, 1.1 ** event_y)

    def update_speed(self, event_y, dt):
        self.pan_speed *= 1.1 ** event_y
        self.pan_speed = min(MAX_SPEED, max(self.pan_speed, MIN_SPEED))

    def update(self, pressed_keys, dt):
        for key in pressed_keys:
            self.update_pos(key, dt)
