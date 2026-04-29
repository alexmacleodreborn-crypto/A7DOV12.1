import streamlit as st
import time
import numpy as np

# ==== IMPORT YOUR MODULES ====
from memory import Memory
from decision import decide
from interaction import execute
from state import state

# =============================
# INITIALISE SYSTEM
# =============================

memory = Memory()

# seed
memory.link("self", "cube")

state["objects"] = [
    {"id": "cube", "pos": [0, 0], "held": False}
]

# =============================
# STREAMLIT UI
# =============================

st.set_page_config(layout="wide")
st.title("A7DO — Live Organism Dashboard")

col1, col2, col3 = st.columns(3)

# placeholders
vitals_box = col1.empty()
memory_box = col2.empty()
env_box = col3.empty()

log_box = st.empty()

# =============================
# MAIN LOOP
# =============================

run = st.button("Start Simulation")

if run:

    cycle = 0

    while True:

        # =========================
        # 1. PERCEPTION
        # =========================
        perceived = [obj["id"] for obj in state["objects"]]

        for obj in perceived:
            memory.get_or_create(obj)
            memory.link("self", obj)

        # =========================
        # 2. DECISION
        # =========================
        action, target = decide(memory, state)
        state["current_intent"] = action

        # =========================
        # 3. EXECUTION
        # =========================
        execute(action, target, state, memory)

        # =========================
        # 4. DECAY + RECOVERY
        # =========================
        memory.decay()
        state["atp"] = min(1.0, state["atp"] + 0.01)

        # =========================
        # 5. UI UPDATE
        # =========================

        # VITALS
        with vitals_box.container():
            st.subheader("Vitals")
            st.write("Cycle:", cycle)
            st.write("ATP:", round(state["atp"], 2))
            st.write("Coherence:", round(state["coherence"], 2))
            st.write("Intent:", state["current_intent"])

        # MEMORY
        with memory_box.container():
            st.subheader("Memory")
            for name, node in memory.nodes.items():
                st.write(f"{name} | V={round(node.voltage,2)} | links={len(node.links)}")

        # ENVIRONMENT
        with env_box.container():
            st.subheader("Environment")
            for obj in state["objects"]:
                st.write(obj)

        # LOG
        log_box.write(f"Action: {action} → Target: {target}")

        time.sleep(0.5)
        cycle += 1
