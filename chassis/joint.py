# chassis/joint.py

class Joint:
    def __init__(self, parent_id, child_id, joint_type="hinge", limits=None):
        self.parent_id = parent_id
        self.child_id = child_id
        self.joint_type = joint_type

        # rotation limits in degrees
        self.limits = limits or {
            "x": (-180, 180),
            "y": (-180, 180),
            "z": (-180, 180),
        }
