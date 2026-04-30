import json
from pathlib import Path


class SimulationExporter:
    """Collect and serialize simulation snapshots for external viewers."""

    def __init__(
        self,
        output_path,
        format_name="json",
        include_com=True,
        include_physics=False,
        snapshot_interval=0.5,
    ):
        self.output_path = Path(output_path)
        self.format_name = format_name
        self.include_com = include_com
        self.include_physics = include_physics
        self.snapshot_interval = snapshot_interval

        self._next_snapshot_time = 0.0
        self._payload = {
            "metadata": {
                "format": format_name,
                "snapshot_interval": snapshot_interval,
                "include_com": include_com,
                "include_physics": include_physics,
            },
            "frames": [],
        }

    def should_snapshot(self, sim_time):
        return sim_time >= self._next_snapshot_time

    def capture(self, sim_time, skeleton, muscles, state):
        frame = {
            "time": float(sim_time),
            "skeleton": self._build_skeleton_frame(skeleton),
            "muscles": self._build_muscle_frame(muscles),
            "objects": self._build_object_frame(state),
        }

        if self.include_com:
            frame["center_of_mass"] = state.get("center_of_mass")

        if self.include_physics:
            frame["physics"] = {
                "stable": state.get("stable"),
                "body_count": len(state.get("bodies", [])),
            }

        self._payload["frames"].append(frame)
        self._next_snapshot_time = sim_time + self.snapshot_interval
        self.flush()

    def flush(self):
        if self.format_name == "gltf":
            payload = self._to_gltf_animation(self._payload)
        else:
            payload = self._payload

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _build_skeleton_frame(self, skeleton):
        return {
            "hierarchy": [
                {
                    "id": bone.id,
                    "name": bone.name,
                    "parent": bone.parent_id,
                    "exists": bone.exists,
                    "start": bone.start.tolist(),
                    "end": bone.end.tolist(),
                }
                for bone in skeleton.bones.values()
            ],
            "export_state": skeleton.export_state(),
        }

    def _build_muscle_frame(self, muscles):
        return [
            {
                "id": m.id,
                "name": m.name,
                "exists": m.exists,
                "active": m.active,
                "activation": m.activation,
                "force": m.compute_force(1.0),
                "fatigue": m.fatigue,
                "origin": m.origin_bone.id,
                "insertion": m.insertion_bone.id,
            }
            for m in muscles.muscles.values()
        ]

    def _build_object_frame(self, state):
        objects = []
        for obj in state.get("objects_physical", []):
            pos = obj.get("position")
            objects.append(
                {
                    "id": obj.get("id"),
                    "position": pos.tolist() if hasattr(pos, "tolist") else pos,
                    "held": bool(obj.get("held", False)),
                    "grasp_state": "held" if obj.get("held", False) else "free",
                }
            )
        return objects

    def _to_gltf_animation(self, payload):
        """
        Lightweight glTF-compatible animation-like container.
        Consumers can map channels/samplers to full binary glTF later.
        """
        nodes = []
        node_map = {}

        first_frame = payload["frames"][0] if payload["frames"] else {}
        hierarchy = first_frame.get("skeleton", {}).get("hierarchy", [])

        for idx, bone in enumerate(hierarchy):
            node_map[bone["id"]] = idx
            nodes.append({"name": bone["name"], "extras": {"bone_id": bone["id"]}})

        channels = []
        for bone in hierarchy:
            channels.append(
                {
                    "target": {"node": node_map[bone["id"]], "path": "translation"},
                    "bone_id": bone["id"],
                    "sampler": "per_frame_endpoint",
                }
            )

        keyframes = []
        for frame in payload["frames"]:
            keyframes.append(
                {
                    "time": frame["time"],
                    "bones": {
                        b["id"]: {
                            "start": b["start"],
                            "end": b["end"],
                        }
                        for b in frame["skeleton"]["hierarchy"]
                    },
                    "muscles": frame["muscles"],
                    "objects": frame["objects"],
                    "center_of_mass": frame.get("center_of_mass"),
                    "physics": frame.get("physics"),
                }
            )

        return {
            "asset": {"version": "2.0", "generator": "A7DO SimulationExporter"},
            "nodes": nodes,
            "animations": [{"name": "skeleton_motion", "channels": channels}],
            "extras": {"frames": keyframes, "metadata": payload["metadata"]},
        }
