# core/action_selector.py

import random

def score(node, state):
    if not node.links:
        return 0

    total = 0
    for target, resistance in node.links.items():
        total += node.voltage / (resistance + 1e-6)

    # apply system constraints
    total *= state["coherence"]
    total *= state["atp"]

    return total + random.uniform(-0.05, 0.05)


def select_action(memory, state):
    best = None
    best_score = -999

    for node in memory.nodes.values():
        s = score(node, state)

        if s > best_score:
            best_score = s
            best = node.name

    if best_score < 0.1:
        return ("idle", None)

    return ("grab", best)
