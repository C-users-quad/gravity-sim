from settings import *
from collision import point_in_boundary

# treat -1 like none gng
MAX_LEVEL = 7
CAPACITY = 64
THETA = 0.75
boundaries      = -np.ones((MAX_NODES, 4),        dtype=np.float32) # [left, top, width, height]
particles       = -np.ones((MAX_NODES, CAPACITY), dtype=np.int32) # indices of particles in node
num_p_in_nodes  =  np.zeros(MAX_NODES,            dtype=np.int32)
children        = -np.ones((MAX_NODES, 4),        dtype=np.int32) # node indices in order of NW, NE, SW, SE
masses          = -np.ones((MAX_NODES),           dtype=np.float32)
centers_of_mass = -np.ones((MAX_NODES, 2),        dtype=np.float32)
s2              = -np.ones((MAX_NODES),           dtype=np.float32) # s in s2/d2 < theta2 check for barnes hut queries.
next_available_index = 1

@njit
def calculate_CoM(node_index: int, tree_masses: np.ndarray, p_masses: np.ndarray, particles: np.ndarray,
                  centers_of_mass: np.ndarray, children: np.ndarray, num_p_in_nodes: np.ndarray, p_positions: np.ndarray):
    num_p_in_node = num_p_in_nodes[node_index]

    if children[node_index, 0] == -1:  # leaf node
        mass_sum = 0.0
        cx = 0.0
        cy = 0.0
        for i in range(num_p_in_node):
            idx = particles[node_index, i]
            m = p_masses[idx]
            mass_sum += m
            cx += m * p_positions[idx, 0]
            cy += m * p_positions[idx, 1]
        if mass_sum > 0:
            centers_of_mass[node_index, 0] = cx / mass_sum
            centers_of_mass[node_index, 1] = cy / mass_sum
        tree_masses[node_index] = mass_sum
        return centers_of_mass[node_index], tree_masses[node_index]
    
    for c in children[node_index]:
        cx, cy, mass = calculate_CoM(c, tree_masses, p_masses, particles, 
                                     centers_of_mass, children, num_p_in_nodes, p_positions)
        tree_masses[node_index] += mass
        centers_of_mass[node_index, 0] += mass * cx
        centers_of_mass[node_index, 1] += mass * cy
    if tree_masses[node_index] != -1:
        centers_of_mass[node_index, 0] /= tree_masses[node_index]
        centers_of_mass[node_index, 1] /= tree_masses[node_index]

    return centers_of_mass[node_index], tree_masses[node_index]

@njit
def query_bh():
    pass

@njit
def clear(boundaries: np.ndarray, particles: np.ndarray, num_p_in_nodes: np.ndarray, children: np.ndarray,
           masses: np.ndarray, centers_of_mass: np.ndarray, s2: np.ndarray, next_available_index: int
    ) -> None:
    boundaries.fill(-1)
    particles.fill(-1)
    num_p_in_nodes.fill(0)
    children.fill(-1)
    masses.fill(-1)
    centers_of_mass.fill(-1)
    s2.fill(-1)
    next_available_index = 1
    return next_available_index

@njit
def subdivide(node_index: int, boundaries: np.ndarray, children: np.ndarray, next_available_index: int) -> int:
    left, top, width, height = boundaries[node_index]
    w_div_2 = width / 2
    h_div_2 = height / 2

    boundaries[next_available_index]   = np.array([left,         top,         w_div_2, h_div_2], dtype=np.float32)
    boundaries[next_available_index+1] = np.array([left+w_div_2, top,         w_div_2, h_div_2], dtype=np.float32)
    boundaries[next_available_index+2] = np.array([left,         top+h_div_2, w_div_2, h_div_2], dtype=np.float32)
    boundaries[next_available_index+3] = np.array([left+w_div_2, top+h_div_2, w_div_2, h_div_2], dtype=np.float32)

    children[node_index, 0] = next_available_index
    children[node_index, 1] = next_available_index+1
    children[node_index, 2] = next_available_index+2
    children[node_index, 3] = next_available_index+3

    return next_available_index+4

@njit # when first calling insert, set node index to zero, level to zero.
def insert(node_index: int, boundaries: np.ndarray, num_p_in_nodes: np.ndarray, particles: np.ndarray,
           children: np.ndarray, particle_index: int, next_available_index: int, px: float, py: float, level: int
    ) -> int: # return 0 = ok, -1 = overflow.
    if not point_in_boundary(boundaries[node_index], px, py):
        return next_available_index
    
    if num_p_in_nodes[node_index] < CAPACITY:
        particles[node_index, num_p_in_nodes[node_index]] = particle_index
        num_p_in_nodes[node_index] += 1
        return next_available_index
    
    if level >= MAX_LEVEL:
        return next_available_index # ur fucked if u get here. increase capacity or something
    
    if children[node_index, 0] == -1:
        if next_available_index+3 < MAX_NODES:
            next_available_index = subdivide(node_index, boundaries, children, next_available_index)

    for c in children[node_index]:
        if c == -1:
            continue
        if point_in_boundary(boundaries[c], px, py):
            return insert(c, boundaries, num_p_in_nodes, particles, children,
                            particle_index, next_available_index, px, py, level+1)

    return next_available_index

def update_quadtree(particle_positions: np.ndarray):
    next_available_index = clear(boundaries, particles, num_p_in_nodes, children, masses, centers_of_mass, s2, next_available_index)
    for i in range(N+1):
        px, py = particle_positions[i]
        insert(0, boundaries, num_p_in_nodes, particles, children, i, next_available_index, px, py, 0)
