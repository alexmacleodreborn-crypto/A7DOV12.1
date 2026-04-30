# chassis/kinematics.py

import numpy as np


def _rotation_matrix_xyz(rotation):
    rx, ry, rz = rotation

    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    cz, sz = np.cos(rz), np.sin(rz)

    rx_m = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry_m = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz_m = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])

    return rz_m @ ry_m @ rx_m


def forward_kinematics(chain):
    """
    chain = list of bones from root → end effector
    returns end effector position

    Assumes each bone has a local segment vector (end - start) and a local
    Euler rotation. Bone transforms are applied parent-to-child.
    """
    if not chain:
        return np.zeros(3)

    pos = chain[0].start.copy()
    cumulative_rotation = np.eye(3)

    for bone in chain:
        local_vec = bone.end - bone.start
        cumulative_rotation = cumulative_rotation @ _rotation_matrix_xyz(bone.rotation)
        pos = pos + cumulative_rotation @ local_vec

    return pos
