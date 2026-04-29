# chassis/ik_solver.py

import numpy as np

def solve_ik(chain, target, iterations=10, alpha=0.1):
    """
    Simple gradient IK solver
    """

    for _ in range(iterations):
        end_pos = forward_kinematics(chain)
        error = target - end_pos

        if np.linalg.norm(error) < 0.01:
            break

        # adjust each joint backwards
        for bone in reversed(chain):
            direction = bone.direction()

            # simple rotation approximation
            adjustment = alpha * error

            bone.rotation += adjustment[:3]

    return chain
