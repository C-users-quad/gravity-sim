def combined_masses(p1, p2):
    return p1.mass + p2.mass

def velocity_of_combined_particles(p1, p2):
    return ((p1.mass * p1.v) + (p2.mass * p2.v)) / (p1.mass + p2.mass)