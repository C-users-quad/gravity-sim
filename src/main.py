from settings import *
from utils import *
from cam import Camera
from quadtree import *
from collision import Boundary

NUM_PARTICLES = 1000 # num particles
PARTICLE_RADIUS = 100 # radius of each particle
PARTICLE_MASS = 100 # particle mass
bytes_in_f32 = np.dtype(np.float32).itemsize

# ==========================================
# Initialization
# ==========================================

# pygame initialization
pygame.init()
pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
pygame.display.set_caption("Truly the test of all time")
cam = Camera()
on = True
# opengl initialization
glClearColor(0.0, 0.0, 0.0, 1.0) # sets the color the window becomes when resetting the image between frames
shader_program = get_shader_program(
    join('shaders', 'vertex_shader.glsl'),
    join('shaders', 'fragment_shader.glsl')
)
glUseProgram(shader_program)
resize_viewport(WINDOW_WIDTH, WINDOW_HEIGHT, shader_program)

# ==========================================
# Particle Setup
# ==========================================

# 1. DEFINE UNIT SQUARE
unit_square = np.array([
    [-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], # triangle ono
    [-0.5, -0.5], [-0.5, 0.5], [0.5, 0.5] # triangle two
], dtype=np.float32)

num_square_vertices = 6

# 2. GENERATE PARTICLE ATTRIBUTES FOR N PARTICLES
centers = (np.random.rand(NUM_PARTICLES, 2).astype(np.float32) - 0.5) * 2 * HALF_WORLD_LENGTH
velocities = np.zeros((NUM_PARTICLES, 2), dtype=np.float32)
radii = (np.ones(NUM_PARTICLES, dtype=np.float32) * PARTICLE_RADIUS).reshape(NUM_PARTICLES, 1)
colors = np.ones((NUM_PARTICLES, 3), dtype=np.float32)
masses = (np.ones(NUM_PARTICLES, dtype=np.float32) * PARTICLE_MASS).reshape(NUM_PARTICLES, 1)

# [cx, cy, vx, vy, r, m]
particles = np.hstack([centers, velocities, radii, masses])

# 3. STORE ATTRIBUTES IN GPU BUFFERS

# each vertex has the data [centerx, centery, radius, r, g, b]
particle_data_for_shaders = np.hstack([centers, radii, colors]).astype(np.float32) 

# vao creation and binding
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# vbo creation and binding
vbo_unit_square = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo_unit_square)
glBufferData(GL_ARRAY_BUFFER, unit_square.nbytes, unit_square, GL_STATIC_DRAW) # static draw tells opengl that this data wont be manipulated
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, bytes_in_f32*2, ctypes.c_void_p(0))

# vbo particle
vbo_particle = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo_particle)
glBufferData(GL_ARRAY_BUFFER, particle_data_for_shaders.nbytes, particle_data_for_shaders, GL_DYNAMIC_DRAW)

# attributes [centerx, centery, radius, r, g, b]
stride = bytes_in_f32*6
glEnableVertexAttribArray(1) # center: centerx, centery
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
glVertexAttribDivisor(1, 1)

glEnableVertexAttribArray(2) # radius: radius
glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(bytes_in_f32*2))
glVertexAttribDivisor(2, 1)

glEnableVertexAttribArray(3) # color: r, g, b
glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(bytes_in_f32*3))
glVertexAttribDivisor(3, 1)

# ==========================================
# Main Loop Functions
# ==========================================

def quit():
    glDeleteBuffers(2, (vbo_unit_square,vbo_particle))
    glDeleteVertexArrays(1, (vao,))
    glDeleteProgram(shader_program)
    pygame.quit()
    sys.exit()

def event_handler():
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global on
            on = False

        if event.type == pygame.VIDEORESIZE:
            global WINDOW_WIDTH, WINDOW_HEIGHT
            resize_viewport(event.w, event.h, shader_program)
            WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
            
        if event.type == pygame.MOUSEWHEEL:
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                cam.update_speed(event.y)
            else:
                cam.update_zoom(event.y)   

# ==========================================
# Main Loop
# ==========================================

def run():
    while on:
        dt = 0.01
        
        # update phase

        event_handler()
        cam.update(dt)
        pass_in_uniforms(shader_program, WINDOW_WIDTH, WINDOW_HEIGHT, cam.zoom, cam.pos)

        # drawing phase
        glClear(GL_COLOR_BUFFER_BIT)
        glBindVertexArray(vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, num_square_vertices, NUM_PARTICLES)

        pygame.display.flip()
    quit()

if __name__ == "__main__":
    run()
