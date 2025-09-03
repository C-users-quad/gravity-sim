from settings import *
from utils import *
from cam import Camera
from quadtree import *

NUM_PARTICLES = 100_000 # num particles
PARTICLE_RADIUS = 100 # radius of each particle
PARTICLE_MASS = 100 # particle mass
bytes_in_f32 = np.dtype(np.float32).itemsize

# ==========================================
# Initialization
# ==========================================

# pygame initialization
pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                pygame.GL_CONTEXT_PROFILE_COMPATIBILITY)
pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
pygame.display.set_caption("Truly the test of all time")
cam = Camera()
clock = pygame.time.Clock()
on = True
# opengl initialization
glClearColor(0.0, 0.0, 0.0, 1.0) # sets the color the window becomes when resetting the image between frames
particle_shader = get_shader_program(
    join('shaders', 'particle_vertex_shader.glsl'),
    join('shaders', 'particle_fragment_shader.glsl')
)
# basic_shader = get_shader_program(
#     join('shaders', 'basic_vertex_shader.glsl'),
#     join('shaders', 'basic_fragment_shader.glsl')
# )
glUseProgram(particle_shader)
resize_viewport(WINDOW_WIDTH, WINDOW_HEIGHT)
initialize_opengl_world_coord_system()

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
particle_vao = glGenVertexArrays(1)
glBindVertexArray(particle_vao)

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
# Quadtree Setup
# ==========================================

node_bounds = np.zeros((MAX_NODES, 4), dtype=np.float32) # (left, top, width, height)
node_particle_indices = -np.ones((MAX_NODES, CAPACITY), np.int32) # particle indices
node_children = -np.ones((MAX_NODES, 4), dtype=np.int32) # node children indices
node_counts = np.zeros(MAX_NODES, dtype=np.int32) # number of particles in node

node_mass = np.zeros(MAX_NODES, dtype=np.float32) # combined mass of particles in node
node_com = np.zeros((MAX_NODES, 2), dtype=np.float32) # (x, y) center of mass positions for nodes
node_s2 = np.zeros(MAX_NODES, dtype=np.float32)

free_nodes = np.arange(1, MAX_NODES, 1, dtype=np.int32) # root node = 0
free_count = MAX_NODES - 1 # its minus one cus root node is always in use.

# vao+vbo setup for visualization

# ==========================================
# Main Loop Functions
# ==========================================

def quit():
    glDeleteBuffers(2, (vbo_unit_square,vbo_particle))
    glDeleteVertexArrays(1, (particle_vao,))
    glDeleteProgram(particle_shader)
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
            resize_viewport(event.w, event.h)
            WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
            
        if event.type == pygame.MOUSEWHEEL:
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                cam.update_speed(event.y)
            else:
                cam.update_zoom(event.y)   

def update_quadtree(node_bounds, node_counts, node_particle_indices, node_children, free_nodes, free_count, node_mass, node_com, node_s2):
    free_count = clear_quadtree(node_bounds, node_particle_indices, node_children, node_counts, node_mass, node_com, node_s2, free_nodes)
    for i in range(NUM_PARTICLES):
        free_count = insert(0, i, particles, node_bounds, node_counts, node_particle_indices, node_children, free_nodes, free_count)

def draw_particles():
    glUseProgram(particle_shader)
    glBindVertexArray(particle_vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_particle)
    glBufferSubData(GL_ARRAY_BUFFER, 0, particle_data_for_shaders.nbytes, particle_data_for_shaders)
    glDrawArraysInstanced(GL_TRIANGLES, 0, num_square_vertices, NUM_PARTICLES)

def draw_quadtree_lines():
    glUseProgram(basic_shader)
    lines = quadtree_bounds_to_lines(node_bounds, node_children)

# ==========================================
# Main Loop
# ==========================================

def run():
    global free_count
    while on:
        dt = clock.tick(FPS) / 1000
        print(clock.get_fps())
        
        # update phase
        update_quadtree(node_bounds, node_counts, node_particle_indices, node_children, free_nodes, free_count, node_mass, node_com, node_s2)
        event_handler()
        cam.update(dt)
        pass_in_uniforms(particle_shader, WINDOW_WIDTH, WINDOW_HEIGHT, cam.zoom, cam.pos)

        # drawing phase
        glClear(GL_COLOR_BUFFER_BIT)
        draw_particles()
        # draw_quadtree_lines()

        pygame.display.flip()
    quit()

if __name__ == "__main__":
    run()
