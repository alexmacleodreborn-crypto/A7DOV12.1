# app.py

import numpy as np
import streamlit as st

from core.a7do_brain import A7DO
from chassis.skeleton import Skeleton
from chassis.muscular_system import MuscularSystem


def initialize_system():
    brain = A7DO()
    skeleton = Skeleton()
    muscles = MuscularSystem(skeleton)
    brain.initialize_body(skeleton, muscles)

    brain.state["objects"] = [
        {"id": "cube"},
        {"id": "ball"},
    ]

    brain.state["objects_physical"] = [
        {
            "id": "cube",
            "position": np.array([5.0, 0.0, 0.0]),
            "held": False,
        },
        {
            "id": "ball",
            "position": np.array([2.0, 0.0, 1.5]),
            "held": False,
        },
    ]

    return brain


def object_table(state):
    rows = []
    for obj in state.get("objects_physical", []):
        rows.append({
            "id": obj["id"],
            "position": list(np.round(obj["position"], 2)),
            "held": obj["held"],
        })
    return rows


def memory_table(memory):
    rows = []
    for name, node in memory.nodes.items():
        if name == "self":
            continue
        rows.append({
            "object": name,
            "voltage": round(node.voltage, 3),
            "links": len(node.links),
            "metadata": node.metadata,
        })
    return rows


def motor_summary(motor):
    if motor is None:
        return {
            "active": False,
            "end_effector": None,
            "target_position": None,
        }

    return {
        "active": motor.state.active,
        "end_effector": motor.state.end_effector,
        "target_position": list(np.round(motor.state.target_position, 2))
        if motor.state.target_position is not None
        else None,
    }


def main():
    st.set_page_config(page_title="A7DO System Viewer", layout="wide")

    if "brain" not in st.session_state:
        st.session_state.brain = initialize_system()
        st.session_state.cycle = 0
        st.session_state.last_action = None

    brain = st.session_state.brain

    st.title("🧠 A7DO System Viewer")
    st.markdown(
        "Use the controls below to step the organism and inspect the full system state."
    )

    left, center, right = st.columns([1, 1, 1])

    left.metric("Cycle", st.session_state.cycle)
    left.metric("Time", round(brain.state["time"], 2))
    left.metric("ATP", round(brain.state["atp"], 3))

    center.metric("Coherence", round(brain.state["coherence"], 3))
    center.metric("Held Object", brain.state["held_object"] or "None")
    center.metric("Target Object", brain.state.get("target_object") or "None")

    right.metric(
        "Engine Cells",
        len(brain.organism.cells) if hasattr(brain.organism, "cells") else "N/A",
    )
    right.metric("Total Objects", len(brain.state.get("objects_physical", [])))
    right.metric("Motor Active", str(brain.motor.state.active))

    with st.expander("Controls"):
        col_a, col_b, col_c = st.columns(3)
        if col_a.button("Step 1 Cycle"):
            brain.update(0.1)
            st.session_state.cycle += 1

        if col_b.button("Step 10 Cycles"):
            for _ in range(10):
                brain.update(0.1)
                st.session_state.cycle += 1

        if col_c.button("Reset System"):
            st.session_state.clear()
            st.experimental_rerun()

    st.divider()

    st.subheader("System Summary")
    st.write(
        {
            "time": round(brain.state["time"], 2),
            "atp": round(brain.state["atp"], 3),
            "coherence": round(brain.state["coherence"], 3),
            "held_object": brain.state["held_object"],
            "target_object": brain.state.get("target_object"),
            "objects": [obj["id"] for obj in brain.state.get("objects_physical", [])],
        }
    )

    st.subheader("Objects")
    st.table(object_table(brain.state))

    st.subheader("Memory Nodes")
    st.table(memory_table(brain.memory))

    st.subheader("Motor State")
    st.json(motor_summary(brain.motor))

    st.subheader("Debug Output")
    if brain.selector.last_action:
        st.write(f"**Last action:** {brain.selector.last_action}")

    st.write("### Internal State")
    st.json({
        "agent_pos": brain.state.get("agent_pos"),
        "objects": brain.state.get("objects"),
        "objects_physical": [
            {"id": o["id"], "position": list(o["position"]), "held": o["held"]}
            for o in brain.state.get("objects_physical", [])
        ],
        "target_object": brain.state.get("target_object"),
        "held_object": brain.state.get("held_object"),
    })

    st.caption(
        "This Streamlit view shows the full A7DO system state, including perception, memory, motor target, and current world objects."
    )


if __name__ == "__main__":
    main()

