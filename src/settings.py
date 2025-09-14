from vispy import app, gloo, util
from vispy.util.transforms import scale, translate
import numpy as np
from typing import Literal, Sequence
from numba import njit, prange, jit
import math
import time

# general game values
N = 16000 # num orbital particles
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
HALF_WORLD_LENGTH = N * 2 # the world is a square with side lengths HALF_WORLD_LENGTH * 2 centered at the origin.
DT_PHYSICS = 0.033 # time between frames in seconds.

# interpolation related limits
MAX_PHYSICS_UPDATES = 1
MAX_ACCUMULATOR = 0.25

# quadtree
MAX_NODES = 25_000

# particle
G = 15 # gravitational constant
R = 10 # radius of orbital particles
MIN_RADIUS, MAX_RADIUS = 1, 249
CENTRAL_PARTICLE_MASS = 1_000_000_000
ORBITING_PARTICLE_MASS = 1

# uniform disc
MAX_UNIFORM_DISC_RADIUS = N

# cam
MOVEMENT_KEY_NAMES = ['W', 'A', 'S', 'D']
MIN_ZOOM = 1e-8
MIN_SPEED, MAX_SPEED = 1, 5000
