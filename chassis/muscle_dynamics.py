# chassis/muscle_dynamics.py

def apply_fatigue(muscle, force_output):
    fatigue_gain = force_output * 0.01
    muscle.fatigue += fatigue_gain
    muscle.fatigue = min(1.0, muscle.fatigue)


def atp_drain(total_force):
    return total_force * 0.001
