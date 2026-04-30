# chassis/interaction_system.py

import numpy as np


class InteractionSystem:
    def __init__(self, skeleton, muscles):
        self.executor = None
        self.skeleton = skeleton
        self.muscles = muscles

        self.objects = []
        self.active_action = None

    def set_executor(self, executor):
        self.executor = executor

    def add_object(self, obj):
        self.objects.append(obj)

    # -----------------------------
    # CORE UPDATE
    # -----------------------------
    def update(self, state):
        if not self.executor:
            return

        bodies = state.get("bodies", [])
        if not bodies:
            return

        # -----------------------------
        # FIND HAND POSITION
        # -----------------------------
        hand_pos = self._get_hand_position()

        # -----------------------------
        # PROCESS OBJECT INTERACTIONS
        # -----------------------------
        held_any = False

        for obj in self.objects:
            obj_pos = np.array(obj.position)

            distance = np.linalg.norm(hand_pos - obj_pos)

            # -----------------------------
            # CONTACT CHECK
            # -----------------------------
            contact = distance < 1.5

            # -----------------------------
            # GRIP FORCE
            # -----------------------------
            grip_force = self._compute_grip_force(state)

            required_force = getattr(obj, "mass", 1.0) * 9.81 * 0.2

            if contact and grip_force >= required_force:
                obj.held = True
                obj.position = hand_pos.copy()
                held_any = True
            else:
                obj.held = False

        # -----------------------------
        # WRITE TO STATE (SINGLE SOURCE OF TRUTH)
        # -----------------------------
        if held_any:
            for obj in self.objects:
                if obj.held:
                    state["held_object"] = obj.id
                    break
        else:
            state["held_object"] = None

        # -----------------------------
        # OPTIONAL: expose physical objects
        # -----------------------------
        state["objects_physical"] = [
            {
                "id": obj.id,
                "held": obj.held,
                "position": obj.position.tolist()
            }
            for obj in self.objects
        ]

    # -----------------------------
    # HELPERS
    # -----------------------------
    def _get_hand_position(self):
        # try to find a hand bone
        for bone in self.skeleton.bones.values():
            if "hand" in bone.id.lower():
                return bone.center()

        # fallback
        return np.array([0.0, 0.0, 0.0])

    def _compute_grip_force(self, state):
        total_force = 0.0

        for m in self.muscles.muscles.values():
            if not m.active:
                continue

            if "arm" in m.name or "bicep" in m.name or "forearm" in m.name:
                total_force += m.compute_force(state.get("atp", 0.0))

        return total_force
