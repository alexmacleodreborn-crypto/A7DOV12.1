# chassis/action_executor.py

from .contact import detect_contact
from .grip import compute_grip_force, can_hold

class ActionExecutor:
    def __init__(self, skeleton, muscles):
        self.skeleton = skeleton
        self.muscles = muscles

        self.held_object = None

    def grab(self, hand_bone, obj, state):
        hand_pos = hand_bone.center()

        contact, dist = detect_contact(hand_pos, obj.position)

        if not contact:
            return False

        # compute muscle force (simplified: sum relevant muscles)
        total_force = sum(
            m.compute_force(state["atp"])
            for m in self.muscles.muscles.values()
            if m.active
        )

        grip_force = compute_grip_force(total_force)

        if can_hold(grip_force, obj.grip_required):
            obj.held = True
            self.held_object = obj
            return True

        return False

    def hold(self, hand_bone):
        if self.held_object:
            self.held_object.position = hand_bone.center()

    def release(self):
        if self.held_object:
            self.held_object.held = False
            self.held_object = None
