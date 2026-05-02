# app.py

import time
import numpy as np

from core.a7do_brain import A7DO
from chassis.skeleton import Skeleton
from chassis.muscular_system import MuscularSystem


# -----------------------------
# DEBUG HELPERS
# -----------------------------
def print_header(cycle):
    print("\n" + "=" * 60)
    print(f"🧠 A7DO CYCLE {cycle}")
    print("=" * 60)


def print_state(state):
    print("\n📊 STATE")
    print(f"Time:        {round(state['time'], 2)}")
    print(f"ATP:         {round(state['atp'], 3)}")
    print(f"Coherence:   {round(state['coherence'], 3)}")
    print(f"Held Object: {state['held_object']}")
    print(f"Target:      {state.get('target_object')}")


def print_objects(state):
    print("\n📦 OBJECTS")
    for obj in state.get("objects_physical", []):
        pos = np.round(obj["position"], 2)
        print(f" - {obj['id']} @ {pos} | held={obj['held']}")


def print_memory(memory):
    print("\n🧠 MEMORY")
    for name, node in memory.nodes.items():
        if name == "self":
            continue

        print(
            f" - {name} | V={round(node.voltage,3)} | links={len(node.links)}"
        )


def print_action(action):
    print("\n🎯 ACTION")
    print(f"Selected: {action}")


# -----------------------------
# INITIAL SETUP
# -----------------------------
print("\n🚀 Initialising A7DO...\n")

brain = A7DO()

# 🦴 build physical body
skeleton = Skeleton()
muscles = MuscularSystem(skeleton)

brain.initialize_body(skeleton, muscles)

# -----------------------------
# SPAWN WORLD
# -----------------------------
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

# -----------------------------
# MAIN LOOP
# -----------------------------
cycle = 0

while True:
    print_header(cycle)

    # -----------------------------
    # RUN ORGANISM
    # -----------------------------
    brain.update(0.1)

    # -----------------------------
    # DEBUG OUTPUT
    # -----------------------------
    print_state(brain.state)

    if hasattr(brain, "selector") and brain.selector.last_action:
        print_action(brain.selector.last_action)

    print_objects(brain.state)

    if hasattr(brain, "memory"):
        print_memory(brain.memory)

    # -----------------------------
    # EXTRA DEBUG (BODY)
    # -----------------------------
    if brain.motor:
        print("\n🦾 MOTOR")
        state = brain.motor.state
        if state.active:
            print(f"Target Bone: {state.end_effector}")
            print(f"Target Pos:  {np.round(state.target_position, 2)}")
        else:
            print("Motor idle")

    # -----------------------------
    # SYSTEM HEALTH
    # -----------------------------
    print("\n⚙️ SYSTEM")
    print(f"Cells (engine): {len(brain.organism.cells) if hasattr(brain.organism, 'cells') else 'N/A'}")
    print(f"Objects:        {len(brain.state['objects_physical'])}")

    # -----------------------------
    # LOOP CONTROL
    # -----------------------------
    time.sleep(0.1)
    cycle += 1
