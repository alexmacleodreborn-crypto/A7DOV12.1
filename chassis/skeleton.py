# chassis/skeleton.py

import numpy as np
from .bone import Bone
from .registry import create_skeleton_registry
from .growth import global_structural_growth


class Skeleton:
    def __init__(self):
        self.bones = {}
        self.time = 0

        self._build()

    # -----------------------------
    # FORCE 2D
    # -----------------------------
    def _to_2d(self, v):
        return np.array([v[0], v[1], 0.0])

    # -----------------------------
    # BUILD FROM REGISTRY
    # -----------------------------
    def _build(self):
        for b in create_skeleton_registry():
            bone = Bone(
                bone_id=b["id"],
                name=b["name"],
                parent_id=b["parent"],
                start=self._to_2d(b["start"]),
                end=self._to_2d(b["end"]),
                development=b["dev"]
            )
            self.bones[bone.id] = bone

    # -----------------------------
    # ACTIVE BONES ONLY
    # -----------------------------
    def get_active_bones(self):
        return {
            k: b for k, b in self.bones.items()
            if b.exists
        }

    # -----------------------------
    # UPDATE (GROWTH)
    # -----------------------------
    def update(self, t):
        self.time = t

        global_scale = global_structural_growth(t)

        for bone in self.bones.values():
            bone.update(t, global_scale)

        # -----------------------------
        # ROOT LOCK (CRITICAL)
        # -----------------------------
        root = self.bones.get("spine")

        if root and root.exists:
            offset = root.start.copy()

            for bone in self.get_active_bones().values():
                bone.start -= offset
                bone.end -= offset

    # -----------------------------
    # CENTER OF MASS
    # -----------------------------
    def center_of_mass(self):
        total_mass = 0
        weighted = np.zeros(3)

        for bone in self.get_active_bones().values():
            m = bone.mass
            weighted += bone.center() * m
            total_mass += m

        return weighted / total_mass if total_mass > 0 else weighted

    # -----------------------------
    # EXPORT STATE
    # -----------------------------
    def export_state(self):
        return {
            "time": self.time,
            "bones": [
                {
                    "id": b.id,
                    "start": b.start.tolist(),
                    "end": b.end.tolist(),
                    "mass": b.mass
                }
                for b in self.get_active_bones().values()
            ],
            "center_of_mass": self.center_of_mass().tolist()
        }
