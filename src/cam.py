from settings import *

class Camera:
    def __init__(self):
        self.pos = np.array([0, 0], dtype=np.float32)
        self.zoom = 0

    def local_to_world(self):
        x, y = self.pos

