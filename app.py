import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt

# A7DO SYSTEMS
from chassis.bone import Bone
from chassis.growth import early, global_structural_growth
from chassis.physics_engine import PhysicsEngine
from chassis.interaction_system import InteractionSystem
from chassis.action_executor import ActionExecutor
from chassis.motor_controller import MotorController


# -------------------------
# BUILD SKELETON (REAL BASE)
# -------------------------

def build_skeleton():

    bones = {}

    bones["spine"] = Bone(
        "spine",
        None,
        [0, 0, 0],
        [0, 1, 0],
        {"t_start": 0, "growth": early}
    )

    bones["neck"] = Bone(
        "neck",
        "spine",
        [0, 1, 0],
        [0, 1.3, 0],
        {"t_start": 2, "growth": early}
    )

    bones["head"] = Bone(
        "head",
        "neck",
        [0, 1.3, 0],
        [0, 1.6, 0],
        {"t_start": 3, "growth": early}
    )

    bones["left_arm"] = Bone(
        "left_arm",
        "spine",
        [0, 0.9, 0],
        [-0.5, 1.2, 0],
        {"t_start": 4, "growth": early}
    )

    bones["right_arm"] = Bone(
        "right_arm",
        "spine",
        [0, 0.9, 0],
        [0.5, 1.2, 0],
        {"t_start": 4, "growth": early}
    )

    class Skeleton:
        def __init__(self, bones):
            self.bones = bones

    return Skeleton(bones)


# -------------------------
# RENDER SKELETON
# -------------------------

def render_skeleton(skeleton):
    fig, ax = plt.subplots()

    for bone in skeleton.bones.values():
        if not bone.exists:
            continue

        x = [bone.start[0], bone.end[0]]
        y = [bone.start[1], bone.end[1]]

        ax.plot(x, y)

    ax.set_title("A7DO Skeleton")
    ax.set_aspect("equal")
    ax.set_xlim(-2, 2)
    ax.set_ylim(0, 2)

    return fig


# -------------------------
# INIT SYSTEM (PERSISTENT)
# -------------------------

if "system" not in st.session_state:

    skeleton = build_skeleton()

    system = {
        "skeleton": skeleton,
        "physics": PhysicsEngine(skeleton, None),
        "interaction": InteractionSystem(skeleton, None),
        "executor": ActionExecutor(skeleton, None),
        "motor": MotorController(skeleton, None),
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

    # DEVELOPMENT (bone growth)
    scale = global_structural_growth(t)

    for bone in system["skeleton"].bones.values():
        bone.update(t, scale)

    # MOTOR (placeholder)
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

st.title("A7DO — Embryo → Organism")

col1, col2 = st.columns(2)

with col1:
    if st.button("Step"):
        step(system)

with col2:
    auto = st.toggle("Auto Run", value=False)


# AUTO LOOP
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


# -------------------------
# DISPLAY SKELETON
# -------------------------

st.subheader("Skeleton")

fig = render_skeleton(system["skeleton"])
st.pyplot(fig)