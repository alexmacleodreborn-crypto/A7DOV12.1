# app.py

import streamlit as st
import time
import numpy as np
import sys
import os

# =========================
# PATH FIX (CRITICAL)
# =========================
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

# =========================
# IMPORT CORE SYSTEM
# =========================
from core.state import state
from core.memory import Memory
from core.perception_adapter import perceive
from core.action_selector import select_action
from core.cognitive_bridge import CognitiveBridge
from core.feedback_processor import process_feedback

# =========================
# IMPORT INTERACTION SYSTEM
# =========================
from chassis.grid_interaction import GridInteractionSystem

# =========================
# INITIALISE SYSTEM
# =========================
memory = Memory()
interaction = GridInteractionSystem()
bridge = CognitiveBridge(interaction)

# seed memory
memory.link("self", "cube")

# =========================
# RESET STATE (SAFE INIT)
# =========================
state["objects"] = [
    {"id": "cube", "pos": [2, 2], "held": False}
]

state["agent_pos"] = [7, 7]

state["obstacles"] = [
    [4, 4], [4, 5], [4, 6],
    [5, 6], [6, 6]
]

state["grid_size"] = 10
state["atp"] = 1.0
state["coherence"] = 1.0
state["cycle"] = 0
state["held_object"] = None

# =========================
# STREAMLIT UI SETUP
# =========================
st.set_page_config(layout="wide")
st.title("A7DO — Live Organism (Pathfinding Enabled)")

col1, col2, col3 = st.columns(3)

vitals_box = col1.empty()
memory_box = col2.empty()
env_box = col3.empty()

grid_box = st.empty()
log_box = st.empty()

# =========================
# GRID RENDER FUNCTION
# =========================
def render_grid(state):
    size = state["grid_size"]
    grid = np.zeros((size, size))

    # obstacles
    for ox, oy in state["obstacles"]:
        grid[oy][ox] = 0.2

    # objects
    for obj in state["objects"]:
        x, y = obj["pos"]
        grid[y][x] = 0.5

    # agent
    ax, ay = state["agent_pos"]
    grid[ay][ax] = 1.0

    return grid

# =========================
# CONTROL
# =========================
run = st.button("Start Simulation")

# =========================
# MAIN LOOP
# =========================
if run:

    while True:

        # =========================
        # 1. PERCEPTION
        # =========================
        perceive(state, memory)

        # =========================
        # 2. DECISION
        # =========================
        action, target = select_action(memory, state)

        # =========================
        # 3. EXECUTION
        # =========================
        success = bridge.execute(action, target, state)

        # =========================
        # 4. FEEDBACK
        # =========================
        process_feedback(success, action, target, memory, state)

        # =========================
        # 5. DECAY + RECOVERY
        # =========================
        memory.decay()
        state["atp"] = min(1.0, state["atp"] + 0.01)

        # =========================
        # 6. UPDATE STATE
        # =========================
        state["cycle"] += 1
        state["last_action_success"] = success
        state["current_intent"] = action

        # =========================
        # UI: VITALS
        # =========================
        with vitals_box.container():
            st.subheader("Vitals")
            st.write("Cycle:", state["cycle"])
            st.write("ATP:", round(state["atp"], 2))
            st.write("Coherence:", round(state["coherence"], 2))
            st.write("Intent:", action)
            st.write("Success:", success)

        # =========================
        # UI: MEMORY
        # =========================
        with memory_box.container():
            st.subheader("Memory")
            for name, node in memory.nodes.items():
                st.write(
                    f"{name} | V={round(node.voltage,2)} | links={len(node.links)}"
                )

        # =========================
        # UI: ENVIRONMENT
        # =========================
        with env_box.container():
            st.subheader("Environment")

            st.write("Agent Position:", state["agent_pos"])
            st.write("Held Object:", state["held_object"])

            st.write("Objects:")
            for obj in state["objects"]:
                st.write(obj)

            st.write("Obstacles:", state["obstacles"])

        # =========================
        # UI: GRID VISUAL
        # =========================
        grid = render_grid(state)
        grid_box.image(grid, width=350, clamp=True)

        # =========================
        # LOG
        # =========================
        log_box.write(f"{action} → {target}")

        time.sleep(0.3)
