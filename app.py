# app.py

import copy
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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


st.set_page_config(page_title="A7DOV12.1", layout="wide")
st.title("A7DOV12.1 – Integrated Simulation")


# -------------------------
# INIT
# -------------------------
def init():
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

    if "object" not in st.session_state:
        st.session_state.object = Object("cube", [2.0, 2.0, 0.0], mass=1.2)

    if "interaction" not in st.session_state:
        itx = InteractionSystem(
            st.session_state.skeleton,
            st.session_state.muscles,
        )
        executor = ActionExecutor(
            st.session_state.skeleton,
            st.session_state.muscles,
        )
        itx.set_executor(executor)
        itx.add_object(st.session_state.object)
        st.session_state.interaction = itx


init()

org = st.session_state.organism
state = st.session_state.state
memory = st.session_state.memory
bridge = st.session_state.bridge
skeleton = st.session_state.skeleton
muscles = st.session_state.muscles
physics = st.session_state.physics
obj = st.session_state.object
interaction = st.session_state.interaction


# -------------------------
# UI
# -------------------------
c1, c2, c3, c4 = st.columns(4)
steps = c1.slider("Steps", 1, 60, 10)
dt = c2.slider("dt", 0.01, 0.25, 0.1)
activate_muscles = c3.checkbox("Activate arm muscles", True)
auto_run = c4.checkbox("Auto run", True)

run_once = st.button("Run simulation")


# -------------------------
# MAIN LOOP
# -------------------------
def run_cycle(dt):
    # --- organism growth ---
    org.update(dt)

    # --- cognition ---
    perceive(state, memory)
    action, target = select_action(memory, state)
    success = bridge.execute(action, target, state)
    process_feedback(success, action, target, memory, state)

    # --- skeleton ---
    t = org.time * 10.0
    skeleton.update(t)

    # --- muscles ---
    if activate_muscles:
        muscles.activate_group(["bicep_left", "bicep_right"], 0.65)

    muscles.update(t, state)

    # --- physics (NOW DRIVES EVERYTHING) ---
    physics.update(dt, state)

    # --- object ---
    obj.update(dt)

    # --- interaction (NOW HAS ACCESS TO PHYSICS) ---
    interaction.update(state)

    # --- state ---
    state["cycle"] += 1
    state["last_action_success"] = success


# -------------------------
# RUN
# -------------------------
if run_once or auto_run:
    for _ in range(steps if run_once else 1):
        run_cycle(dt)


# -------------------------
# OUTPUT
# -------------------------
left, right = st.columns(2)

with left:
    st.subheader("Cognitive + organism")
    st.json({
        "time": round(org.time, 2),
        "cells": len(org.cells),
        "agent_pos": state["agent_pos"],
        "held_object": state.get("held_object"),
        "coherence": round(state["coherence"], 3),
        "atp": round(state["atp"], 3),
        "cycle": state["cycle"],
    })

with right:
    st.subheader("Physics")
    st.json({
        "center_of_mass": state.get("center_of_mass"),
        "stable": state.get("stable"),
        "object": {
            "held": obj.held,
            "position": obj.position.round(3).tolist(),
        },
        "action": interaction.active_action,
    })


# -------------------------
# VISUAL
# -------------------------
fig, ax = plt.subplots(figsize=(6, 6))

# cells
if org.cells:
    cells = np.array([c.position for c in org.cells])
    ax.scatter(cells[:, 0], cells[:, 1], s=5, alpha=0.2)

# skeleton
for bone in skeleton.bones.values():
    if not bone.exists:
        continue
    ax.plot(
        [bone.start[0], bone.end[0]],
        [bone.start[1], bone.end[1]],
        linewidth=2,
    )

# object
ax.scatter(obj.position[0], obj.position[1], s=80, marker="s")

ax.set_xlim(-25, 25)
ax.set_ylim(-5, 45)
ax.grid(True, alpha=0.2)

st.pyplot(fig)


if auto_run:
    time.sleep(0.1)
    st.rerun()
