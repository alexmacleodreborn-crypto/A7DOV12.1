# chassis/growth.py

import math

def sigmoid(t, k=0.05, t0=50):
    return 1 / (1 + math.exp(-k * (t - t0)))


def early_growth(t):
    return sigmoid(t, 0.08, 20)


def mid_growth(t):
    return sigmoid(t, 0.06, 50)


def late_growth(t):
    return sigmoid(t, 0.04, 90)


def global_structural_growth(t):
    return sigmoid(t, 0.05, 60)
