import concurrent.futures
import random
import threading
import time

from enum import Enum

from logger import MyLogger
from node.log import Log
from rpc.rpc_client import RPCClient
from rpc.rpc_server import RPCServer

logger = MyLogger()


class RaftState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


min_val_for_timeout = 1
max_val_for_timeout = 2


class RaftServer:
    def __init__(self, server_id, raft_servers):
        self.commit_index = -1
        self.server_id = server_id
        self.raft_servers = raft_servers
        self.hostname = raft_servers[server_id]['host']
        self.port = raft_servers[server_id]['port']
        self.current_term = 0
        self.voted_for = None
        self.state = RaftState.FOLLOWER
        self.election_timeout = random.uniform(min_val_for_timeout, max_val_for_timeout)
        self.start = time.time()
        self.log = Log()
        self.log.append_entry(self.current_term, '')
        self.election_in_progress = False

        # Create RPC server, register RPC functions and create RPC server thread
        self.server = RPCServer(host=self.hostname, port=self.port)
        self.server.register_function(self.append_entries_rpc, 'append_entries')
        self.server.register_function(self.request_vote_rpc, 'request_vote')
        self.server_thread = threading.Thread(target=self.server.run)
        # Create RPC clients for all other servers
        self.clients = {_server_id: RPCClient(host=server['host'], port=server['port'])
                        for _server_id, server in raft_servers.items() if _server_id != server_id}
        self.start = time.time()
        self.heartbeat_interval = 0.5
        self.leader = None
        # create thread pool for handling client requests in parallel
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.clients))
        self.send_heartbeat_max_retry = 3

    def __str__(self):
        return f"Server(id={self.server_id}, state={self.state.name}, term={self.current_term}, votedFor={self.voted_for})"

    def run(self):
        logger.info(f"Starting RaftNode with ID: {self.server_id}")
        self.server_thread.start()
        self.transition_to_follower()
        delay = random.uniform(0, 5)  # Randomize the initial delay before the first election
        time.sleep(delay)
        while True:
            if self.state == RaftState.FOLLOWER:
                if time.time() - self.start > self.election_timeout:
                    self.transition_to_candidate()
                    self.reset_election_timeout()
            elif self.state == RaftState.LEADER:
                self.send_append_entries_to_server_multicast()
                self.reset_election_timeout()
            time.sleep(self.heartbeat_interval)

    def transition_to_follower(self, verbose=True):
        if verbose:
            logger.info(f"Transitioning to follower state. Server state: {self}")
        self.state = RaftState.FOLLOWER
        self.voted_for = None
        self.start = time.time()

    def transition_to_candidate(self, verbose=True):
        self.state = RaftState.CANDIDATE
        if verbose:
            logger.info(f"Transitioning to candidate state. Server state: {self}")
        self.current_term += 1
        self.voted_for = self.server_id
        self.start = time.time()
        self.election_timeout = random.uniform(1, 2)
        self.start_election()

    def transition_to_leader(self, verbose=True):
        if verbose:
            logger.info(f"Transitioning to leader state. Server state: {self}")
        self.state = RaftState.LEADER
        self.start = time.time()
        self.election_timeout = random.uniform(1, 2)

    def send_append_entries_to_server(self, _server_id, max_retries, log_entries):
        retries = 0
        while _server_id != self.server_id and retries < max_retries:
            try:
                # def append_entries_rpc(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
                response = self.clients[_server_id].call(
                    'append_entries', self.current_term, self.server_id,
                    self.log.get_last_index(), self.log.get_entry(self.log.get_last_index()).term,
                    log_entries, self.commit_index
                )
                if response is None:
                    logger.info(f"Node {_server_id} is unreachable")
                    # time.sleep(1)  # Wait a while before trying again
                    retries += 1
                    continue
                if not response['success']:
                    logger.info(f"Node {_server_id} rejected heartbeat")
                    # time.sleep(1)  # Wait a while before trying again
                    retries += 1
                    continue
                break  # If the response was successful, break the loop
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                # time.sleep(1)  # Wait a while before trying again
                retries += 1

    def send_append_entries_to_server_multicast(self, log_entries=None):
        if log_entries is None:
            log_entries = []
        futures = {self.executor.submit(self.send_append_entries_to_server, _server_id, self.send_heartbeat_max_retry, log_entries)
                   for _server_id in self.raft_servers.keys()
                   }
        for future in concurrent.futures.as_completed(futures):
            future.result()

    def reset_election_timeout(self):
        self.start = time.time()
        self.election_timeout = random.uniform(min_val_for_timeout, max_val_for_timeout)

    def start_election(self):
        if self.election_in_progress:
            return
        self.election_in_progress = True
        logger.info(f"Starting election for RaftNode {self}")
        votes_received = 1
        unreachable_nodes = 0
        total_servers = len(self.raft_servers)

        for _server_id in self.raft_servers.keys():
            if _server_id != self.server_id:
                # response = self.clients[_server_id].request_vote(
                #     self.server_id, self.current_term,
                #     self.log.get_entry(0).index, self.log.get_entry(0).command
                # )
                response = self.clients[_server_id].call(
                    'request_vote', self.server_id, self.current_term
                )
                if response is None:
                    logger.info(f"Node {_server_id} is unreachable")
                    unreachable_nodes += 1
                    if unreachable_nodes > total_servers / 3:
                        self.election_in_progress = False
                        self.transition_to_follower()
                        return
                    continue
                elif response['term'] > self.current_term:
                    logger.info(f"RaftNode {self.server_id} discovered higher term. Transitioning to follower")
                    self.election_in_progress = False
                    self.transition_to_follower()
                    return
                elif response['vote_granted']:
                    logger.info(f"Vote granted to RaftNode {self.server_id} by RaftNode {_server_id}")
                    votes_received += 1
                    if votes_received > total_servers / 2:
                        # if votes_received >  total_servers - 1:
                        self.election_in_progress = False
                        self.transition_to_leader()
                        return
                else:
                    self.election_in_progress = False
                    self.transition_to_follower()
                    return

    def append_entries_rpc(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
        logger.info(f"Received append_entries from RaftNode {leader_id} to RaftNode {self.server_id} with entries {entries}")
        response = {'term': self.current_term, 'success': False}

        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {leader_id} with current term {self.current_term}")
            return response

        if term >= self.current_term:
            self.reset_election_timeout()

        if term > self.current_term or (self.voted_for is None or self.voted_for == leader_id):
            self.transition_to_follower(verbose=False)

        if term > self.current_term:
            self.current_term = term

        if prev_log_index > self.log.get_last_index():
            logger.info(f"RaftNode {self.server_id} rejected append_entries from RaftNode {leader_id}")
            return response

        if prev_log_index > 0 and prev_log_term != self.log.get_entry(prev_log_index).term:
            logger.info(f"RaftNode {self.server_id} rejected append_entries from RaftNode {leader_id}")
            return response

        if prev_log_index > 0 and prev_log_term == self.log.get_entry(prev_log_index).term:
            self.log.delete_entries_after(prev_log_index)

        for entry in entries:
            self.log.append_entry(entry['term'], entry['command'])

        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, self.log.get_last_index())

        response['success'] = True
        return response

    def request_vote_rpc(self, candidate_id, term):
        logger.info(f"RPC call received: request_vote for RaftNode {self.server_id}")
        response = {'term': self.current_term, 'vote_granted': False}

        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {candidate_id} with current term {self.current_term}")
            return response

        if term >= self.current_term:
            self.reset_election_timeout()

        if term > self.current_term or (self.voted_for is None or self.voted_for == candidate_id) \
                and self.state == RaftState.FOLLOWER:
            response['vote_granted'] = True
            logger.info(
                f"Vote granted to RaftNode {candidate_id} by RaftNode {self.server_id}, transitioning to FOLLOWER state"
            )
            self.transition_to_follower()

        return response
