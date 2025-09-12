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

def interpolate(old_positions, current_positions, accumulator, render_positions):
    """
    DEPRECATED...
    Keeps visuals smooth even if physics is slow by interpolating old and current positions
    Returns:
        render_positions (np.ndarray) : the rendering positions for the particles
    """
    alpha = accumulator / DT
    render_positions[:] = old_positions * (1 - alpha) + current_positions * alpha
    return render_positions
