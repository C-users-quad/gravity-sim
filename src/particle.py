from settings import N, G, R, CENTRAL_PARTICLE_MASS, ORBITING_PARTICLE_MASS, MAX_UNIFORM_DISC_RADIUS, HALF_WORLD_LENGTH, np, njit, prange
from utils import calculate_radius, initialize_velocity
from collision import ccd_resolve

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

def make_particles() -> None:
    """
    initializes and creates n orbital particles + one central particle in a uniform disc.
    """
    particle_radii = [(0, 0)] # this first index represents the central particle.
    max_r2 = MAX_UNIFORM_DISC_RADIUS*MAX_UNIFORM_DISC_RADIUS
    min_r2 = central_particle_r*central_particle_r
    for _ in range(N):
        u = np.random.uniform(0.0, 1.0)
        r = np.sqrt((max_r2 - min_r2) * u + min_r2)
        theta = np.random.uniform(0, 2 * np.pi)
        particle_radii.append((r, theta))
    
    cumulative_mass = [CENTRAL_PARTICLE_MASS]
    for _ in range(N):
        m_enclosed = cumulative_mass[-1] + ORBITING_PARTICLE_MASS
        cumulative_mass.append(m_enclosed)

    for i, (r, theta) in enumerate(particle_radii):
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        positions[i] = [x, y]

        v = initialize_velocity(x, y, cumulative_mass[i])
        velocities[i] = v

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
        accelerations: np.ndarray, positions: np.ndarray, G: float
    ) -> None:
    """
    Applys forces to all particles.
    Args:
        particle_index (int): index of particle you are applying forces to
        pseudo_particles (np.ndarray): 2d array representing barnes hut centers of mass for force approximations.
        dt (float): delta time.
        accelerations (np.ndarray): array of all particle accelerations.
    """
    epsilon = 1.0
    if pseudo_particles.shape[0] == 0:
        return
    ppx, ppy, ppm = pseudo_particles[:, 0], pseudo_particles[:, 1], pseudo_particles[:, 2]
    dx = ppx - positions[particle_index, 0]
    dy = ppy - positions[particle_index, 1]
    d2 = dx*dx + dy*dy + epsilon

    accelerations[particle_index, 0] = np.sum(G * ppm * dx / (d2 * np.sqrt(d2)))
    accelerations[particle_index, 1] = np.sum(G * ppm * dy / (d2 * np.sqrt(d2)))

@njit
def update_position(
        particle_index: int, dt: float, positions: np.ndarray, velocities: np.ndarray, 
        accelerations: np.ndarray, masses: np.ndarray, radii: np.ndarray, G: float
    ) -> None:
    """
    Uses velocity verlet integration to update particle positions, velocities, and accelerations.
    """
    # position update
    positions[particle_index, 0] += velocities[particle_index, 0] * dt + 0.5 * accelerations[particle_index, 0] * dt*dt
    world_border_collisions(particle_index, 0, positions, velocities)

    positions[particle_index, 1] += velocities[particle_index, 1] * dt + 0.5 * accelerations[particle_index, 1] * dt*dt
    world_border_collisions(particle_index, 1, positions, velocities)

    old_a = accelerations[particle_index]
    accelerations[particle_index, 0] = 0.0
    accelerations[particle_index, 1] = 0.0

    # force update
    pseudo_particles = query_bh(particle_index)
    apply_forces(particle_index, pseudo_particles, accelerations, positions, G)

    # collision check
    collision_candidates = get_neighbors(particle_index) # returns np.ndarray with elements candidate_index
    for i in range(collision_candidates.shape[0]):
        candidate_index = collision_candidates[i]
        if candidate_index == particle_index:
            continue
        ccd_resolve(
            particle_index, candidate_index, dt,
            positions, velocities, radii, masses
        )

    velocities[particle_index] += 0.5 * (old_a + accelerations[particle_index]) * dt

@njit
def update_physics(
        particle_index: int, dt: float, positions: np.ndarray, velocities: np.ndarray, 
        accelerations: np.ndarray, masses: np.ndarray, radii: np.ndarray, G: float
    ) -> None:

    if particle_index != 0: # only update physics if its not the central particle
        update_position(
            particle_index, dt, 
            positions, velocities, accelerations, masses, radii, G
        )

@njit
def update_particle(particle_index: int, dt: float) -> None:
    update_physics(
        particle_index, dt, positions, velocities, 
        accelerations, masses, radii, G
    )
