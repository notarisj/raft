import argparse
from enum import Enum
import threading
import time
import random

from logger import MyLogger
from rpc.rpc_server import RPCServer
from rpc.rpc_client import RPCClient


class RaftState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


logger = MyLogger()


class RaftNode:

    def __init__(self, node_id, _ports, _nodes):
        self.election_timer = None
        self.heartbeat_timer = None
        logger.info(f"Initializing RaftNode with ID: {node_id}")
        self.node_id = node_id
        self.nodes = _nodes
        self.ports = _ports
        self.port = _ports[node_id]
        self.state = RaftState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = [{'term': 0, 'value': None}]
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {node: len(self.log) + 1 for node in self.nodes}
        self.match_index = {node: 0 for node in self.nodes}
        self.election_timeout = random.uniform(0.15, 3)  # Randomize the election timeout
        self.heartbeat_interval = 0.1
        self.election_lock = threading.Lock()
        self.leader_lock = threading.Lock()
        self.server = RPCServer(host='localhost', port=self.port)
        self.server.register_function(self.append_entries_rpc, 'append_entries')
        self.server.register_function(self.request_vote_rpc, 'request_vote')
        self.server_thread = threading.Thread(target=self.server.run)
        self.clients = {node: RPCClient(f"http://localhost:{_ports[node]}") for node in _nodes if node != node_id}
        self.election_in_progress = False

    def start(self):
        logger.info(f"Starting RaftNode with ID: {self.node_id}")
        self.server_thread.start()
        self.transition_to_follower(election_failed=True)

    def transition_to_follower(self, election_failed=False):
        logger.info(f"Transitioning RaftNode {self.node_id} to FOLLOWER state")
        self.state = RaftState.FOLLOWER
        self.voted_for = None
        self.reset_election_timer()
        if election_failed:
            self.schedule_election()

    def transition_to_candidate(self):
        logger.info(f"Transitioning RaftNode {self.node_id} to CANDIDATE state")
        self.state = RaftState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.reset_election_timer()
        self.start_election()

    def transition_to_leader(self):
        logger.info(f"Transitioning RaftNode {self.node_id} to LEADER state")
        self.state = RaftState.LEADER
        self.reset_election_timer()
        self.reset_heartbeat_timer()
        self.send_heartbeat()

    def reset_election_timer(self):
        logger.info(f"Resetting election timer for RaftNode {self.node_id}")
        self.election_lock.acquire()
        self.election_timer = time.time()
        self.election_lock.release()
        self.election_timeout = random.uniform(0.15, 0.3)  # Randomize the election timeout

    def reset_heartbeat_timer(self):
        logger.info(f"Resetting heartbeat timer for RaftNode {self.node_id}")
        self.leader_lock.acquire()
        self.heartbeat_timer = time.time()
        self.leader_lock.release()

    def schedule_election(self):
        if self.election_in_progress:
            return
        logger.info(f"Scheduling election for RaftNode {self.node_id} after {self.election_timeout} seconds")
        timer_thread = threading.Timer(self.election_timeout, self.transition_to_candidate)
        timer_thread.start()

    def start_election(self):
        if self.election_in_progress:
            return
        self.election_in_progress = True
        logger.info(f"Starting election for RaftNode {self.node_id}")
        votes_received = 1
        total_nodes = len(self.nodes)

        for node in self.nodes:
            if node != self.node_id:
                logger.info(f"Requesting vote from RaftNode {node} for RaftNode {self.node_id}")
                response = self.clients[node].call(
                    'request_vote', self.current_term, self.node_id, len(self.log) - 1,
                    self.log[-1]['term'] if self.log else 0
                )
                if response is None:
                    logger.info(f"Node {node} is unreachable")
                    continue
                if response['term'] > self.current_term:
                    logger.info(
                        f"RaftNode {node} has a higher term, transitioning RaftNode {self.node_id} to FOLLOWER state")
                    self.current_term = response['term']
                    self.transition_to_follower()
                    self.election_in_progress = False
                    return
                elif response['vote_granted']:
                    logger.info(f"Vote received from RaftNode {node} for RaftNode {self.node_id}")
                    votes_received += 1

        if votes_received > total_nodes // 2:
            logger.info(f"RaftNode {self.node_id} has received majority votes, transitioning to LEADER state")
            self.transition_to_leader()
            self.election_in_progress = False
        else:
            logger.info(f"RaftNode {self.node_id} has not received enough votes, transitioning to FOLLOWER state")
            self.election_in_progress = False
            self.transition_to_follower(election_failed=True)

    def send_heartbeat(self):
        logger.info(f"Sending heartbeat from RaftNode {self.node_id}")
        self.leader_lock.acquire()
        self.reset_heartbeat_timer()
        self.leader_lock.release()

        while self.state == RaftState.LEADER:
            for node in self.nodes:
                if node != self.node_id:
                    prev_log_index = self.next_index[node] - 1
                    prev_log_term = self.log[prev_log_index]['term'] if prev_log_index >= 0 else 0
                    entries = self.log[self.next_index[node]:]
                    try:
                        logger.info(f"Sending heartbeat to RaftNode {node}")
                        response = self.clients[node].call('append_entries', self.current_term, self.node_id,
                                                           prev_log_index, prev_log_term, entries, self.commit_index)
                        logger.info(f"Received response from node {node}: {response}")
                    except Exception as e:
                        logger.info(f"Failed to send heartbeat to {node}, error: {str(e)}")
                        continue
            time.sleep(self.heartbeat_interval)

    def update_commit_index(self):
        logger.info(f"Updating commit index for RaftNode {self.node_id}")
        sorted_match_indexes = sorted(self.match_index.values())
        majority_index = sorted_match_indexes[len(sorted_match_indexes) // 2]
        if majority_index > self.commit_index and self.log[majority_index]['term'] == self.current_term:
            self.commit_index = majority_index
            self.apply_log_entries()

    def apply_log_entries(self):
        logger.info(f"Applying log entries for RaftNode {self.node_id}")
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]
            # Apply the log entry to the state machine

    def append_entries_rpc(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
        logger.info(f"RPC call received: append_entries for RaftNode {self.node_id}")
        response = {'term': self.current_term, 'success': False}

        self.reset_election_timeout_if_needed(term)

        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {leader_id} with current term {self.current_term}")
            return response

        self.reset_election_timer()

        if term > self.current_term or (
                prev_log_index == len(self.log) - 1 and prev_log_term != self.log[prev_log_index]['term']):
            logger.info(
                f"RaftNode {leader_id} has a higher term, transitioning RaftNode {self.node_id} to FOLLOWER state")
            self.current_term = term
            self.transition_to_follower()
            return {'term': self.current_term, 'success': False}

        if prev_log_index >= 0 and self.log[prev_log_index]['term'] != prev_log_term:
            return response

        if not entries:  # this is a heartbeat
            logger.info(f"Heartbeat received from RaftNode {leader_id}")

        response['term'] = self.current_term
        response['success'] = True

        if entries:
            self.log = self.log[:prev_log_index + 1] + entries

        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
            self.apply_log_entries()

        return response

    def request_vote_rpc(self, term, candidate_id, last_log_index, last_log_term):
        logger.info(f"RPC call received: request_vote for RaftNode {self.node_id}")
        response = {'term': self.current_term, 'vote_granted': False}

        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {candidate_id} with current term {self.current_term}")
            return response

        self.reset_election_timeout_if_needed(term)

        if term > self.current_term or (self.voted_for is None or self.voted_for == candidate_id):
            if last_log_index >= len(self.log) - 1 and last_log_term >= self.log[last_log_index]['term']:
                response['vote_granted'] = True
                self.voted_for = candidate_id
                self.current_term = term
                if term > self.current_term:  # Only transition to follower if term is higher
                    logger.info(
                        f"Vote granted to RaftNode {candidate_id} by RaftNode {self.node_id}, \
                        transitioning to FOLLOWER state")
                    self.transition_to_follower()

        return response

    def reset_election_timeout_if_needed(self, term):
        if term >= self.current_term:
            self.reset_election_timer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a Raft node.")
    parser.add_argument("-id", "--node_id", type=str, help="Node ID")
    parser.add_argument("-p", "--ports", type=str, help="Dictionary of node IDs and corresponding ports")
    args = parser.parse_args()

    # if not args.node_id or not args.ports:
    #     parser.print_help()
    #     exit(1)
    #
    # ports = eval(args.ports)
    # nodes = list(ports.keys())

    ports = {'node1': 8000, 'node2': 8001, 'node3': 8002}
    nodes = ['node1', 'node2', 'node3']

    raft_node = RaftNode('node1', ports, nodes)
    time.sleep(0.5)
    raft_node.start()
