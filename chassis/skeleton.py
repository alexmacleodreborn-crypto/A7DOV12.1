# chassis/skeleton.py

import numpy as np
from .bone import Bone
from .growth import early_growth, mid_growth, late_growth


def to_2d(vec):
    """Force 2D (z = 0)"""
    return [vec[0], vec[1], 0.0]


class Skeleton:
    def __init__(self):
        self.bones = {}

        self._build_skeleton()

    # -----------------------------
    # BUILD FULL BODY (2D)
    # -----------------------------
    def _build_skeleton(self):

        def dev(t_start, t_control, t_load, curve):
            return {
                "t_start": t_start,
                "t_control": t_control,
                "t_load": t_load,
                "growth_curve": curve
            }

        # -----------------------------
        # SPINE (ROOT)
        # -----------------------------
        self._add_bone(
            "spine",
            None,
            [0, 0],
            [0, 5],
            dev(0, 80, 100, early_growth)
        )

        # -----------------------------
        # HEAD
        # -----------------------------
        self._add_bone(
            "head",
            "spine",
            [0, 5],
            [0, 7],
            dev(10, 90, 110, early_growth)
        )

        # -----------------------------
        # LEFT ARM
        # -----------------------------
        self._add_bone(
            "left_upper_arm",
            "spine",
            [0, 4],
            [-2, 4],
            dev(20, 100, 120, mid_growth)
        )

        self._add_bone(
            "left_forearm",
            "left_upper_arm",
            [-2, 4],
            [-4, 4],
            dev(30, 110, 130, mid_growth)
        )

        self._add_bone(
            "left_hand",
            "left_forearm",
            [-4, 4],
            [-5, 4],
            dev(40, 120, 140, mid_growth)
        )

        # -----------------------------
        # RIGHT ARM
        # -----------------------------
        self._add_bone(
            "right_upper_arm",
            "spine",
            [0, 4],
            [2, 4],
            dev(20, 100, 120, mid_growth)
        )

        self._add_bone(
            "right_forearm",
            "right_upper_arm",
            [2, 4],
            [4, 4],
            dev(30, 110, 130, mid_growth)
        )

        self._add_bone(
            "right_hand",
            "right_forearm",
            [4, 4],
            [5, 4],
            dev(40, 120, 140, mid_growth)
        )

        # -----------------------------
        # LEFT LEG
        # -----------------------------
        self._add_bone(
            "left_thigh",
            "spine",
            [0, 0],
            [-1, -3],
            dev(25, 100, 130, late_growth)
        )

        self._add_bone(
            "left_shin",
            "left_thigh",
            [-1, -3],
            [-1, -6],
            dev(35, 110, 140, late_growth)
        )

        self._add_bone(
            "left_foot",
            "left_shin",
            [-1, -6],
            [-2, -7],
            dev(45, 120, 150, late_growth)
        )

        # -----------------------------
        # RIGHT LEG
        # -----------------------------
        self._add_bone(
            "right_thigh",
            "spine",
            [0, 0],
            [1, -3],
            dev(25, 100, 130, late_growth)
        )

        self._add_bone(
            "right_shin",
            "right_thigh",
            [1, -3],
            [1, -6],
            dev(35, 110, 140, late_growth)
        )

        self._add_bone(
            "right_foot",
            "right_shin",
            [1, -6],
            [2, -7],
            dev(45, 120, 150, late_growth)
        )

    # -----------------------------
    # ADD BONE
    # -----------------------------
    def _add_bone(self, bone_id, parent_id, start, end, development):
        bone = Bone(
            bone_id,
            bone_id,
            parent_id,
            to_2d(start),
            to_2d(end),
            development
        )
        self.bones[bone_id] = bone

    # -----------------------------
    # UPDATE (GROWTH)
    # -----------------------------
    def update(self, t):
        global_scale = self._global_growth(t)

        for bone in self.bones.values():
            bone.update(t, global_scale)

    # -----------------------------
    # GLOBAL GROWTH CURVE
    # -----------------------------
    def _global_growth(self, t):
        return 1 / (1 + np.exp(-0.05 * (t - 60)))

    # -----------------------------
    # GET ACTIVE BONES (FOR RENDER)
    # -----------------------------
    def get_active_bones(self):
        return [b for b in self.bones.values() if b.exists]
