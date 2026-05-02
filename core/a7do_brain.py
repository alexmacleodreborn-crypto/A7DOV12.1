# core/a7do_brain.py

from core.state import create_initial_state
from core.perception_adapter import perceive
from core.action_selector import ActionSelector
from core.memory import Memory
from core.feedback_processor import process_feedback

from chassis.motor_controller import MotorController
from chassis.physics_engine import PhysicsEngine
from chassis.interaction_system import InteractionSystem

from engine.organism import Organism


class A7DO:
    def __init__(self):
        self.state = create_initial_state()

        # 🧠 cognition
        self.memory = Memory()
        self.selector = ActionSelector()

        # 🦴 body
        self.motor = None  # set after skeleton init
        self.physics = None
        self.interaction = None

        # 🧬 growth
        self.organism = Organism()

        self.initialized = False

    def initialize_body(self, skeleton, muscles):
        self.motor = MotorController(skeleton, muscles)
        self.physics = PhysicsEngine(skeleton, muscles)
        self.interaction = InteractionSystem(skeleton, muscles)

        self.initialized = True

    def update(self, dt):
        if not self.initialized:
            return

        t = self.state["time"]

        # 🧬 1. growth
        self.organism.update(dt)

        # 🦴 1b. body development + muscle dynamics
        # Keep the physical body in sync with biological time before perception,
        # motor execution, and physics use the skeleton/muscle state.
        if self.motor is not None:
            self.motor.skeleton.update(t)
            self.motor.muscles.update(t, self.state)

        # 👁 2. perception
        perceived = perceive(self.state, self.memory)

        # 🧠 3. memory
        self.memory.update(perceived)

        # 🧠 4. decision
        action = self.selector.select(self.memory, self.state)

        # 🎯 5. convert action → motor target
        # Manual dashboard commands get priority so a user-sent limb target is
        # not immediately overwritten by autonomous reach/inspect decisions.
        manual_override = bool(self.state.get("manual_motor_override"))
        if action and not manual_override:
            target = self._get_target_position(action)
            if target is not None:
                self.motor.set_target("right_arm", target)

        # 🦾 6. motor execution
        self.motor.update(t, self.state)

        if manual_override and not self.motor.state.active:
            self.state["manual_motor_override"] = False

        # ⚙️ 7. physics
        self.physics.update(dt, self.state)

        # ✋ 8. interaction
        self.interaction.update(self.state)

        # 🔁 9. feedback
        success = self.motor.state.active  # or some check
        process_feedback(success, action, self.state.get("target_object"), self.memory, self.state)

        # 🔋 10. energy recovery
        self.state["atp"] = min(1.0, self.state["atp"] + 0.01)

        self.state["time"] += dt

    def _get_target_position(self, action):
        # basic mapping (expand later)
        if "target_object" in self.state:
            for obj in self.state.get("objects_physical", []):
                if obj["id"] == self.state["target_object"]:
                    return obj["position"]
        return None
