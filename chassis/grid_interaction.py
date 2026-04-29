# chassis/grid_interaction.py

import numpy as np


def distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))


def move_towards(current, target):
    current = np.array(current)
    target = np.array(target)

    direction = target - current

    if np.linalg.norm(direction) < 0.01:
        return current.tolist()

    step = direction / np.linalg.norm(direction)
    new_pos = current + step

    return new_pos.round().astype(int).tolist()


class GridInteractionSystem:
    """
    Lightweight interaction system for dashboard simulation
    (does NOT require skeleton/muscles)
    """

    def __init__(self):
        pass

    def execute(self, action, target, state):

        if action == "idle":
            return False

        obj = None
        for o in state["objects"]:
            if o["id"] == target:
                obj = o
                break

        if obj is None:
            return False

        agent_pos = state["agent_pos"]
        obj_pos = obj["pos"]

        dist = distance(agent_pos, obj_pos)

        # MOVE FIRST
        if dist > 1:
            state["agent_pos"] = move_towards(agent_pos, obj_pos)
            return False

        # INTERACT
        obj["held"] = True
        state["held_object"] = obj["id"]
        state["atp"] -= 0.05

        return True
