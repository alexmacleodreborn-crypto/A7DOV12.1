# app.py

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.a7do_brain import A7DO
from chassis.skeleton import Skeleton
from chassis.muscular_system import MuscularSystem


DEFAULT_DEVELOPMENT_TIME = 160.0
DT = 0.1


def initialize_system(development_time: float = DEFAULT_DEVELOPMENT_TIME) -> A7DO:
    """Create a ready-to-use A7DO system with visible/controllable current limbs."""
    brain = A7DO()
    skeleton = Skeleton()
    muscles = MuscularSystem(skeleton)
    brain.initialize_body(skeleton, muscles)

    # Start the dashboard from a mature-enough body state so all registered limbs
    # are visible and controllable immediately. The user can still reset and step.
    brain.state["time"] = float(development_time)
    skeleton.update(brain.state["time"])
    muscles.update(brain.state["time"], brain.state)

    brain.state["objects"] = [
        {"id": "cube"},
        {"id": "ball"},
        {"id": "beacon"},
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
        {
            "id": "beacon",
            "position": np.array([-4.0, 2.0, 0.0]),
            "held": False,
        },
    ]

    brain.state.setdefault("sensor_events", [])
    brain.state.setdefault("manual_commands", [])
    return brain


def ensure_session() -> None:
    if "brain" not in st.session_state:
        st.session_state.brain = initialize_system()
        st.session_state.cycle = 0
        st.session_state.learning_log = []
        log_event("System initialized", "A7DO dashboard booted with camera, mic, limb, movement, and learning panels.")


def to_list(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.round(3).tolist()
    if isinstance(value, list):
        return [to_list(item) for item in value]
    if isinstance(value, dict):
        return {key: to_list(item) for key, item in value.items()}
    return value


def log_event(event: str, detail: str, category: str = "system") -> None:
    st.session_state.setdefault("learning_log", [])
    st.session_state.learning_log.insert(
        0,
        {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "category": category,
            "event": event,
            "detail": detail,
        },
    )
    st.session_state.learning_log = st.session_state.learning_log[:100]


def step_brain(brain: A7DO, cycles: int = 1, dt: float = DT) -> None:
    for _ in range(cycles):
        before_action = brain.selector.last_action
        brain.update(dt)
        st.session_state.cycle += 1
        after_action = brain.selector.last_action

        if after_action and after_action != before_action:
            log_event("Action selected", f"{after_action}", "learning")

    log_event("Simulation stepped", f"Advanced {cycles} cycle(s) by dt={dt}.", "movement")


def object_table(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for obj in state.get("objects_physical", []):
        rows.append(
            {
                "id": obj["id"],
                "position": to_list(obj["position"]),
                "held": obj["held"],
            }
        )
    return rows


def memory_table(memory) -> list[dict[str, Any]]:
    rows = []
    for name, node in memory.nodes.items():
        if name == "self":
            continue
        rows.append(
            {
                "object": name,
                "voltage": round(node.voltage, 3),
                "links": len(node.links),
                "metadata": to_list(node.metadata),
            }
        )
    return rows


def limb_table(brain: A7DO) -> list[dict[str, Any]]:
    rows = []
    for bone in brain.motor.skeleton.bones.values():
        rows.append(
            {
                "id": bone.id,
                "name": bone.name,
                "parent": bone.parent_id or "root",
                "exists": bone.exists,
                "controllable": bone.controllable,
                "load_bearing": bone.load_bearing,
                "length": round(float(bone.length()), 3),
                "mass": round(float(bone.mass), 3),
                "start": to_list(bone.start),
                "end": to_list(bone.end),
                "rotation": to_list(bone.rotation),
            }
        )
    return rows


def muscle_table(brain: A7DO) -> list[dict[str, Any]]:
    rows = []
    for muscle in brain.motor.muscles.muscles.values():
        rows.append(
            {
                "id": muscle.id,
                "name": muscle.name,
                "origin": muscle.origin_bone.id,
                "insertion": muscle.insertion_bone.id,
                "exists": muscle.exists,
                "active": muscle.active,
                "activation": round(float(muscle.activation), 3),
                "fatigue": round(float(muscle.fatigue), 3),
                "force_at_current_atp": round(float(muscle.compute_force(brain.state.get("atp", 1.0))), 3),
            }
        )
    return rows


def motor_summary(motor) -> dict[str, Any]:
    if motor is None:
        return {
            "active": False,
            "end_effector": None,
            "target_position": None,
        }

    return {
        "active": motor.state.active,
        "end_effector": motor.state.end_effector,
        "target_position": to_list(motor.state.target_position)
        if motor.state.target_position is not None
        else None,
        "error_vector": to_list(motor.state.error_vector)
        if motor.state.error_vector is not None
        else None,
    }


def build_body_figure(brain: A7DO) -> go.Figure:
    fig = go.Figure()
    skeleton = brain.motor.skeleton

    # Bones: show active bones brightly and dormant bones faintly so the dashboard
    # communicates the full registered body.
    for bone in skeleton.bones.values():
        color = "royalblue" if bone.exists else "rgba(120, 120, 120, 0.25)"
        width = 8 if bone.exists else 3
        dash = None if bone.exists else "dash"

        fig.add_trace(
            go.Scatter3d(
                x=[bone.start[0], bone.end[0]],
                y=[bone.start[1], bone.end[1]],
                z=[bone.start[2], bone.end[2]],
                mode="lines+markers+text",
                line=dict(color=color, width=width, dash=dash),
                marker=dict(size=4, color=color),
                text=["", bone.name],
                textposition="top center",
                name=f"Bone: {bone.name}",
                hovertext=[bone.id, bone.id],
                showlegend=False,
            )
        )

    # Muscle lines
    for muscle in brain.motor.muscles.muscles.values():
        origin = muscle.origin_bone.center()
        insert = muscle.insertion_bone.center()
        activation = float(muscle.activation)
        color = f"rgb({int(255 * activation)}, 50, {int(255 * (1 - activation))})" if muscle.exists else "rgba(160,160,160,0.25)"
        width = 3 + activation * 8 if muscle.exists else 2

        fig.add_trace(
            go.Scatter3d(
                x=[origin[0], insert[0]],
                y=[origin[1], insert[1]],
                z=[origin[2], insert[2]],
                mode="lines",
                line=dict(color=color, width=width),
                name=f"Muscle: {muscle.name}",
                hovertext=[muscle.name, muscle.name],
                showlegend=False,
            )
        )

    # Objects
    for obj in brain.state.get("objects_physical", []):
        pos = np.array(obj["position"], dtype=float)
        fig.add_trace(
            go.Scatter3d(
                x=[pos[0]],
                y=[pos[1]],
                z=[pos[2]],
                mode="markers+text",
                marker=dict(size=7, color="orange" if obj["held"] else "green"),
                text=[obj["id"]],
                textposition="top center",
                name=f"Object: {obj['id']}",
                showlegend=False,
            )
        )

    # Current motor target
    if brain.motor.state.target_position is not None:
        target = brain.motor.state.target_position
        fig.add_trace(
            go.Scatter3d(
                x=[target[0]],
                y=[target[1]],
                z=[target[2]],
                mode="markers+text",
                marker=dict(size=9, color="red", symbol="x"),
                text=["Target"],
                textposition="bottom center",
                name="Target",
                showlegend=False,
            )
        )

    com = brain.state.get("center_of_mass")
    if com is not None:
        fig.add_trace(
            go.Scatter3d(
                x=[com[0]],
                y=[com[1]],
                z=[com[2]],
                mode="markers+text",
                marker=dict(size=7, color="purple", symbol="diamond"),
                text=["COM"],
                textposition="bottom center",
                name="Center of Mass",
                showlegend=False,
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, b=0, t=20),
        height=650,
    )

    return fig


def render_controls(brain: A7DO) -> None:
    st.subheader("🎮 Movement + Limb Controls")

    sim_a, sim_b, sim_c, sim_d = st.columns(4)

    if sim_a.button("Step 1 Cycle", use_container_width=True):
        step_brain(brain, 1)
        st.rerun()

    if sim_b.button("Step 10 Cycles", use_container_width=True):
        step_brain(brain, 10)
        st.rerun()

    if sim_c.button("Step 100 Cycles", use_container_width=True):
        step_brain(brain, 100)
        st.rerun()

    if sim_d.button("Reset System", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("#### Direct limb target")
    controllable = [
        bone.id
        for bone in brain.motor.skeleton.bones.values()
        if bone.exists and bone.controllable
    ]

    if not controllable:
        st.warning("No controllable limbs are currently available. Step time forward until development reaches control thresholds.")
        return

    limb_col, x_col, y_col, z_col, send_col = st.columns([1.5, 1, 1, 1, 1.2])
    selected_limb = limb_col.selectbox("Limb / end-effector", controllable, index=0)
    x = x_col.number_input("Target X", value=5.0, step=0.5)
    y = y_col.number_input("Target Y", value=15.0, step=0.5)
    z = z_col.number_input("Target Z", value=0.0, step=0.5)

    if send_col.button("Send target", use_container_width=True):
        target = np.array([x, y, z], dtype=float)
        brain.motor.set_target(selected_limb, target)
        brain.state["manual_motor_override"] = True
        brain.state.setdefault("manual_commands", []).append(
            {"limb": selected_limb, "target": target.tolist(), "cycle": st.session_state.cycle}
        )
        log_event("Manual limb target", f"{selected_limb} → {target.tolist()}", "movement")
        step_brain(brain, 1)
        st.rerun()

    st.markdown("#### Movement presets")
    preset_cols = st.columns(4)
    presets = {
        "Reach cube": ("right_arm", np.array([5.0, 0.0, 0.0])),
        "Reach ball": ("right_arm", np.array([2.0, 0.0, 1.5])),
        "Left scan": ("left_arm", np.array([-6.0, 12.0, 0.0])),
        "Right scan": ("right_arm", np.array([6.0, 12.0, 0.0])),
    }

    for index, (label, (limb, target)) in enumerate(presets.items()):
        disabled = limb not in controllable
        if preset_cols[index].button(label, disabled=disabled, use_container_width=True):
            brain.motor.set_target(limb, target)
            brain.state["manual_motor_override"] = True
            brain.state.setdefault("manual_commands", []).append(
                {"preset": label, "limb": limb, "target": target.tolist(), "cycle": st.session_state.cycle}
            )
            log_event("Movement preset", f"{label}: {limb} → {target.tolist()}", "movement")
            step_brain(brain, 5)
            st.rerun()


def render_sensors(brain: A7DO) -> None:
    st.subheader("📷 Camera + 🎙️ Microphone Inputs")
    st.caption(
        "Streamlit requests browser permission for camera and microphone. Captured inputs are logged into A7DO's learning/output stream for inspection."
    )

    cam_col, mic_col = st.columns(2)

    with cam_col:
        image = st.camera_input("Camera input / visual perception")
        if image is not None:
            size_kb = len(image.getvalue()) / 1024
            event = {
                "type": "camera",
                "name": image.name,
                "size_kb": round(size_kb, 2),
                "cycle": st.session_state.cycle,
            }
            if event not in brain.state.setdefault("sensor_events", []):
                brain.state["sensor_events"].append(event)
                log_event("Camera perception captured", f"{image.name}, {size_kb:.1f} KB", "sensor")
            st.success(f"Camera frame received: {image.name} ({size_kb:.1f} KB)")

    with mic_col:
        audio = st.audio_input("Microphone input / audio perception")
        if audio is not None:
            size_kb = len(audio.getvalue()) / 1024
            event = {
                "type": "microphone",
                "name": audio.name,
                "size_kb": round(size_kb, 2),
                "cycle": st.session_state.cycle,
            }
            if event not in brain.state.setdefault("sensor_events", []):
                brain.state["sensor_events"].append(event)
                log_event("Microphone sample captured", f"{audio.name}, {size_kb:.1f} KB", "sensor")
            st.audio(audio)
            st.success(f"Audio sample received: {audio.name} ({size_kb:.1f} KB)")


def render_learning_output(brain: A7DO) -> None:
    st.subheader("🧠 Learning + Output Console")

    out_a, out_b = st.columns([1, 1])

    with out_a:
        st.markdown("##### Learning events")
        log_df = pd.DataFrame(st.session_state.get("learning_log", []))
        if log_df.empty:
            st.info("No learning events yet.")
        else:
            st.dataframe(log_df, use_container_width=True, hide_index=True)

    with out_b:
        st.markdown("##### Current decision/output")
        st.json(
            {
                "last_action": brain.selector.last_action,
                "target_object": brain.state.get("target_object"),
                "held_object": brain.state.get("held_object"),
                "motor": motor_summary(brain.motor),
                "sensor_events": brain.state.get("sensor_events", []),
                "manual_commands": brain.state.get("manual_commands", [])[-10:],
            }
        )


def main() -> None:
    st.set_page_config(page_title="A7DO Full Control Dashboard", layout="wide")
    ensure_session()

    brain: A7DO = st.session_state.brain

    st.title("🧠🤖 A7DO Full Control Dashboard")
    st.markdown(
        "Control and inspect A7DO's body, limbs, movement, camera input, microphone input, memory, learning output, and internal state."
    )

    metric_cols = st.columns(8)
    metric_cols[0].metric("Cycle", st.session_state.cycle)
    metric_cols[1].metric("Time", round(brain.state["time"], 2))
    metric_cols[2].metric("ATP", round(brain.state["atp"], 3))
    metric_cols[3].metric("Coherence", round(brain.state["coherence"], 3))
    metric_cols[4].metric("Held", brain.state["held_object"] or "None")
    metric_cols[5].metric("Target", brain.state.get("target_object") or "None")
    metric_cols[6].metric("Motor Active", str(brain.motor.state.active))
    metric_cols[7].metric("Stable", str(brain.state.get("stable", "N/A")))

    tab_dashboard, tab_controls, tab_sensors, tab_learning, tab_state = st.tabs(
        [
            "Body Dashboard",
            "Movement Controls",
            "Camera + Mic",
            "Learning Output",
            "Internal State",
        ]
    )

    with tab_dashboard:
        visual_col, table_col = st.columns([1.35, 1])
        with visual_col:
            st.subheader("3D Body, Limbs, Muscles + Targets")
            st.plotly_chart(build_body_figure(brain), use_container_width=True)
        with table_col:
            st.subheader("All registered limbs")
            st.dataframe(pd.DataFrame(limb_table(brain)), use_container_width=True, hide_index=True)
            st.subheader("Muscles")
            st.dataframe(pd.DataFrame(muscle_table(brain)), use_container_width=True, hide_index=True)

    with tab_controls:
        render_controls(brain)

    with tab_sensors:
        render_sensors(brain)

    with tab_learning:
        render_learning_output(brain)

    with tab_state:
        state_col_a, state_col_b = st.columns(2)
        with state_col_a:
            st.subheader("Objects")
            st.dataframe(pd.DataFrame(object_table(brain.state)), use_container_width=True, hide_index=True)

            st.subheader("Memory Nodes")
            memory_rows = memory_table(brain.memory)
            if memory_rows:
                st.dataframe(pd.DataFrame(memory_rows), use_container_width=True, hide_index=True)
            else:
                st.info("Memory will populate as perception/update cycles run.")

            st.subheader("Motor State")
            st.json(motor_summary(brain.motor))

        with state_col_b:
            st.subheader("System Summary")
            st.json(
                {
                    "time": round(brain.state["time"], 2),
                    "atp": round(brain.state["atp"], 3),
                    "coherence": round(brain.state["coherence"], 3),
                    "agent_pos": brain.state.get("agent_pos"),
                    "center_of_mass": brain.state.get("center_of_mass"),
                    "stable": brain.state.get("stable"),
                    "held_object": brain.state["held_object"],
                    "target_object": brain.state.get("target_object"),
                    "objects": [obj["id"] for obj in brain.state.get("objects_physical", [])],
                }
            )

            st.subheader("Raw debug state")
            st.json(
                {
                    "objects": to_list(brain.state.get("objects")),
                    "objects_physical": to_list(brain.state.get("objects_physical", [])),
                    "sensor_events": to_list(brain.state.get("sensor_events", [])),
                    "manual_commands": to_list(brain.state.get("manual_commands", [])),
                }
            )

    st.caption(
        "This dashboard exposes A7DO's current registered limbs, movement targets, camera/mic browser inputs, memory state, learning events, and 3D body representation."
    )


if __name__ == "__main__":
    main()
