# core/cognitive_bridge.py

class CognitiveBridge:
    def __init__(self, interaction):
        self.interaction = interaction

    def execute(self, action, target, state):
        """
        Converts cognitive intent → physical system
        """

        state["current_intent"] = action

        if action == "idle":
            return False

        # delegate to interaction layer
        return self.interaction.execute(action, target, state)
