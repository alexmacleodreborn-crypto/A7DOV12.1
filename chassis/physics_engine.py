# chassis/physics_engine.py

import numpy as np
from .rigid_body import RigidBody
from .integrator import step
from .collision import handle_ground_collision
from .balance import compute_center_of_mass, support_polygon, is_stable

GRAVITY = np.array([0, -9.81, 0])


class PhysicsEngine:
    def __init__(self, skeleton, muscles):
        self.skeleton = skeleton
        self.muscles = muscles

        self.bodies = []

        self._build_bodies()

    def _build_bodies(self):
        self.bodies = []
        for bone in self.skeleton.bones.values():
            self.bodies.append(RigidBody(bone))

    def update(self, dt, state):
        # -----------------------------
        # RESET FORCES (CRITICAL FIX)
        # -----------------------------
        for body in self.bodies:
            if hasattr(body, "reset_forces"):
                body.reset_forces()
            else:
                body.force = np.zeros(3)

        # -----------------------------
        # APPLY GRAVITY
        # -----------------------------
        for body in self.bodies:
            body.apply_force(GRAVITY * body.mass)

        # -----------------------------
        # APPLY MUSCLE FORCES (FIXED)
        # -----------------------------
        for m in self.muscles.muscles.values():
            if not m.active:
                continue

            force = m.compute_force(state.get("atp", 1.0))

            direction = (
                m.insertion_bone.center() -
                m.origin_bone.center()
            )

            norm = np.linalg.norm(direction)
            if norm == 0:
                continue

            direction = direction / norm

            for body in self.bodies:
                if body.bone == m.insertion_bone:
                    body.apply_force(direction * force)

                elif body.bone == m.origin_bone:
                    body.apply_force(-direction * force)

        # -----------------------------
        # INTEGRATE MOTION
        # -----------------------------
        step(self.bodies, dt)

        # -----------------------------
        # SYNC BACK TO SKELETON (CRITICAL FIX)
        # -----------------------------
        for body in self.bodies:
            body.bone.position = body.position

        # -----------------------------
        # COLLISIONS
        # -----------------------------
        for body in self.bodies:
            handle_ground_collision(body)

        # -----------------------------
        # CENTER OF MASS + STABILITY
        # -----------------------------
        com = compute_center_of_mass(self.bodies)

        # safer foot detection
        feet = [
            b.position for b in self.bodies
            if getattr(b.bone, "is_support", False)
            or "foot" in b.bone.id.lower()
            or "leg" in b.bone.id.lower()
        ]

        stable = False
        if len(feet) > 0:
            support = support_polygon(feet)
            stable = is_stable(com, support)

        # -----------------------------
        # WRITE TO STATE (USV)
        # -----------------------------
        state["center_of_mass"] = com.tolist()
        state["stable"] = stable

        # 🔥 expose bodies to other systems (VERY IMPORTANT)
        state["bodies"] = self.bodies
