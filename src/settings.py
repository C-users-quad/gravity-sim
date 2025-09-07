from vispy import app, gloo
import numpy as np
from typing import Literal, Sequence
from numba import njit, prange

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
HALF_WORLD_LENGTH = 1000 # the world is a square with side lengths HALF_WORLD_LENGTH * 2 centered at the origin.

DT = 0.01 # time between frames in seconds.

G = 1
N = 10 # num particles
R = 10 # radius of particles
MIN_RADIUS, MAX_RADIUS = 1, 249
CENTRAL_PARTICLE_MASS = 1_000_000
ORBITING_PARTICLE_MASS = 1

MAX_UNIFORM_DISC_RADIUS = 100

MOVEMENT_KEY_NAMES = ['W', 'A', 'S', 'D']