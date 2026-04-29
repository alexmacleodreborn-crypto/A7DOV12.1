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
        for bone in self.skeleton.bones.values():
            self.bodies.append(RigidBody(bone))

    def update(self, dt, state):
        total_force = 0

        for body in self.bodies:
            # gravity
            gravity_force = GRAVITY * body.mass
            body.apply_force(gravity_force)

        # apply muscle forces
        for m in self.muscles.muscles.values():
            if not m.active:
                continue

            force = m.compute_force(state["atp"])
            total_force += force

            direction = (
                m.insertion_bone.center() -
                m.origin_bone.center()
            )

            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)

            for body in self.bodies:
                if body.bone == m.insertion_bone:
                    body.apply_force(direction * force)

        # integrate
        step(self.bodies, dt)

        # collisions
        for body in self.bodies:
            handle_ground_collision(body)

        # balance check
        com = compute_center_of_mass(self.bodies)

        feet = [
            b.position for b in self.bodies
            if "leg" in b.bone.id or "foot" in b.bone.id
        ]

        if len(feet) > 0:
            support = support_polygon(feet)
            stable = is_stable(com, support)
        else:
            stable = False

        # write to USV
        state["center_of_mass"] = com.tolist()
        state["stable"] = stable
