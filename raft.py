import threading


class Node:
    def __init__(self, nodes, node_id, timeout=2):
        self.nodes = nodes
        self.node_id = node_id
        self.state = "follower"  # initial state
        self.timeout = timeout
        self.leader_id = None
        self.timer = threading.Timer(self.timeout, self.become_candidate)

    def become_candidate(self):
        print(f"Node {self.node_id} becomes a candidate.")
        self.state = "candidate"
        self.leader_id = None
        self.start_election()

    def start_election(self):
        # Send RequestVote RPC to all other nodes
        votes = self.send_request_vote()

        if votes >= len(self.nodes) // 2 + 1:
            self.become_leader()
        else:
            # If not won, wait for a while and restart election
            self.timer = threading.Timer(self.timeout, self.become_candidate)
            self.timer.start()

    def become_leader(self):
        print(f"Node {self.node_id} becomes the leader.")
        self.state = "leader"
        self.leader_id = self.node_id
        self.send_heartbeat()
        self.timer.cancel()
        print(f"Node {self.node_id} timer stopped.")

    def send_request_vote(self):
        # In reality, this will involve RPC calls over the network
        votes = 0
        for node in self.nodes:
            if node != self and node.vote(self.node_id):
                votes += 1
        return votes

    def vote(self, candidate_id):
        # Vote for a candidate if not voted yet
        if self.leader_id is None:
            self.leader_id = candidate_id
            print(f"Node {self.node_id} votes for Node {candidate_id}.")
            return True
        return False

    def send_heartbeat(self):
        # In reality, this will involve RPC calls over the network
        for node in self.nodes:
            if node != self:
                node.receive_heartbeat(self.node_id)

    def receive_heartbeat(self, leader_id):
        self.timer.cancel()
        print(f"Node {self.node_id} timer stopped.")
        # self.timer = threading.Timer(self.timeout, self.become_candidate)
        # self.timer.start()

        # Recognize the new leader
        self.leader_id = leader_id
        print(f"Node {self.node_id} recognizes Node {leader_id} as the leader.")
