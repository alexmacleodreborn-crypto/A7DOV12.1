# chassis/muscular_system.py

from .muscle import Muscle
from .muscle_registry import create_muscle_registry
from .muscle_dynamics import apply_fatigue, atp_drain


class MuscularSystem:
    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.muscles = {}

        self._build()

    def _build(self):
        registry = create_muscle_registry(self.skeleton.bones)

        for m in registry:
            origin_id = m["origin"]
            insertion_id = m["insertion"]

            # -----------------------------
            # SAFE LOOKUP (CRITICAL FIX)
            # -----------------------------
            origin_bone = self.skeleton.bones.get(origin_id)
            insertion_bone = self.skeleton.bones.get(insertion_id)

            if origin_bone is None or insertion_bone is None:
                print(f"[WARN] Muscle skipped: {m['id']} "
                      f"(missing bone: {origin_id} or {insertion_id})")
                continue

            muscle = Muscle(
                muscle_id=m["id"],
                name=m["name"],
                origin_bone=origin_bone,
                insertion_bone=insertion_bone,
                max_force=m["max_force"],
                development=m["dev"]
            )

            self.muscles[muscle.id] = muscle

    def update(self, t, state):
        atp = state.get("atp", 0.0)

        total_force = 0.0

        for m in self.muscles.values():
            m.update(t, atp)

            if not m.exists:
                continue

            force = m.compute_force(atp)
            total_force += force

            apply_fatigue(m, force)

        # -----------------------------
        # ATP DRAIN (SAFE)
        # -----------------------------
        state["atp"] -= atp_drain(total_force)
        state["atp"] = max(0.0, state["atp"])

    def activate_group(self, muscle_ids, level):
        for mid in muscle_ids:
            if mid in self.muscles:
                self.muscles[mid].activation = level

    def export_state(self):
        return {
            "muscles": [
                {
                    "id": m.id,
                    "active": m.active,
                    "force": m.compute_force(1.0),
                    "fatigue": m.fatigue
                }
                for m in self.muscles.values()
            ]
        }
