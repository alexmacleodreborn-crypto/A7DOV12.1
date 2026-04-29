# core/movement.py

from core.pathfinding import a_star

def get_next_step(state, target_pos):

    start = tuple(state["agent_pos"])
    goal = tuple(target_pos)

    path = a_star(
        start,
        goal,
        state["obstacles"],
        state["grid_size"]
    )

    if not path:
        return start  # stuck

    return path[0]  # next step only
