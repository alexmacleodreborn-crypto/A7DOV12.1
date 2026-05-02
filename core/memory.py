# core/memory.py

"""
Cognitive Memory System
Voltage (V) + Resistance (R) based graph
"""

import time


class MemoryNode:
    def __init__(self, name):
        self.name = name

        # importance
        self.voltage = 1.0

        # connections: target -> resistance
        self.links = {}

        # metadata (used by perception)
        self.metadata = {}

        self.last_accessed = time.time()

    def strengthen(self, target):
        """
        Reduce resistance + increase importance
        """
        if target not in self.links:
            self.links[target] = 1.0
        else:
            self.links[target] *= 0.9

        self.voltage += 0.1


class Memory:
    def __init__(self):
        self.nodes = {}

    def get_or_create(self, name):
        if name not in self.nodes:
            self.nodes[name] = MemoryNode(name)
        return self.nodes[name]

    def link(self, a, b):
        node_a = self.get_or_create(a)
        node_b = self.get_or_create(b)

        node_a.strengthen(b)
        node_b.strengthen(a)

    def decay(self):
        for node in self.nodes.values():
            node.voltage *= 0.99

    def update(self, perceived):
        self.decay()
        for node in perceived:
            node.voltage += 0.1
