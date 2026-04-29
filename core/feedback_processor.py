# core/feedback_processor.py

def process_feedback(success, action, target, memory, state):
    if target is None:
        return

    node = memory.get_or_create(target)

    if success:
        # reinforce success
        memory.link("self", target)
        node.voltage += 0.2

        state["coherence"] = min(1.0, state["coherence"] + 0.02)

    else:
        # penalise failure
        if target in node.links:
            node.links[target] *= 1.1

        state["coherence"] *= 0.98
