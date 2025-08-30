import pygame
from OpenGL.GL import *
import sys
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from os.path import join
import os

WINDOW_WIDTH, WINDOW_HEIGHT = 1040, 960
FPS = 60