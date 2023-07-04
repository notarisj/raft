import concurrent.futures
import json
import random
import threading
import time
import math

from enum import Enum

from src.configuration_reader import IniConfig
from src.logger import MyLogger
from src.raft_node.log import Log
from src.rpc.rpc_client import RPCClient
from src.rpc.rpc_server import RPCServer

logger = MyLogger()
raft_config = IniConfig('src/configurations/config.ini')


class RaftState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3


class RaftServer:
    def __init__(self, server_id, raft_servers, database_uri, database_name, collection_name):
        self.server_id = server_id
        self.raft_servers = raft_servers
        self.hostname = raft_servers[server_id]['host']
        self.port = raft_servers[server_id]['port']
        self.voted_for = None
        self.state = RaftState.FOLLOWER
        self.min_val_for_timeout = float(raft_config.get_property('raft', 'min_val_for_timeout'))
        self.max_val_for_timeout = float(raft_config.get_property('raft', 'max_val_for_timeout'))
        self.election_timeout = random.uniform(self.min_val_for_timeout, self.max_val_for_timeout)
        self.start = time.time()
        self.log = Log(database_uri, database_name, collection_name, self.server_id)
        self.current_term = self.log.get_last_term()
        if self.log.is_empty():
            self.commit_index = 0
        else:
            self.commit_index = self.log.get_last_commit_index()
        self.election_in_progress = False

        # Create RPC server, register RPC functions and create RPC server thread
        self.rpc_server = RPCServer(host=self.hostname, port=self.port)
        self.rpc_server.register_function(self.append_entries_rpc, 'append_entries')
        self.rpc_server.register_function(self.request_vote_rpc, 'request_vote')

        # Create RPC clients for all other servers
        self.clients = {_server_id: RPCClient(host=server['host'], port=server['port'])
                        for _server_id, server in raft_servers.items() if _server_id != server_id}
        self.start = time.time()
        self.heartbeat_interval = float(raft_config.get_property('raft', 'heartbeat_interval'))
        self.leader_id = None
        # create thread pool for handling client requests in parallel
        self.heartbeat_executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.clients))
        self.append_entries_executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.clients))

        # create leader next index for each follower
        self.next_index = {}
        self.set_next_index()
        self.follower_append_index = {}
        self.is_running = False
        self.lock = threading.Lock()

    def __str__(self):
        return f"Server(id={self.server_id}, state={self.state.name}, " \
               f"term={self.current_term}, votedFor={self.voted_for})"

    def run(self):
        logger.info(f"Starting RaftNode with ID: {self.server_id}")
        threading.Thread(target=self.rpc_server.run).start()
        self.transition_to_follower()
        while self.is_running:
            if self.state == RaftState.FOLLOWER:
                if time.time() - self.start > self.election_timeout:
                    self.transition_to_candidate()
                    self.reset_election_timeout()
            elif self.state == RaftState.LEADER:
                threading.Thread(target=self.send_append_entries_to_servers_multicast).start()
                self.reset_election_timeout()
            time.sleep(self.heartbeat_interval)

    def add_node(self, server_id, host, port):
        self.raft_servers[server_id] = {'host': host, 'port': port}
        self.clients[server_id] = RPCClient(host=host, port=port)
        self.next_index[server_id] = 1
        self.follower_append_index[server_id] = 0

    def update_node(self, server_id, host, port):
        del self.raft_servers[server_id]
        del self.clients[server_id]
        self.raft_servers[server_id] = {'host': host, 'port': port}
        self.clients[server_id] = RPCClient(host=host, port=port)

    def delete_node(self, server_id):
        if server_id in self.raft_servers:
            del self.raft_servers[server_id]
        if server_id in self.clients:
            del self.clients[server_id]
        if server_id in self.next_index:
            del self.next_index[server_id]
        if server_id in self.follower_append_index:
            del self.follower_append_index[server_id]

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
        self.election_timeout = random.uniform(self.min_val_for_timeout, self.max_val_for_timeout)
        self.reset_election_timeout()
        self.start_election()

    def transition_to_leader(self, verbose=True):
        if verbose:
            logger.info(f"Transitioning to leader state. Server state: {self}")
        self.state = RaftState.LEADER
        self.leader_id = self.server_id
        self.start = time.time()
        self.election_timeout = random.uniform(1, 2)
        self.set_next_index()
        self.commit_index = self.log.get_last_commit_index()
        self.follower_append_index = {_server_id: self.commit_index for _server_id in self.clients.keys()}
        if self.log.is_empty():
            self.commit_index = 0
        else:
            self.commit_index = self.log.get_last_commit_index()
        self.follower_append_index = {_server_id: 0 if self.commit_index is None else self.commit_index
                                      for _server_id in self.clients.keys()}

    def set_next_index(self):
        self.next_index = {_server_id: self.log.get_last_index() + 1 for _server_id in self.raft_servers.keys() if
                           _server_id != self.server_id}

    def send_append_entries(self, _server_id):
        # write detailed documentation
        """
        Send append entries to a single server. The entries to be sent in
        each server are determined by the next_index
        :param _server_id: id of the server to send append entries to
        """
        entries = self.log.get_all_entries_from_index(self.next_index[_server_id])
        try:
            prev_log_index = self.next_index[_server_id] - 1
            prev_log_entry = self.log.get_entry(self.next_index[_server_id] - 1)
            if prev_log_entry is not None:
                prev_log_term = prev_log_entry.term
            else:
                prev_log_term = self.current_term

            response = self.clients[_server_id].call(
                'append_entries', self.current_term, self.server_id, prev_log_index,
                prev_log_term, entries, self.commit_index
            )
            if response is None:
                logger.info(f"Node {_server_id} is unreachable")
            elif response['term'] > self.current_term:
                logger.info(f"Node {_server_id} has higher term")
                self.transition_to_follower()
            elif response['success']:
                logger.info(f"Node {_server_id} accepted append entries")
                self.next_index[_server_id] = len(self.log.entries) + 1
                logger.info(f"Node {_server_id} next index: {self.next_index[_server_id]}")
                if len(entries) > 0:
                    self.follower_append_index[_server_id] = entries[-1].index
            elif response['index'] != -1:
                logger.info(f"Node {_server_id} rejected append entries with index {response['index']}"
                            f"setting next index to {response['index']} + 1")
                logger.info(f"Node {_server_id} has missing entries")
                self.next_index[_server_id] = response['index'] + 1
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def commit_leader_entries(self):
        with self.lock:
            new_commit_index = self.calculate_committed_index()
            self.log.commit_entries(self.commit_index, new_commit_index)
            self.commit_index = new_commit_index

    def send_append_entries_to_servers_multicast(self):
        """
        This method sends append entries to all servers in the cluster. It is called by the leader.
        """
        logger.info(f"Starting append entries multicast.")
        self.commit_leader_entries()
        futures = {self.heartbeat_executor.submit(self.send_append_entries, _server_id)
                   for _server_id in self.raft_servers.keys() if _server_id != self.server_id}
        for future in concurrent.futures.as_completed(futures):
            future.result()
        logger.info(f"Append entries multicast finished.")
        return

    def calculate_committed_index(self):
        """
        This method calculates the committed index for the leader.
        :return: the committed index
        """
        def get_top_servers(server_dict, x):
            sorted_servers = sorted(server_dict.items(), key=lambda item: item[1], reverse=True)
            return dict(sorted_servers[:x])

        number_of_nodes_needed = math.ceil((len(self.raft_servers)) / 2)
        top_servers = get_top_servers(self.follower_append_index, number_of_nodes_needed)

        # the following index has been at least replicated by majority of the nodes
        return min(top_servers.values())

    def append_entries_to_leader(self, _append_entries):
        """
        This method is called when the leader receives an append entries
        request from the client or another raft node.

        :param _append_entries:
        """
        if self.state != RaftState.LEADER:
            return False
        self.log.append_entry(self.current_term, json.dumps(_append_entries))
        return True

    def reset_election_timeout(self):
        self.start = time.time()

    def start_election(self):
        """
        This method is called when a node times out and starts an election.
        It sends a vote request to all other nodes in the cluster.
        """
        if self.election_in_progress:
            return
        self.election_in_progress = True
        logger.info(f"Starting election for RaftNode {self}")
        votes_received = 1
        unreachable_nodes = 0
        total_servers = len(self.raft_servers)

        # TODO: Send vote requests in parallel
        for _server_id in self.raft_servers.keys():
            if _server_id != self.server_id:
                last_log_index = self.log.get_last_index()
                if self.log.is_empty():
                    last_log_term = self.current_term
                else:
                    last_log_term = self.log.get_entry(last_log_index).term
                response = self.clients[_server_id].call(
                    'request_vote', self.server_id, self.current_term,
                    last_log_index, last_log_term
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
                        self.election_in_progress = False
                        self.transition_to_leader()
                        return
                else:
                    self.election_in_progress = False
                    self.transition_to_follower()
                    return

    def append_entries_rpc(self, term, leader_id, prev_log_index, prev_log_term, entries, leader_commit):
        """
        Invoked by leader to replicate log entries; also used as heartbeat.

        Args:
            term: leader's term
            leader_id: so follower can redirect clients
            prev_log_index: index of log entry immediately preceding new ones
            prev_log_term: term of prev_log_index entry
            entries: log entries to store (empty for heartbeat; may send more than one for efficiency)
            leader_commit: leader's commit_index
        """

        logger.info(f"Received append_entries from RaftNode {leader_id} to "
                    f"RaftNode {self.server_id} with entries {entries}")
        response = {'term': self.current_term, 'success': True, 'index': -1}

        if term < self.current_term:
            logger.info(f"Received outdated term, responding to RaftNode {leader_id} "
                        f"with current term {self.current_term}")
            response['success'] = False
            return response

        if term >= self.current_term:
            self.reset_election_timeout()
            self.leader_id = leader_id
            self.current_term = term

        """
        Receiver Implementation
        1. Reply false if term < currentTerm (§5.1)
        2. Reply false if log doesn't contain an entry at prevLogIndex whose term matches prevLogTerm (§5.3)
        3. If an existing entry conflicts with a new one (same index but different terms), delete the 
           existing entry and all that follow it (§5.3)
        4. Append any new entries not already in the log
        5. If leaderCommit > commitIndex, set commitIndex = min(leaderCommit, index of last new entry)
        """

        # 1. Reply false if term < currentTerm (§5.1)
        if term < self.current_term:
            response['success'] = False
            return response

        if prev_log_index > self.log.get_last_index():
            logger.info(
                f"RaftNode {self.server_id} rejected append_entries from RaftNode {leader_id} "
                f"due to missing log entries. Previous log index: {prev_log_index}, "
                f"Previous log term: {prev_log_term}, "
                f"Last log index: {self.log.get_last_index()}"
            )
            response['index'] = self.log.get_last_index()
            response['success'] = False
            return response

        # 2. Reply false if log doesn't contain an entry at prevLogIndex whose term matches prevLogTerm (§5.3)
        # 3. If an existing entry conflicts with a new one (same index but different terms), delete the
        #    existing entry and all that follow it (§5.3)
        if self.log.get_entry(prev_log_index) is not None:
            if prev_log_term != self.log.get_entry(prev_log_index).term:
                logger.info(
                    f"RaftNode {self.server_id} rejected append_entries from RaftNode {leader_id} "
                    f"due to conflicting entries. Previous log index: {prev_log_index}, "
                    f"Previous log term: {prev_log_term}, "
                    f"Log term at index {prev_log_index}: {self.log.get_entry(prev_log_index).term}"
                    f"Conflicting entries will be deleted."
                )
                self.log.delete_entries_after(prev_log_index)
                response['success'] = False
                # return response

        # 4. Append any new entries not already in the log
        if entries is not None:
            for entry in entries:
                self.log.append_entry(entry['term'], entry['command'])

        # 5. If leaderCommit > commitIndex, set commitIndex = min(leaderCommit, index of last new entry)
        if leader_commit > self.commit_index:
            self.log.commit_entries(self.commit_index, leader_commit)
            self.commit_index = min(leader_commit, self.log.get_last_index())
        return response

    def request_vote_rpc(self, candidate_id, term, last_log_index, last_log_term):
        """
        Invoked by candidates to gather votes.

        Args:
            candidate_id: candidate requesting vote
            term: candidate's term
            last_log_index: index of candidate's last log entry
            last_log_term: term of candidate's last log entry
        """
        logger.info(f"RPC call received: request_vote for RaftNode {self.server_id}")
        response = {'term': self.current_term, 'vote_granted': False}
        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {candidate_id} with current term {self.current_term}")
            return response

        if term > self.current_term:
            self.current_term = term
            self.voted_for = None
            self.reset_election_timeout()

        if (self.voted_for is None or self.voted_for == candidate_id) and self.log.is_up_to_date(last_log_index,
                                                                                                 last_log_term):
            self.voted_for = candidate_id
            response['vote_granted'] = True
            logger.info(f"Vote granted to RaftNode {candidate_id} by RaftNode {self.server_id}")
            return response
        else:
            logger.info(f"Vote denied to RaftNode {candidate_id} by RaftNode {self.server_id}")
            return response
