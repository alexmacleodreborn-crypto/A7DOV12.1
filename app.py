import streamlit as st
import matplotlib.pyplot as plt
from engine.organism import Organism
import numpy as np

# --- INIT ---
if "org" not in st.session_state:
    st.session_state.org = Organism()

org = st.session_state.org

# --- UI CONTROLS ---
st.title("A7DO – Life Engine (Streamlit)")

col1, col2 = st.columns(2)

with col1:
    steps = st.slider("Simulation Steps", 1, 50, 10)

with col2:
    speed = st.slider("dt (speed)", 0.01, 0.5, 0.1)

if st.button("Run Simulation Step"):
    for _ in range(steps):
        org.update(speed)

# --- VITALS ---
st.subheader("Vitals")

st.write({
    "time": round(org.time, 2),
    "cell_count": len(org.cells),
})

# --- VISUAL ---
st.subheader("Structure View")

xs = [c.position[0] for c in org.cells]
ys = [c.position[1] for c in org.cells]

colors = []
for c in org.cells:
    if c.type == "neural":
        colors.append("blue")
    elif c.type == "mesoderm":
        colors.append("red")
    else:
        colors.append("green")

fig, ax = plt.subplots()
ax.scatter(xs, ys, c=colors, s=5)

ax.set_xlim(-20, 20)
ax.set_ylim(-5, 30)

st.pyplot(fig)
