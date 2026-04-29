# core/cognitive_bridge.py

class CognitiveBridge:
    def __init__(self, memory, interaction):
        self.memory = memory
        self.interaction = interaction

    def execute(self, action, target, state):
        if action == "idle":
            state["current_intent"] = None
            return

        state["current_intent"] = action

        for obj in self.interaction.objects:
            if obj.id == target:
                self.interaction.active_action = action
                return
