# app.py

import streamlit as st
import time
import numpy as np
import sys
import os

# =========================
# PATH FIX
# =========================
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

# =========================
# IMPORT CORE
# =========================
from core.state import state
from core.memory import Memory
from core.perception_adapter import perceive
from core.action_selector import select_action
from core.cognitive_bridge import CognitiveBridge
from core.feedback_processor import process_feedback

# =========================
# IMPORT GRID INTERACTION (IMPORTANT)
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
# INIT STATE (SAFE RESET)
# =========================
state["objects"] = [
    {"id": "cube", "pos": [2, 2], "held": False}
]

state["agent_pos"] = [5, 5]
state["atp"] = 1.0
state["coherence"] = 1.0
state["cycle"] = 0

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(layout="wide")
st.title("A7DO — Live Organism")

col1, col2, col3 = st.columns(3)

vitals_box = col1.empty()
memory_box = col2.empty()
env_box = col3.empty()

grid_box = st.empty()
log_box = st.empty()

# =========================
# GRID RENDER
# =========================
def render_grid(state):
    size = state["grid_size"]
    grid = np.zeros((size, size))

    # objects
    for obj in state["objects"]:
        x, y = obj["pos"]
        grid[y][x] = 0.5

    # agent
    ax, ay = state["agent_pos"]
    grid[ay][ax] = 1.0

    return grid

# =========================
# MAIN LOOP
# =========================
run = st.button("Start Simulation")

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
            for obj in state["objects"]:
                st.write(obj)

        # =========================
        # UI: GRID
        # =========================
        grid = render_grid(state)
        grid_box.image(grid, width=300, clamp=True)

        # =========================
        # LOG
        # =========================
        log_box.write(f"{action} → {target}")

        time.sleep(0.3)
