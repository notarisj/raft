import time

from node import RaftNode

if __name__ == "__main__":

    ports = {'node1': 8000, 'node2': 8001, 'node3': 8002}
    nodes = ['node1', 'node2', 'node3']

    raft_node = RaftNode('node2', ports, nodes)
    time.sleep(0.5)
    raft_node.start()
