# core/state.py

"""
Unified State Vector (USV)

This is the single source of truth for the organism.
Everything reads/writes here.
"""

state = {

    # =========================
    # PHYSICAL / ENVIRONMENT
    # =========================
    "objects": [
        {
            "id": "cube",
            "pos": [2, 2],
            "held": False
        }
    ],

    "grid_size": 10,

    # =========================
    # AGENT BODY (SIMPLIFIED)
    # =========================
    "agent_pos": [5, 5],

    # =========================
    # ENERGY SYSTEM
    # =========================
    "atp": 1.0,

    # =========================
    # COGNITIVE SYSTEM
    # =========================
    "coherence": 1.0,
    "current_intent": None,

    # =========================
    # INTERACTION STATE
    # =========================
    "held_object": None,
    "last_action_success": False,

    # =========================
    # DEBUG / TRACKING
    # =========================
    "cycle": 0
}
