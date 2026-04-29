# core/perception_adapter.py

def perceive(state, memory):
    """
    Convert environment into memory nodes + spatial awareness
    """

    perceived = []

    agent_pos = state["agent_pos"]

    for obj in state["objects"]:
        node = memory.get_or_create(obj["id"])

        # store distance (important for decision later)
        dx = obj["pos"][0] - agent_pos[0]
        dy = obj["pos"][1] - agent_pos[1]

        node.metadata = {
            "pos": obj["pos"],
            "distance": abs(dx) + abs(dy)
        }

        memory.link("self", obj["id"])
        perceived.append(node)

    return perceived
