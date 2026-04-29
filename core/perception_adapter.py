# core/perception_adapter.py

def perceive(objects, memory):
    perceived = []

    for obj in objects:
        node = memory.get_or_create(obj.id)
        memory.link("self", obj.id)
        perceived.append(node)

    return perceived
