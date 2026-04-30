# app.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from engine.organism import Organism
from anatomy.L01_Skeleton import SkeletonManifold


# -----------------------------
# INIT SYSTEM
# -----------------------------
if "org" not in st.session_state:
    st.session_state.org = Organism()

if "skeleton" not in st.session_state:
    st.session_state.skeleton = SkeletonManifold()

org = st.session_state.org
skeleton = st.session_state.skeleton


# -----------------------------
# UI
# -----------------------------
st.title("🧠 A7DO – Cell → Skeleton Bridge")

col1, col2 = st.columns(2)

steps = col1.slider("Steps", 1, 50, 10)
dt = col2.slider("dt", 0.01, 0.5, 0.1)

run = st.button("Run")


# -----------------------------
# RUN SIMULATION
# -----------------------------
if run:
    for _ in range(steps):
        org.update(dt)


# -----------------------------
# VITALS
# -----------------------------
st.write({
    "time": round(org.time, 2),
    "cells": len(org.cells),
})


# -----------------------------
# BUILD CONTROL SIGNALS
# -----------------------------
def extract_body_signals(cells):
    positions = np.array([c.position for c in cells])

    if len(positions) == 0:
        return None

    signals = {}

    signals["height"] = positions[:,1].max()
    signals["center_x"] = positions[:,0].mean()

    # detect spread (for arms)
    signals["width"] = positions[:,0].std()

    return signals


signals = extract_body_signals(org.cells)


# -----------------------------
# DRIVE L01 SKELETON
# -----------------------------
def update_skeleton_from_cells(skeleton, signals):
    if not signals:
        return

    scale = max(0.5, min(2.0, signals["height"] / 10))

    # update geometry scale
    skeleton.generate_current_geometry(scale)


update_skeleton_from_cells(skeleton, signals)


# -----------------------------
# DRAW REAL SKELETON (2D)
# -----------------------------
st.subheader("L01 Skeleton (Driven by Cells)")

fig, ax = plt.subplots()

for bone_id, bone in skeleton.registry.items():
    p1 = bone.pos_proximal
    p2 = bone.pos_distal

    if p1 is None or p2 is None:
        continue

    xs = [p1[0], p2[0]]
    ys = [p1[1], p2[1]]

    ax.plot(xs, ys, linewidth=2)


# Optional: overlay cells
if st.checkbox("Show Cells", False):
    xs = [c.position[0] for c in org.cells]
    ys = [c.position[1] for c in org.cells]
    ax.scatter(xs, ys, s=2, alpha=0.2)


ax.set_xlim(-20, 20)
ax.set_ylim(-5, 30)

st.pyplot(fig)