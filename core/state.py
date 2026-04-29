# core/state.py

state = {
    "objects": [
        {"id": "cube", "pos": [2, 2], "held": False}
    ],

    "grid_size": 10,

    # 🟩 obstacles (walls)
    "obstacles": [
        [4, 4], [4, 5], [4, 6],
        [5, 6], [6, 6]
    ],

    "agent_pos": [7, 7],

    "atp": 1.0,
    "coherence": 1.0,
    "current_intent": None,

    "held_object": None,
    "last_action_success": False,

    "cycle": 0
}
