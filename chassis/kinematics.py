# chassis/kinematics.py

import numpy as np

def forward_kinematics(chain):
    """
    chain = list of bones from root → end effector
    returns end effector position
    """
    pos = np.zeros(3)

    for bone in chain:
        direction = bone.direction()
        length = bone.length()
        pos += direction * length

    return pos
