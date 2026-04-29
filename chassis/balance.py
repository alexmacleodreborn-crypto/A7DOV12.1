# chassis/balance.py

import numpy as np

def compute_center_of_mass(bodies):
    total_mass = 0
    weighted = np.zeros(3)

    for b in bodies:
        weighted += b.position * b.mass
        total_mass += b.mass

    return weighted / total_mass if total_mass > 0 else weighted


def support_polygon(feet_positions):
    """
    Simplified: returns bounding box of feet
    """
    xs = [p[0] for p in feet_positions]
    zs = [p[2] for p in feet_positions]

    return min(xs), max(xs), min(zs), max(zs)


def is_stable(com, support):
    min_x, max_x, min_z, max_z = support

    return (min_x <= com[0] <= max_x) and (min_z <= com[2] <= max_z)
