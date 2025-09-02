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

WINDOW_WIDTH, WINDOW_HEIGHT = 1040, 960
FPS = 60

MIN_ZOOM, MAX_ZOOM = 0.1, 2
