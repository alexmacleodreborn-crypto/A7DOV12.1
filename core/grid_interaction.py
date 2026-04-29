# chassis/grid_interaction.py

from core.movement import get_next_step
import numpy as np


def distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))


class GridInteractionSystem:

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

        # 🟩 PATHFINDING MOVEMENT
        if dist > 1:
            next_step = get_next_step(state, obj_pos)
            state["agent_pos"] = list(next_step)
            return False

        # 🟩 INTERACT
        obj["held"] = True
        state["held_object"] = obj["id"]
        state["atp"] -= 0.05

        return True
