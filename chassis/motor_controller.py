# chassis/motor_controller.py

import numpy as np
from .ik_solver import solve_ik
from .kinematics import forward_kinematics
from .motion_planner import plan_reach
from .controller_state import MotorState

class MotorController:
    def __init__(self, skeleton, muscles):
        self.skeleton = skeleton
        self.muscles = muscles
        self.state = MotorState()

    def set_target(self, bone_id, target_position):
        self.state.end_effector = bone_id
        self.state.target_position = np.array(target_position)
        self.state.active = True

    def _get_chain(self, bone_id):
        chain = []
        current = self.skeleton.bones[bone_id]

        while current:
            chain.append(current)
            parent_id = current.parent_id
            current = self.skeleton.bones.get(parent_id)

        return list(reversed(chain))

    def update(self, t, state):
        if not self.state.active:
            return

        chain = self._get_chain(self.state.end_effector)

        # current position
        current_pos = forward_kinematics(chain)

        # path planning
        path = plan_reach(current_pos, self.state.target_position)

        for target in path:
            solve_ik(chain, target)

        # compute error
        final_pos = forward_kinematics(chain)
        error = np.linalg.norm(self.state.target_position - final_pos)

        if error < 0.05:
            self.state.active = False

        # map rotations → muscle activation
        self._apply_muscle_activation(chain)

    def _apply_muscle_activation(self, chain):
        for bone in chain:
            for muscle in self.muscles.muscles.values():
                if not muscle.active:
                    continue

                if muscle.insertion_bone == bone:
                    muscle.activation = min(1.0, muscle.activation + 0.1)
