def create_initial_state():
    return {
        "time": 0.0,
        "agent_pos": [0, 0],
        "objects": [],
        "objects_physical": [],
        "held_object": None,
        "target_object": None,
        "atp": 1.0,
        "coherence": 1.0,
    }
