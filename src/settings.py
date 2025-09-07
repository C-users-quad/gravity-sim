from vispy import app, gloo
import numpy as np

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
HALF_WORLD_LENGTH = 1000 # the world is a square with side lengths HALF_WORLD_LENGTH * 2 centered at the origin.

DT = 0.01 # time between frames in seconds.
N = 1 # num particles

MOVEMENT_KEY_NAMES = ['W', 'A', 'S', 'D']