# chassis/muscle_registry.py

def create_muscle_registry(bones):
    return [
        {
            "id": "bicep_left",
            "name": "Left Bicep",
            "origin": "spine_top",
            "insertion": "left_arm",
            "max_force": 100,
            "dev": {
                "t_start": 40,
                "t_activation": 110
            }
        },
        {
            "id": "bicep_right",
            "name": "Right Bicep",
            "origin": "spine_top",
            "insertion": "right_arm",
            "max_force": 100,
            "dev": {
                "t_start": 40,
                "t_activation": 110
            }
        }
    ]
