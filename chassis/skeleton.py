# chassis/skeleton.py

import numpy as np
from .bone import Bone
from .registry import create_base_skeleton
from .growth import structural_growth


class Skeleton:
    def __init__(self):
        self.bones = {}
        self.time = 0
        self.scale_factor = 1.0

        self._build()

    def _build(self):
        base = create_base_skeleton()

        for b in base:
            bone = Bone(
                bone_id=b["id"],
                name=b["name"],
                parent_id=b["parent"],
                start=b["start"],
                end=b["end"],
            )
            self.bones[bone.id] = bone

    def update(self, t):
        """
        Main update loop (called every frame / heartbeat)
        """
        self.time = t

        new_scale = structural_growth(t)

        # scale delta (important: avoid compounding)
        if self.scale_factor == 0:
            ratio = 1
        else:
            ratio = new_scale / self.scale_factor

        for bone in self.bones.values():
            bone.scale(ratio)

        self.scale_factor = new_scale

    def center_of_mass(self):
        total_mass = 0
        weighted_sum = np.zeros(3)

        for bone in self.bones.values():
            m = bone.mass
            c = bone.center()

            weighted_sum += c * m
            total_mass += m

        return weighted_sum / total_mass if total_mass > 0 else weighted_sum

    def export_state(self):
        return {
            "bones": [
                {
                    "id": b.id,
                    "start": b.start.tolist(),
                    "end": b.end.tolist(),
                    "mass": b.mass,
                }
                for b in self.bones.values()
            ],
            "center_of_mass": self.center_of_mass().tolist(),
            "scale": self.scale_factor,
            "time": self.time,
        }
