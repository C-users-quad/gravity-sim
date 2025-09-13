from settings import N, G, R, DT_PHYSICS, CENTRAL_PARTICLE_MASS, ORBITING_PARTICLE_MASS, MAX_UNIFORM_DISC_RADIUS, HALF_WORLD_LENGTH, np, njit, prange, math, time
from utils import calculate_radius, initialize_velocity
from collision import ccd_resolve, point_in_boundary
from quadtree import query_bh, get_query_bh_args

central_particle_r = calculate_radius(CENTRAL_PARTICLE_MASS)

radii = np.concatenate([
    [central_particle_r], 
    np.ones(N) * R
]).astype(np.float32) # radius.
colors = np.ones((N + 1, 3), dtype=np.float32) # white.
masses = np.concatenate([
    [CENTRAL_PARTICLE_MASS],
    np.ones(N) * ORBITING_PARTICLE_MASS
]).astype(np.float32)
positions = np.zeros((N + 1, 2), dtype=np.float32) # center positions [cx, cy].
velocities = np.zeros((N + 1, 2), dtype=np.float32) # [vx, vy].
accelerations = np.zeros((N + 1, 2), dtype=np.float32) # [ax, ay].
old_positions = np.empty_like(positions)

def make_particles() -> None:
    """
    Initialize N orbiting particles + one central particle in a uniform disc.
    Sets positions and velocities so that orbits are roughly circular.
    """
    positions[0] = [0.0, 0.0]
    velocities[0] = [0.0, 0.0]

    r_min2 = central_particle_r*central_particle_r
    r_max2 = MAX_UNIFORM_DISC_RADIUS*MAX_UNIFORM_DISC_RADIUS
    for i in range(1, N+1):
        # radius distributed uniformly in area
        u = np.random.uniform(0.0, 1.0)
        r = np.sqrt((r_max2 - r_min2) * u + r_min2)

        theta = np.random.uniform(0, 2*np.pi)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        positions[i] = np.array([x, y], dtype=np.float32)

        # mass enclosed proportional to area inside r
        m_enclosed = CENTRAL_PARTICLE_MASS

        velocities[i] = initialize_velocity(x, y, m_enclosed)

@njit
def world_border_collisions(
        particle_index: int, direction: int,
        positions: np.ndarray, velocities: np.ndarray, radii: np.ndarray
    ) -> None:
    """
    prevents particles from leaving the confines of this cruel world
    Args:
        particle_index (int): the index of the particle currently being checked
        direction (int): 0 for horizontal collisions, 1 for vertical collisions.
    """
    radius = radii[particle_index]
    cx, cy = positions[particle_index]
    if direction == 0: # horizontal
        left = cx - radius
        right = cx + radius
        if left < -HALF_WORLD_LENGTH:
            positions[particle_index, 0] = -HALF_WORLD_LENGTH + radius
            velocities[particle_index, 0] *= -1
        elif right > HALF_WORLD_LENGTH:
            positions[particle_index, 0] = HALF_WORLD_LENGTH - radius
            velocities[particle_index, 0] *= -1
    else: # vertical
        top = cy - radius
        bottom = cy + radius
        if top < -HALF_WORLD_LENGTH:
            positions[particle_index, 1] = -HALF_WORLD_LENGTH + radius
            velocities[particle_index, 1] *= -1
        elif bottom > HALF_WORLD_LENGTH:
            positions[particle_index, 1] = HALF_WORLD_LENGTH - radius
            velocities[particle_index, 1] *= -1

@njit
def apply_forces(
        particle_index: int, pseudo_particles: np.ndarray,
        accelerations: np.ndarray, positions: np.ndarray, G: float, count: int
    ) -> None:
    epsilon = 1.0
    if count == 0:
        return

    px = positions[particle_index, 0]
    py = positions[particle_index, 1]

    ax = 0.0
    ay = 0.0

    for i in range(count):
        dx = pseudo_particles[i, 0] - px
        dy = pseudo_particles[i, 1] - py
        m = pseudo_particles[i, 2]

        d2 = dx*dx + dy*dy + epsilon
        inv_dist3 = 1.0 / (d2 * math.sqrt(d2))

        ax += G * m * dx * inv_dist3
        ay += G * m * dy * inv_dist3

    accelerations[particle_index, 0] += ax
    accelerations[particle_index, 1] += ay

@njit
def update_position(
        particle_index: int, dt: float, positions: np.ndarray, velocities: np.ndarray, 
        accelerations: np.ndarray, masses: np.ndarray, radii: np.ndarray, G: float, 
        old_positions: np.ndarray, query_bh_args: tuple
    ) -> None:
    """
    Uses velocity verlet integration to update particle positions, velocities, and accelerations.
    """
    # position update
    positions[particle_index, 0] += velocities[particle_index, 0] * dt + 0.5 * accelerations[particle_index, 0] * dt*dt
    world_border_collisions(particle_index, 0, positions, velocities, radii)

    positions[particle_index, 1] += velocities[particle_index, 1] * dt + 0.5 * accelerations[particle_index, 1] * dt*dt
    world_border_collisions(particle_index, 1, positions, velocities, radii)

    old_a = accelerations[particle_index].copy()
    accelerations[particle_index, 0] = 0.0
    accelerations[particle_index, 1] = 0.0

    # force update
    px, py = positions[particle_index]
    pseudo_particles, count = query_bh(*query_bh_args, px, py)
    apply_forces(particle_index, pseudo_particles, accelerations, positions, G, count)
    # collision check between orbitals and central
    near_central = point_in_boundary((-500, -500, 1000, 1000), px, py)

    if near_central:
        ccd_resolve(
            particle_index, 0, dt,
            positions, velocities, radii, masses
        )

    velocities[particle_index] += 0.5 * (old_a + accelerations[particle_index]) * dt

def get_args_for_particle_update(dt: float):
    return(dt, N, positions, velocities, 
           accelerations, masses, radii, G, old_positions, get_query_bh_args())

@njit
def update_particles(dt, N, positions, velocities, accelerations, masses, radii, G, old_positions, query_bh_args):
    for i in range(1, N+1):
        update_position(
        i, dt, positions, velocities, 
        accelerations, masses, radii, G, old_positions, query_bh_args
    )
