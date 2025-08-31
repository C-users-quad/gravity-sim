from settings import *
from utils import *

N = 10 # num particles
r = 100 # radius of each particle
bytes_in_f32 = np.dtype(np.float32).itemsize

# ==========================================
# Initialization
# ==========================================

# pygame initialization
pygame.init()
pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
pygame.display.set_caption("Truly the test of all time")
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
centers = np.random.rand(N, 2).astype(np.float32) * [WINDOW_WIDTH, WINDOW_HEIGHT]
velocities = np.zeros((N, 2), dtype=np.float32)
radii = np.ones(N, dtype=np.float32) * r
colors = np.ones((N, 3), dtype=np.float32)

# 3. STORE ATTRIBUTES IN GPU BUFFERS

# Shape (N, 8)
# each vertex has the data [centerx, centery, vx, vy, radius, r, g, b]
particles_data = np.hstack([centers, velocities, radii.reshape(N, 1), colors]).astype(np.float32)

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
glBufferData(GL_ARRAY_BUFFER, particles_data.nbytes, particles_data, GL_DYNAMIC_DRAW)

# attributes [centerx, centery, vx, vy, radius, r, g, b]
stride = bytes_in_f32*8
glEnableVertexAttribArray(1) # center: centerx, centery
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
glVertexAttribDivisor(1, 1)

glEnableVertexAttribArray(2) # velocity: vx, vy
glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(bytes_in_f32*2))
glVertexAttribDivisor(2, 1)

glEnableVertexAttribArray(3) # radius: radius
glVertexAttribPointer(3, 1, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(bytes_in_f32*4))
glVertexAttribDivisor(3, 1)

glEnableVertexAttribArray(4) # color: r, g, b
glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(bytes_in_f32*5))
glVertexAttribDivisor(4, 1)

# ==========================================
# Main Loop Functions
# ==========================================

def quit():
    glDeleteBuffers(2, (vbo_unit_square,vbo_particle))
    glDeleteVertexArrays(1, (vao,))
    pygame.quit()
    sys.exit()

def event_handler():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global on
            on = False

        if event.type == pygame.VIDEORESIZE:
            resize_viewport(event.w, event.h, shader_program)

# ==========================================
# Main Loop
# ==========================================

def run():
    while on:
        # update phase
        event_handler()

        # drawing phase
        glClear(GL_COLOR_BUFFER_BIT)
        glBindVertexArray(vao)
        glDrawArraysInstanced(GL_TRIANGLES, 0, num_square_vertices, N)

        pygame.display.flip()
    quit()

run() # program entrypoint
