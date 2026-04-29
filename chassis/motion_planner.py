# chassis/motion_planner.py

import numpy as np

def plan_reach(current_pos, target_pos):
    """
    Creates smooth motion path
    """
    steps = 10
    path = []

    for i in range(steps):
        t = i / steps
        pos = current_pos * (1 - t) + target_pos * t
        path.append(pos)

    return path
