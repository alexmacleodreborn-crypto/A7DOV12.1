import time
import streamlit as st
import matplotlib.pyplot as plt

from engine.life_system import LifeSystem


st.set_page_config(page_title="A7DO Layered Dashboard", layout="wide")
st.title("A7DO — Layer 01 → Layer 10 Connected Dashboard")


def ensure_system():
    if "life_system" not in st.session_state:
        st.session_state.life_system = LifeSystem()
    return st.session_state.life_system


def render_skeleton(state):
    fig, ax = plt.subplots()
    for bone in state.get("bones", []):
        if not bone.get("exists"):
            continue
        x = [bone["start"][0], bone["end"][0]]
        y = [bone["start"][1], bone["end"][1]]
        ax.plot(x, y)
    ax.set_title("Layer 01: Skeletal Chassis")
    ax.set_aspect("equal")
    ax.set_xlim(-2, 2)
    ax.set_ylim(-0.5, 2.5)
    return fig


def layer_connected(state):
    return {
        "Layer 01 — Skeletal Chassis": bool(state.get("bones")),
        "Layer 02 — Muscular Actuators": bool(state.get("muscles")),
        "Layer 03 — Kinematics & Dynamics": bool(state.get("bones")) and bool(state.get("muscles")),
        "Layer 04 — Reflex Hierarchy": bool(state.get("last_action")) or bool(state.get("motor_active")),
        "Layer 05 — Visceral Metabolism": state.get("atp") is not None,
        "Layer 06 — Sensory Array": "objects_physical" in state,
        "Layer 07 — Growth & State Adaptation": state.get("cells", 0) > 0,
        "Layer 08 — Morphological Sync": bool(state.get("center_of_mass")) and bool(state.get("bones")),
        "Layer 09 — Vocal & Acoustic Sync": state.get("phase") == "infant",
        "Layer 10 — Cognitive Archive": state.get("memory_nodes", 0) > 0,
    }


system = ensure_system()

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("Step"):
        system.step_cycle()
with col2:
    auto = st.toggle("Auto Run", value=False)
with col3:
    dt = st.slider("Step size", min_value=0.01, max_value=0.5, value=0.1, step=0.01)

if auto:
    system.update(dt)
    time.sleep(0.05)
    st.rerun()

state = system.get_state()

st.subheader("Global State")
st.json(
    {
        "time": round(state.get("time", 0.0), 2),
        "phase": state.get("phase"),
        "heartbeat": round(state.get("heartbeat", 0.0), 2),
        "maternal_heartbeat": state.get("maternal_heartbeat"),
        "cells": state.get("cells"),
        "bones": len(state.get("bones", [])),
        "muscles": len(state.get("muscles", [])),
        "memory_nodes": state.get("memory_nodes", 0),
        "atp": round(state.get("atp", 0.0), 3),
        "coherence": round(state.get("coherence", 0.0), 3),
        "last_action": state.get("last_action"),
    }
)

st.subheader("Layer Connectivity (01 → 10)")
connect = layer_connected(state)
for layer_name, ok in connect.items():
    st.write(f"{'✅' if ok else '⚪'} {layer_name}")

left, right = st.columns([2, 1])
with left:
    st.subheader("Body Structure")
    st.pyplot(render_skeleton(state))
with right:
    st.subheader("Center of Mass")
    st.write(state.get("center_of_mass"))
    st.subheader("Targeting")
    st.write(
        {
            "target_object": state.get("target_object"),
            "held_object": state.get("held_object"),
            "motor_active": state.get("motor_active"),
        }
    )
