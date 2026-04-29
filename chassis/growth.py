# chassis/growth.py

import math

def sigmoid(t, k=0.05, t0=50):
    return 1 / (1 + math.exp(-k * (t - t0)))


def structural_growth(t):
    """
    G_struct(t)
    Controls bone scaling over biological time
    """
    return sigmoid(t, 0.05, 60)


def developmental_phase(t):
    if t < 20:
        return "embryo"
    elif t < 50:
        return "fetal"
    elif t < 100:
        return "infant"
    elif t < 200:
        return "child"
    else:
        return "adult"
