# core/perception_adapter.py

def perceive(state, memory):
    """
    Convert environment into memory nodes + spatial awareness
    """

    perceived = []

    agent_pos = state["agent_pos"]

    for obj in state["objects_physical"]:
        node = memory.get_or_create(obj["id"])

        # store distance (important for decision later)
        dx = obj["position"][0] - agent_pos[0]
        dy = obj["position"][1] - agent_pos[1]

        node.metadata = {
            "pos": obj["position"],
            "distance": abs(dx) + abs(dy)
        }

        memory.link("self", obj["id"])
        perceived.append(node)

    return perceived
