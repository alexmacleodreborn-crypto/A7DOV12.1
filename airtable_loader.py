import requests

from chassis.bone import Bone
from chassis.muscle import Muscle
from chassis.growth import early_growth, mid_growth, late_growth


class A7DOLoader:
    def __init__(self, api_key, base_id):
        self.api_key = api_key
        self.base_id = base_id
        self.base_url = f"https://api.airtable.com/v0/{base_id}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    # -----------------------------
    # FETCH
    # -----------------------------
    def fetch_table(self, table):
        url = f"{self.base_url}/{table}"
        records = []

        while url:
            res = requests.get(url, headers=self.headers)
            data = res.json()

            records.extend(data.get("records", []))

            offset = data.get("offset")
            if offset:
                url = f"{self.base_url}/{table}?offset={offset}"
            else:
                url = None

        return records

    # -----------------------------
    # CURVE MAPPING
    # -----------------------------
    def pick_curve(self, t):
        if t == "early":
            return early_growth
        elif t == "mid":
            return mid_growth
        elif t == "late":
            return late_growth
        return mid_growth

    # -----------------------------
    # MAIN LOAD
    # -----------------------------
    def load_all(self):
        bones_raw = self.fetch_table("Bones")
        dev_raw = self.fetch_table("Bone Development")
        curves_raw = self.fetch_table("Growth Curves")
        muscles_raw = self.fetch_table("Muscles")
        objects_raw = self.fetch_table("Objects")
        phases_raw = self.fetch_table("Development Phases")

        # -----------------------------
        # ID MAPPINGS
        # -----------------------------
        bone_lookup = {
            rec["id"]: rec["fields"].get("Bone ID")
            for rec in bones_raw
        }

        curve_lookup = {
            rec["id"]: rec["fields"]
            for rec in curves_raw
        }

        dev_lookup = {}
        for rec in dev_raw:
            f = rec["fields"]
            for b in f.get("Bone", []):
                dev_lookup[b] = f

        # -----------------------------
        # BUILD BONES
        # -----------------------------
        bones = {}

        for rec in bones_raw:
            f = rec["fields"]

            bone_id = f.get("Bone ID")
            if not bone_id:
                raise Exception(f"Missing Bone ID in {rec['id']}")

            # resolve parent
            parent_rec = f.get("Parent Bone", [None])[0]
            parent_id = bone_lookup.get(parent_rec)

            if parent_rec and not parent_id:
                raise Exception(f"Broken parent link for {bone_id}")

            # development
            dev = dev_lookup.get(rec["id"])
            if not dev:
                raise Exception(f"No development profile for {bone_id}")

            # curve
            curve_rec = dev.get("Growth Curve", [None])[0]
            curve_data = curve_lookup.get(curve_rec, {})
            curve_type = curve_data.get("Type", "mid")

            bone = Bone(
                bone_id=bone_id,
                name=f.get("Name", bone_id),
                parent_id=parent_id,
                start=[0, 0, 0],
                end=[
                    f.get("Axis X", 0),
                    f.get("Axis Y", 1),
                    f.get("Axis Z", 0),
                ],
                development={
                    "t_start": dev.get("t_start", 0),
                    "t_control": dev.get("t_control", 10),
                    "t_load": dev.get("t_load", 20),
                    "growth_curve": self.pick_curve(curve_type),
                },
            )

            bones[bone_id] = bone

        # -----------------------------
        # VALIDATE SKELETON
        # -----------------------------
        self._validate_no_cycles(bones)
        self._validate_orphans(bones)

        # -----------------------------
        # BUILD MUSCLES
        # -----------------------------
        muscles = {}

        for rec in muscles_raw:
            f = rec["fields"]

            origin_rec = f.get("origin_bone", [None])[0]
            insert_rec = f.get("insertion_bone", [None])[0]

            origin = bone_lookup.get(origin_rec)
            insert = bone_lookup.get(insert_rec)

            if origin not in bones or insert not in bones:
                raise Exception(f"Invalid muscle linkage: {f.get('name')}")

            muscle = Muscle(
                muscle_id=f.get("muscle_id"),
                name=f.get("name"),
                origin_bone=bones[origin],
                insertion_bone=bones[insert],
                max_force=f.get("max_force", 1.0),
                development={
                    "t_start": f.get("t_start", 0),
                    "t_activation": f.get("t_activation", 10),
                },
            )

            muscles[muscle.id] = muscle

        # -----------------------------
        # OBJECTS (SOFT VALIDATION)
        # -----------------------------
        objects = []

        for rec in objects_raw:
            f = rec["fields"]

            if "object_id" not in f:
                print(f"⚠️ Missing object_id in {rec['id']}")
                continue

            obj = SimpleObject(
                obj_id=f.get("object_id"),
                name=f.get("name"),
                mass=f.get("mass", 1.0),
                friction=f.get("friction", 0.5),
            )

            objects.append(obj)

        # -----------------------------
        # PHASES
        # -----------------------------
        phases = []

        for rec in phases_raw:
            f = rec["fields"]

            phases.append({
                "t_min": f.get("t_min", 0),
                "t_max": f.get("t_max", 100),
                "cognition": f.get("cognition_enabled", False),
                "interaction": f.get("interaction_enabled", False),
                "phase": f.get("phase"),
            })

        return {
            "bones": bones,
            "muscles": muscles,
            "objects": objects,
            "phases": phases,
        }

    # -----------------------------
    # VALIDATION
    # -----------------------------
    def _validate_no_cycles(self, bones):
        visited = set()

        def visit(bone_id, stack):
            if bone_id in stack:
                raise Exception(f"Cycle detected at {bone_id}")

            stack.add(bone_id)

            parent = bones[bone_id].parent_id
            if parent:
                visit(parent, stack)

            stack.remove(bone_id)

        for b in bones:
            visit(b, set())

    def _validate_orphans(self, bones):
        for bone in bones.values():
            if bone.parent_id and bone.parent_id not in bones:
                raise Exception(f"Orphan bone: {bone.id}")


# -----------------------------
# SIMPLE OBJECT
# -----------------------------
class SimpleObject:
    def __init__(self, obj_id, name, mass, friction):
        self.id = obj_id
        self.name = name
        self.mass = mass
        self.friction = friction

        self.position = [0.0, 0.0, 0.0]
        self.held = False