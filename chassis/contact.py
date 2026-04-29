# chassis/contact.py

import numpy as np

def detect_contact(hand_pos, obj_pos, threshold=2.0):
    dist = np.linalg.norm(hand_pos - obj_pos)
    return dist < threshold, dist
