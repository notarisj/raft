# Initialize list of nodes with None
import time

from raft import Node

nodes = [None for _ in range(5)]

# Populate nodes with actual Node instances
for i in range(5):
    nodes[i] = Node(nodes, node_id=i)

# Start all nodes
for node in nodes:
    node.timer.start()

# Let it run for a while
time.sleep(50)

# Stop all nodes
for node in nodes:
    node.timer.cancel()
