# app.py

import streamlit as st
import numpy as np
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from core.state import state
from core.memory import Memory
from core.perception_adapter import perceive
from core.action_selector import select_action
from core.cognitive_bridge import CognitiveBridge
from core.feedback_processor import process_feedback
from chassis.grid_interaction import GridInteractionSystem

# =========================
# INIT (ONLY ONCE)
# =========================
if "initialised" not in st.session_state:

    st.session_state.initialised = True

    st.session_state.memory = Memory()
    st.session_state.interaction = GridInteractionSystem()
    st.session_state.bridge = CognitiveBridge(st.session_state.interaction)

    st.session_state.memory.link("self", "cube")

    state["objects"] = [
        {"id": "cube", "pos": [2, 2], "held": False}
    ]

    state["agent_pos"] = [7, 7]

    state["obstacles"] = [
        [4, 4], [4, 5], [4, 6],
        [5, 6], [6, 6]
    ]

    state["grid_size"] = 10
    state["cycle"] = 0

# =========================
# GRID RENDER
# =========================
def render_grid(state):
    grid = np.zeros((state["grid_size"], state["grid_size"]))

    for ox, oy in state["obstacles"]:
        grid[oy][ox] = 0.2

    for obj in state["objects"]:
        x, y = obj["pos"]
        grid[y][x] = 0.5

    ax, ay = state["agent_pos"]
    grid[ay][ax] = 1.0

    return grid

# =========================
# UI
# =========================
st.title("A7DO — Live Organism")

col1, col2, col3 = st.columns(3)

step = st.button("Step")
auto = st.checkbox("Auto Run")

# =========================
# SINGLE STEP FUNCTION
# =========================
def run_step():

    memory = st.session_state.memory
    bridge = st.session_state.bridge

    perceive(state, memory)

    action, target = select_action(memory, state)

    success = bridge.execute(action, target, state)

    process_feedback(success, action, target, memory, state)

    memory.decay()
    state["atp"] = min(1.0, state["atp"] + 0.01)

    state["cycle"] += 1
    state["current_intent"] = action
    state["last_action_success"] = success

# =========================
# EXECUTION CONTROL
# =========================
if step:
    run_step()

if auto:
    run_step()
    st.rerun()

# =========================
# UI OUTPUT
# =========================

with col1:
    st.subheader("Vitals")
    st.write("Cycle:", state["cycle"])
    st.write("ATP:", round(state["atp"], 2))
    st.write("Coherence:", round(state["coherence"], 2))
    st.write("Intent:", state["current_intent"])
    st.write("Success:", state["last_action_success"])

with col2:
    st.subheader("Memory")
    for name, node in st.session_state.memory.nodes.items():
        st.write(f"{name} | V={round(node.voltage,2)}")

with col3:
    st.subheader("Environment")
    st.write("Agent:", state["agent_pos"])
    st.write("Obstacles:", state["obstacles"])
    st.write("Objects:", state["objects"])

st.image(render_grid(state), width=350)
