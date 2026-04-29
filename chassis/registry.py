# chassis/registry.py

def create_base_skeleton():
    return [
        {
            "id": "spine_base",
            "name": "Spine Base",
            "parent": None,
            "start": (0, 0, 0),
            "end": (0, 10, 0),
        },
        {
            "id": "spine_mid",
            "name": "Spine Mid",
            "parent": "spine_base",
            "start": (0, 10, 0),
            "end": (0, 20, 0),
        },
        {
            "id": "spine_top",
            "name": "Spine Top",
            "parent": "spine_mid",
            "start": (0, 20, 0),
            "end": (0, 30, 0),
        },
        {
            "id": "left_arm",
            "name": "Left Arm",
            "parent": "spine_top",
            "start": (0, 25, 0),
            "end": (-15, 20, 0),
        },
        {
            "id": "right_arm",
            "name": "Right Arm",
            "parent": "spine_top",
            "start": (0, 25, 0),
            "end": (15, 20, 0),
        },
    ]
