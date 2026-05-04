# core/action_selector.py

import random


# -----------------------------
# SCORING FUNCTION
# -----------------------------
def score(node, state):
    """
    Scores a memory node based on:
    - connection strength (voltage / resistance)
    - distance (if available)
    - organism state (ATP, coherence)
    """

    if not node.links:
        return 0.0

    base_score = 0.0

    for target, resistance in node.links.items():
        base_score += node.voltage / (resistance + 1e-6)

    # -----------------------------
    # DISTANCE MODIFIER
    # -----------------------------
    distance_penalty = 1.0
    if hasattr(node, "metadata") and node.metadata:
        if "distance" in node.metadata:
            d = node.metadata["distance"]
            distance_penalty = 1.0 / (d + 1.0)

    # -----------------------------
    # ORGANISM STATE MODIFIERS
    # -----------------------------
    total = base_score
    total *= distance_penalty
    total *= state.get("coherence", 1.0)
    total *= state.get("atp", 1.0)

    # -----------------------------
    # SMALL EXPLORATION NOISE
    # -----------------------------
    total += random.uniform(-0.05, 0.05)

    return total


# -----------------------------
# ACTION SELECTION
# -----------------------------
class ActionSelector:
    def __init__(self):
        self.last_action = None

    def select(self, memory, state):
        """
        Select best action based on memory graph.
        Writes decision into global state.
        """

        best_node = None
        best_score = -999.0

        # -----------------------------
        # EVALUATE ALL NODES
        # -----------------------------
        for node in memory.nodes.values():

            # 🚨 skip self node
            if node.name == "self":
                continue

            s = score(node, state)

            if s > best_score:
                best_score = s
                best_node = node

        # -----------------------------
        # NO VALID ACTION
        # -----------------------------
        if best_node is None or best_score < 0.1:
            state["target_object"] = None
            self.last_action = ("idle", None)
            return self.last_action

        # -----------------------------
        # SET TARGET IN GLOBAL STATE
        # -----------------------------
        state["target_object"] = best_node.name

        # -----------------------------
        # DETERMINE ACTION TYPE
        # -----------------------------
        action_type = self._decide_action_type(best_node, state)

        self.last_action = (action_type, best_node.name)

        return self.last_action

    # -----------------------------
    # ACTION TYPE LOGIC
    # -----------------------------
    def _decide_action_type(self, node, state):
        """
        Decide what kind of action to perform.
        Expandable later (grab, move, inspect, etc.)
        """

        # If already holding something → maybe release later
        if state.get("held_object"):
            return "hold"

        # If close → interact
        if hasattr(node, "metadata") and node.metadata:
            if "distance" in node.metadata:
                if node.metadata["distance"] < 1.5:
                    return "interact"

        # Otherwise move toward it
        return "reach"
