# chassis/registry.py

from .growth import early_growth, mid_growth, late_growth

def create_skeleton_registry():
    return [
        {
            "id": "spine_base",
            "name": "Spine Base",
            "parent": None,
            "start": (0, 0, 0),
            "end": (0, 10, 0),
            "dev": {
                "t_start": 5,
                "t_control": 80,
                "t_load": 120,
                "growth_curve": early_growth
            }
        },
        {
            "id": "spine_top",
            "name": "Spine Top",
            "parent": "spine_base",
            "start": (0, 10, 0),
            "end": (0, 25, 0),
            "dev": {
                "t_start": 10,
                "t_control": 90,
                "t_load": 130,
                "growth_curve": mid_growth
            }
        },
        {
            "id": "left_arm",
            "name": "Left Arm",
            "parent": "spine_top",
            "start": (0, 20, 0),
            "end": (-15, 15, 0),
            "dev": {
                "t_start": 30,
                "t_control": 110,
                "t_load": 150,
                "growth_curve": late_growth
            }
        },
        {
            "id": "right_arm",
            "name": "Right Arm",
            "parent": "spine_top",
            "start": (0, 20, 0),
            "end": (15, 15, 0),
            "dev": {
                "t_start": 30,
                "t_control": 110,
                "t_load": 150,
                "growth_curve": late_growth
            }
        }
    ]
