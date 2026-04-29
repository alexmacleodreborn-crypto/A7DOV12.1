# chassis/interaction_system.py

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

    def update(self, state):
        if not self.executor:
            return

        # simple example: always try grab first object
        if self.objects:
            obj = self.objects[0]

            hand = self.skeleton.bones.get("right_arm")

            if hand:
                success = self.executor.grab(hand, obj, state)

                if success:
                    self.active_action = "holding"
                else:
                    self.active_action = "reaching"

        # maintain hold
        if self.executor.held_object:
            hand = self.skeleton.bones.get("right_arm")
            self.executor.hold(hand)
