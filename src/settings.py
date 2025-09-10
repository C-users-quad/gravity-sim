from vispy import app, gloo, util
from vispy.util.transforms import scale, translate
import numpy as np
from typing import Literal, Sequence
from numba import njit, prange
import math
from OpenGL.GL import GL_PROGRAM_POINT_SIZE

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
HALF_WORLD_LENGTH = 10000 # the world is a square with side lengths HALF_WORLD_LENGTH * 2 centered at the origin.

DT = 0.01 # time between frames in seconds.

MAX_NODES = 100_000

G = 10
N = 1000 # num particles
R = 10 # radius of particles
MIN_RADIUS, MAX_RADIUS = 1, 249
CENTRAL_PARTICLE_MASS = 1_000_000
ORBITING_PARTICLE_MASS = 1

MAX_UNIFORM_DISC_RADIUS = 3000

MOVEMENT_KEY_NAMES = ['W', 'A', 'S', 'D']
MIN_ZOOM, MAX_ZOOM = 0.1, 2.0
MIN_SPEED, MAX_SPEED = 10, 1000