from settings import *

@njit
def ccd_resolve(
        particle_index: int, candidate_index: int, dt: float,
        positions: np.ndarray, velocities: np.ndarray, radii: np.ndarray, masses: np.ndarray
    ) -> None:
    """
    Continuous collision detection between 2 particles.
    Args:
        particle_index (int): index of the particle you are checking collisions for
        candidate_index (int) index of the other particle you are checking collisions for
        dt (float): delta time over one frame
        positions (np.ndarray): positions of all particles
        velocities (np.ndarray): velocities of all particles
        radii (np.ndarray): radii of all particles
    """
    p1_x, p1_y = positions[particle_index]
    p2_x, p2_y = positions[candidate_index]

    p1_vx, p1_vy = velocities[particle_index]
    p2_vx, p2_vy = velocities[candidate_index]

    p1_r = radii[particle_index]
    p2_r = radii[candidate_index]

    epsilon = 1e-5

    px = p1_x - p2_x
    py = p1_y - p2_y
    vx = p1_vx - p2_vx
    vy = p1_vy - p2_vy
    R = p1_r + p2_r
    R2 = R*R
    
    # p_dot_p is effectively distance squared. if its less than R2, then theres a collision at t=0.
    p_dot_p = px*px + py*py
    if p_dot_p < R2:
        resolve_collision(particle_index, candidate_index, 0, positions, velocities, radii)
        return
    
    # if theres no collision already and velocities are zero, then there wont be a collision.
    v_dot_v = vx*vx + vy*vy
    if v_dot_v < epsilon:
        return
    
    # quadratic check
    a = v_dot_v
    b = 2*(px*vx + py*vy)
    c = p_dot_p - R2
    
    # if the discriminant is negative, there arent any real solutions.
    discriminant = b*b - 4*a*c
    if discriminant < 0:
        return

    sqrt_disc = np.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2*a)
    t2 = (-b + sqrt_disc) / (2*a)
    
    t = dt + 1.0 # sentinel time
    if 0 <= t1 <= dt:
        t = t1
    if 0 <= t2 <= dt and t2 < t:
        t = t2

    if t != dt + 1.0:
        resolve_collision(particle_index, candidate_index, t, positions, velocities, radii)

@njit
def resolve_collision(particle_index: int, candidate_index: int, t: float, 
        positions: np.ndarray, velocities: np.ndarray, radii: np.ndarray
    ) -> None:
    """
    Resolve 2D elastic collision between particle i and j at time t.
    Args:
        particle_index (int): index of the particle you are checking collisions for
        candidate_index (int) index of the other particle you are checking collisions for
        t (float): the time of collision between particles i and j
        positions (np.ndarray): positions of all particles
        velocities (np.ndarray): velocities of all particles
        radii (np.ndarray): radii of all particles
    """
    p1_vx, p1_vy = velocities[particle_index]
    p2_vx, p2_vy = velocities[candidate_index]

    # move to collision
    positions[particle_index, 0] += p1_vx * t
    positions[particle_index, 1] += p1_vy * t
    positions[candidate_index, 0] += p2_vx * t
    positions[candidate_index, 1] += p2_vy * t

    # relative position
    p1_x, p1_y = positions[particle_index]
    p2_x, p2_y = positions[candidate_index]
    dx = p1_x - p2_x
    dy = p1_y - p2_y

    dist2 = dx*dx + dy*dy
    if dist2 == 0.0:
        return

    dist = np.sqrt(dist2)
    overlap = (radii[particle_index] + radii[candidate_index]) - dist
    if overlap > 0:
        nx, ny = dx / dist, dy / dist
        positions[particle_index, 0] += nx * overlap
        positions[particle_index, 1] += ny * overlap

@njit
def point_in_boundary(boundary: np.ndarray, px: float, py: float) -> bool:
    """returns true if point px, py is in a rectangle with left, top, width, height."""
    left, top, width, height = boundary
    return (left <= px < left + width) and (top <= py < top + height)
