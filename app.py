import copy
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from engine.organism import Organism
from core.state import state as base_state
from core.memory import Memory
from core.perception_adapter import perceive
from core.action_selector import select_action
from core.cognitive_bridge import CognitiveBridge
from core.feedback_processor import process_feedback
from core.grid_interaction import GridInteractionSystem

from chassis.skeleton import Skeleton
from chassis.muscular_system import MuscularSystem
from chassis.physics_engine import PhysicsEngine
from chassis.object_model import Object
from chassis.action_executor import ActionExecutor
from chassis.interaction_system import InteractionSystem


st.set_page_config(page_title="A7DOV12.1 Integrated App", layout="wide")
st.title("A7DOV12.1 – Integrated Bio/Cognitive/Chassis Simulation")


def init_session():
    if "organism" not in st.session_state:
        st.session_state.organism = Organism()

    if "state" not in st.session_state:
        st.session_state.state = copy.deepcopy(base_state)

    if "memory" not in st.session_state:
        m = Memory()
        m.get_or_create("self")
        st.session_state.memory = m

    if "bridge" not in st.session_state:
        st.session_state.bridge = CognitiveBridge(GridInteractionSystem())

    if "skeleton" not in st.session_state:
        st.session_state.skeleton = Skeleton()

    if "muscles" not in st.session_state:
        st.session_state.muscles = MuscularSystem(st.session_state.skeleton)

    if "physics" not in st.session_state:
        st.session_state.physics = PhysicsEngine(
            st.session_state.skeleton,
            st.session_state.muscles,
        )

    if "physical_object" not in st.session_state:
        st.session_state.physical_object = Object("cube", [2.0, 2.0, 0.0], mass=1.2)

    if "physical_interaction" not in st.session_state:
        itx = InteractionSystem(st.session_state.skeleton, st.session_state.muscles)
        executor = ActionExecutor(st.session_state.skeleton, st.session_state.muscles)
        itx.set_executor(executor)
        itx.add_object(st.session_state.physical_object)
        st.session_state.physical_interaction = itx


init_session()

org = st.session_state.organism
state = st.session_state.state
memory = st.session_state.memory
bridge = st.session_state.bridge
skeleton = st.session_state.skeleton
muscles = st.session_state.muscles
physics = st.session_state.physics
physical_obj = st.session_state.physical_object
physical_itx = st.session_state.physical_interaction

col1, col2, col3 = st.columns(3)
steps = col1.slider("Steps", 1, 60, 10)
dt = col2.slider("dt", 0.01, 0.25, 0.1)
activate_muscles = col3.checkbox("Activate arm muscles", True)

run = st.button("Run simulation")


def run_cycle(dt_value: float):
    org.update(dt_value)

    perceive(state, memory)
    action, target = select_action(memory, state)
    success = bridge.execute(action, target, state)
    process_feedback(success, action, target, memory, state)

    t = org.time * 10.0
    skeleton.update(t)

    if activate_muscles:
        muscles.activate_group(["bicep_left", "bicep_right"], 0.65)

    muscles.update(t, state)
    physics.update(dt_value, state)

    physical_obj.update(dt_value)
    physical_itx.update(state)

    state["cycle"] += 1
    state["last_action_success"] = success


if run:
    for _ in range(steps):
        run_cycle(dt)


left, right = st.columns(2)

with left:
    st.subheader("Cognitive + organism state")
    st.json(
        {
            "time": round(org.time, 2),
            "cells": len(org.cells),
            "agent_pos": state["agent_pos"],
            "held_object": state.get("held_object"),
            "coherence": round(state["coherence"], 3),
            "atp": round(state["atp"], 3),
            "cycle": state["cycle"],
            "last_action_success": state["last_action_success"],
            "current_intent": state.get("current_intent"),
        }
    )

    st.write("Memory nodes:", list(memory.nodes.keys()))

with right:
    st.subheader("Skeleton + physics state")
    st.json(
        {
            "center_of_mass": state.get("center_of_mass"),
            "stable": state.get("stable"),
            "physical_object": {
                "id": physical_obj.id,
                "held": physical_obj.held,
                "position": physical_obj.position.round(3).tolist(),
            },
            "chassis_action": physical_itx.active_action,
        }
    )


st.subheader("Visualizations")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Cells + agent/object map (x,y)
if org.cells:
    cells = np.array([c.position for c in org.cells])
    axes[0].scatter(cells[:, 0], cells[:, 1], s=6, alpha=0.25, label="cells")

axes[0].scatter(state["agent_pos"][0], state["agent_pos"][1], s=80, marker="x", label="agent")
for obj in state["objects"]:
    axes[0].scatter(obj["pos"][0], obj["pos"][1], s=80, marker="s", label=f"obj:{obj['id']}")

for ox, oy in state["obstacles"]:
    axes[0].scatter(ox, oy, s=50, marker="s", alpha=0.5)

axes[0].set_title("Engine cells + Core grid world")
axes[0].set_xlabel("x")
axes[0].set_ylabel("y")
axes[0].legend(loc="upper right", fontsize=8)

# Skeleton view (x,y)
for bone in skeleton.bones.values():
    if not bone.exists:
        continue
    xs = [bone.start[0], bone.end[0]]
    ys = [bone.start[1], bone.end[1]]
    axes[1].plot(xs, ys, linewidth=3)
    c = bone.center()
    axes[1].scatter(c[0], c[1], s=15)

axes[1].set_title("Chassis skeleton")
axes[1].set_xlabel("x")
axes[1].set_ylabel("y")
axes[1].set_xlim(-25, 25)
axes[1].set_ylim(-5, 45)
axes[1].grid(True, alpha=0.2)

st.pyplot(fig)
