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

    def _build(self):
        for b in create_skeleton_registry():
            bone = Bone(
                bone_id=b["id"],
                name=b["name"],
                parent_id=b["parent"],
                start=b["start"],
                end=b["end"],
                development=b["dev"]
            )
            self.bones[bone.id] = bone

    def update(self, t):
        self.time = t
        global_scale = global_structural_growth(t)

        for bone in self.bones.values():
            bone.update(t, global_scale)

    def center_of_mass(self):
        total_mass = 0
        weighted = np.zeros(3)

        for bone in self.bones.values():
            if not bone.exists:
                continue

            m = bone.mass
            weighted += bone.center() * m
            total_mass += m

        return weighted / total_mass if total_mass > 0 else weighted

    def export_state(self):
        return {
            "time": self.time,
            "bones": [
                {
                    "id": b.id,
                    "exists": b.exists,
                    "controllable": b.controllable,
                    "start": b.start.tolist(),
                    "end": b.end.tolist(),
                    "mass": b.mass
                }
                for b in self.bones.values()
            ],
            "center_of_mass": self.center_of_mass().tolist()
        }
