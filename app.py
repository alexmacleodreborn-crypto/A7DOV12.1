import streamlit as st
import time

from chassis.physics_engine import PhysicsEngine
from chassis.interaction_system import InteractionSystem
from chassis.action_executor import ActionExecutor
from chassis.motor_controller import MotorController
from chassis.growth import global_structural_growth


# -------------------------
# DUMMY STRUCTURES (replace later)
# -------------------------

class DummySkeleton:
    def __init__(self):
        self.bones = {}

class DummyMuscles:
    def __init__(self):
        self.muscles = {}


# -------------------------
# SYSTEM INIT (persisted)
# -------------------------

if "system" not in st.session_state:

    skeleton = DummySkeleton()
    muscles = DummyMuscles()

    system = {
        "skeleton": skeleton,
        "muscles": muscles,
        "physics": PhysicsEngine(skeleton, muscles),
        "interaction": InteractionSystem(skeleton, muscles),
        "executor": ActionExecutor(skeleton, muscles),
        "motor": MotorController(skeleton, muscles),
        "state": {
            "t": 0.0,
            "dt": 0.1,
            "atp": 1.0,
            "held_object": None,
        }
    }

    system["interaction"].set_executor(system["executor"])

    st.session_state.system = system


system = st.session_state.system


# -------------------------
# UPDATE STEP
# -------------------------

def step(system):
    state = system["state"]
    t = state["t"]
    dt = state["dt"]

    # DEVELOPMENT
    scale = global_structural_growth(t)

    for bone in system["skeleton"].bones.values():
        bone.update(t, scale)

    for muscle in system["muscles"].muscles.values():
        muscle.update(t, state["atp"])

    # MOTOR
    system["motor"].update(t, state)

    # PHYSICS
    system["physics"].update(dt, state)

    # INTERACTION
    system["interaction"].update(state)

    # ENERGY
    state["atp"] = min(1.0, state["atp"] + 0.01)

    # TIME
    state["t"] += dt


# -------------------------
# UI
# -------------------------

st.title("A7DO Organism")

col1, col2 = st.columns(2)

with col1:
    if st.button("Step"):
        step(system)

with col2:
    auto = st.toggle("Auto Run", value=False)


# AUTO LOOP (controlled)
if auto:
    step(system)
    time.sleep(0.05)
    st.rerun()


# -------------------------
# DISPLAY STATE
# -------------------------

state = system["state"]

st.subheader("State")

st.write({
    "time": round(state["t"], 2),
    "atp": round(state["atp"], 2),
    "held_object": state["held_object"]
})