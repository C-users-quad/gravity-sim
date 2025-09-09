from vispy import app, gloo
import numpy as np
from typing import Literal, Sequence
from numba import njit, prange

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
HALF_WORLD_LENGTH = 10000 # the world is a square with side lengths HALF_WORLD_LENGTH * 2 centered at the origin.

DT = 0.0001 # time between frames in seconds.

MAX_NODES = 100_000

G = 10
N = 100 # num particles
R = 10 # radius of particles
MIN_RADIUS, MAX_RADIUS = 1, 249
CENTRAL_PARTICLE_MASS = 1_000_000_000
ORBITING_PARTICLE_MASS = 1_000

MAX_UNIFORM_DISC_RADIUS = 500

MOVEMENT_KEY_NAMES = ['W', 'A', 'S', 'D']
MAX_ZOOM, MIN_ZOOM = 0.1, 2.0