import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import sys
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from os.path import join
import os
import numba
import time
import math

HALF_WORLD_LENGTH = 1_000_000
WINDOW_WIDTH, WINDOW_HEIGHT = 1040, 960
FPS = 120

MIN_ZOOM, MAX_ZOOM = 0.01, 2
MIN_CAM_SPEED, MAX_CAM_SPEED = 10, 1000000
