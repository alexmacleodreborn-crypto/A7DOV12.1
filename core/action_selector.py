# core/action_selector.py

import random

def score(node, state):
    if not node.links:
        return 0

    base_score = 0

    for target, resistance in node.links.items():
        base_score += node.voltage / (resistance + 1e-6)

    # 🔥 NEW: distance penalty
    distance_penalty = 1.0
    if hasattr(node, "metadata") and "distance" in node.metadata:
        distance_penalty = 1 / (node.metadata["distance"] + 1)

    # system modifiers
    total = base_score * distance_penalty
    total *= state["coherence"]
    total *= state["atp"]

    return total + random.uniform(-0.05, 0.05)


def select_action(memory, state):
    best_node = None
    best_score = -999

    for node in memory.nodes.values():
        s = score(node, state)

        if s > best_score:
            best_score = s
            best_node = node

    if best_score < 0.1:
        return ("idle", None)

    return ("interact", best_node.name)
