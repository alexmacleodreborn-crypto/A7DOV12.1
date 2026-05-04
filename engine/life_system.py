# engine/life_system.py

"""
Master Life System Orchestrator
Coordinates all engines through developmental phases
"""

import numpy as np
from .organism import Organism
from chassis.skeleton import Skeleton
from chassis.muscular_system import MuscularSystem
from core.a7do_brain import A7DO


class LifeSystem:
    def __init__(self):
        self.t = 0.0

        # Phase tracking
        self.phase = "zygote"  # zygote → embryo → fetus → birth → infant

        # Biological engine
        self.organism = Organism()

        # Physical engines (initialized later)
        self.skeleton = None
        self.muscles = None
        self.brain = None

        # Development metrics
        self.heartbeat = 60  # BPM
        self.maternal_heartbeat = 72

    def update(self, dt):
        """Master update - coordinates all systems through phases"""
        self.t += dt

        # Phase transitions
        if self.phase == "zygote" and self.t > 5:
            self.phase = "embryo"

        elif self.phase == "embryo" and self.t > 30:
            self.phase = "fetus"
            self._initialize_skeleton()

        elif self.phase == "fetus" and self.t > 120:
            self.phase = "birth"
            self._initialize_muscles()

        elif self.phase == "birth" and self.t > 150:
            self.phase = "infant"
            self._initialize_brain()

        # Update active systems
        self._update_active_systems(dt)

    def _initialize_skeleton(self):
        """Phase 2: Skeleton formation"""
        self.skeleton = Skeleton()

    def _initialize_muscles(self):
        """Phase 3: Muscular system"""
        if self.skeleton:
            self.muscles = MuscularSystem(self.skeleton)

    def _initialize_brain(self):
        """Phase 4: Cognitive system"""
        if self.skeleton and self.muscles:
            self.brain = A7DO()
            self.brain.initialize_body(self.skeleton, self.muscles)

    def _update_active_systems(self, dt):
        """Update only systems that exist in current phase"""

        # Always update biological
        self.organism.update(dt)

        # Update heartbeat (gets faster with development)
        self.heartbeat = 60 + (self.t / 10)

        # Skeleton phase
        if self.skeleton and self.phase in ["fetus", "birth", "infant"]:
            self.skeleton.update(self.t)

        # Muscles phase
        if self.muscles and self.phase in ["birth", "infant"]:
            self.muscles.update(self.t, {"atp": 1.0})

        # Brain phase
        if self.brain and self.phase == "infant":
            self.brain.update(dt)

    def get_state(self):
        """Get complete system state for UI"""
        state = {
            "time": self.t,
            "phase": self.phase,
            "heartbeat": self.heartbeat,
            "maternal_heartbeat": self.maternal_heartbeat,
            "cells": len(self.organism.cells) if hasattr(self.organism, 'cells') else 0,
        }

        # Add skeleton data if exists
        if self.skeleton:
            active_bones = self.skeleton.get_active_bones()
            state["bones"] = [
                {
                    "id": b.id,
                    "name": b.name,
                    "start": b.start.tolist(),
                    "end": b.end.tolist(),
                    "exists": b.exists,
                    "mass": b.mass,
                }
                for b in active_bones.values()
            ]
            state["center_of_mass"] = self.skeleton.center_of_mass().tolist()

        # Add muscle data if exists
        if self.muscles:
            state["muscles"] = [
                {
                    "id": m.id,
                    "name": m.name,
                    "active": m.active,
                    "exists": m.exists,
                    "activation": m.activation,
                    "force": m.compute_force(1.0),
                }
                for m in self.muscles.muscles.values()
            ]

        # Add brain data if exists
        if self.brain:
            state.update({
                "atp": self.brain.state.get("atp", 0),
                "coherence": self.brain.state.get("coherence", 0),
                "held_object": self.brain.state.get("held_object"),
                "target_object": self.brain.state.get("target_object"),
                "objects_physical": self.brain.state.get("objects_physical", []),
                "memory_nodes": len(self.brain.memory.nodes),
                "last_action": self.brain.selector.last_action if self.brain.selector else None,
                "motor_active": self.brain.motor.state.active if self.brain.motor else False,
            })

        return state

    def step_cycle(self):
        """Step one development cycle"""
        self.update(0.1)

    def reset(self):
        """Reset to zygote phase"""
        self.__init__()