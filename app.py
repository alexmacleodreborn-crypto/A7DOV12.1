# app.py

import time

from chassis.physics_engine import PhysicsEngine
from chassis.interaction_system import InteractionSystem
from chassis.action_executor import ActionExecutor
from chassis.motor_controller import MotorController

# you already have these
from chassis.growth import global_structural_growth


# -------------------------
# MOCK / BRIDGE OBJECTS
# (replace with your real loaders later)
# -------------------------

class DummySkeleton:
    def __init__(self, bones):
        self.bones = bones


class DummyMuscles:
    def __init__(self, muscles):
        self.muscles = muscles


# -------------------------
# MAIN ORGANISM
# -------------------------

class A7DO:
    def __init__(self, skeleton, muscles):

        self.skeleton = skeleton
        self.muscles = muscles

        # systems
        self.physics = PhysicsEngine(skeleton, muscles)
        self.interaction = InteractionSystem(skeleton, muscles)
        self.executor = ActionExecutor(skeleton, muscles)
        self.motor = MotorController(skeleton, muscles)

        self.interaction.set_executor(self.executor)

        # unified state
        self.state = {
            "t": 0.0,
            "dt": 0.1,
            "atp": 1.0,
            "held_object": None,
        }

    # -------------------------
    # MAIN LOOP STEP
    # -------------------------
    def update(self):

        t = self.state["t"]
        dt = self.state["dt"]

        # -------------------------
        # 1. DEVELOPMENT (bones + muscles)
        # -------------------------
        global_scale = global_structural_growth(t)

        for bone in self.skeleton.bones.values():
            bone.update(t, global_scale)

        for muscle in self.muscles.muscles.values():
            muscle.update(t, self.state["atp"])

        # -------------------------
        # 2. MOTOR CONTROL (optional target)
        # -------------------------
        self.motor.update(t, self.state)

        # -------------------------
        # 3. PHYSICS
        # -------------------------
        self.physics.update(dt, self.state)

        # -------------------------
        # 4. INTERACTION
        # -------------------------
        self.interaction.update(self.state)

        # -------------------------
        # 5. ENERGY RECOVERY
        # -------------------------
        self.state["atp"] = min(1.0, self.state["atp"] + 0.01)

        # -------------------------
        # 6. TIME
        # -------------------------
        self.state["t"] += dt

    # -------------------------
    # RUN LOOP
    # -------------------------
    def run(self):

        while True:
            self.update()

            print(f"\nTime: {round(self.state['t'],2)}")
            print(f"ATP: {round(self.state['atp'],2)}")
            print(f"Held: {self.state.get('held_object')}")

            time.sleep(0.05)


# -------------------------
# ENTRY POINT
# -------------------------

def build_system():
    """
    You will replace this with your actual skeleton/muscle builder
    """

    # TEMP: empty placeholders so system runs
    skeleton = DummySkeleton(bones={})
    muscles = DummyMuscles(muscles={})

    return A7DO(skeleton, muscles)


if __name__ == "__main__":
    system = build_system()
    system.run()