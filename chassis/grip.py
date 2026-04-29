# chassis/grip.py

def compute_grip_force(muscle_force, alignment=1.0):
    return muscle_force * alignment


def can_hold(grip_force, required_force):
    return grip_force >= required_force
