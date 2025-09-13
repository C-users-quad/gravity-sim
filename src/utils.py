from settings import *

@njit
def calculate_radius(mass: float) -> float:
    radius = np.sqrt(mass / np.pi)
    return max(MIN_RADIUS, min(radius, MAX_RADIUS))

def initialize_velocity(x, y, m_enclosed):
    pos = np.array([x, y], dtype=np.float64)
    r = np.linalg.norm(pos)

    if r == 0:
        return np.zeros(2)

    v_t = np.sqrt(G * m_enclosed / r)

    direction = np.array([-pos[1], pos[0]], dtype=np.float64)
    direction /= np.linalg.norm(direction)
    v = v_t * direction
    return v

def interpolate(accumulator: int, value: Sequence[float], old_value: Sequence[float]
    ) -> Sequence[float]:
    """
    Takes in a value and interpolates it between it and its old value one update before the present

    Args:
        alpha (float): factor of interpolation
        dt_physics (float): dt of physics updates
        accumulator (float): dt of frame_dt - num_physics_updates * dt_physics
        value (Sequence[float]): current state of value to interpolate
        old_value (Sequence[float]): state of value one update before current

    Returns:
        Sequence[float]: interpolated value
    """
    alpha = accumulator / DT_PHYSICS
    interp_value = old_value + (value - old_value) * alpha
    return interp_value
