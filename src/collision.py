from settings import *

@numba.njit(parallel=True)
def ccd_resolve(particles: np.ndarray, candidates: np.ndarray, dt: float) -> None:
    """
    Continuous collision detection between 2 particles
    Args:
        particles (np.ndarray): shape (N,M) numpy array representing all particles (N) and their attributes (M attributes per particle)
        candidates (np.ndarray): shape (K,2) numpy array representing all possible collision pairs (K pairs per particle)
        dt (float): delta time over one frame
    """
    K = candidates.shape[0]
    for pair in numba.prange(K):
        p1_index = candidates[pair,0]
        p2_index = candidates[pair,1]
        
        p1 = particles[p1_index]
        p2 = particles[p2_index]
        
        px = p1[0] - p2[0]
        py = p1[1] - p2[1]
        vx = p1[2] - p2[2]
        vy = p1[3] - p2[3]
        R = p1[4] + p2[4]
        R2 = R*R
        
        # p_dot_p is effectively distance squared. if its less than R2, then theres a collision at t=0.
        p_dot_p = px*px + py*py
        if p_dot_p < R2:
            resolve_elastic_collision(p1, p2, 0)
            continue
        
        # if theres no collision already and velocities are zero, then there wont be a collision.
        v_dot_v = vx*vx + vy*vy
        if v_dot_v == 0:
            continue
        
        # quadratic check
        a = v_dot_v
        b = 2*(px*vx + py*vy)
        c = p_dot_p - R2
        
        # if the discriminant is negative, there arent any real solutions.
        discriminant = b*b - 4*a*c
        if discriminant < 0:
            continue

        sqrt_disc = discriminant**0.5
        t1 = (-b - sqrt_disc) / (2*a)
        t2 = (-b + sqrt_disc) / (2*a)
        
        t = dt + 1.0 # sentinel time
        if 0 <= t1 <= dt:
            t = t1
        if 0 <= t2 <= dt and t2 < t:
            t = t2

        if t != dt + 1.0:
            resolve_elastic_collision(p1, p2, t)

@numba.njit
def resolve_elastic_collision(p1: np.ndarray, p2: np.ndarray, t: float) -> None:
    """
    Resolve 2D elastic collision between particle i and j at time t.
    Args:
        p1 (np.ndarray): shape M array representing a particle with M attributes.
        p2 (np.ndarray): shape M array representing a particle with M attributes.
        t (float): the time of collision between particles p1 and p2.
    """
    # move to collision
    p1[0] += p1[2] * t
    p1[1] += p1[3] * t
    p2[0] +=p2[2] * t
    p2[1] += p2[3] * t

    # relative position & velocity
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dvx = p2[2] - p1[2]
    dvy = p2[3] - p1[3]

    dist2 = dx*dx + dy*dy
    if dist2 == 0.0:
        return

    m1 = p1[5]
    m2 = p2[5]

    v_dot_p = dvx*dx + dvy*dy
    coeff = 2.0 * v_dot_p / ((m1 + m2) * dist2)

    # update velocities
    p1[2] += coeff * m2 * dx
    p1[3] += coeff * m2 * dy
    p2[2] -= coeff * m1 * dx
    p2[3] -= coeff * m1 * dy
