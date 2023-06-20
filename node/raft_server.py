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
    def __init__(self, server_id, raft_servers, uncommitted_log_file_path=None, committed_log_file_path=None):
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
        self.log = Log(uncommitted_log_file_path, committed_log_file_path)
        if len(self.log.entries) == 0:
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
        self.leader_id = None
        # create thread pool for handling client requests in parallel
        self.heartbeat_executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.clients))
        self.append_entries_executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.clients))
        threading.Thread(target=self.run).start()

        # create leader next index for each follower
        self.next_index = {_server_id: self.log.get_last_index() + 1 for _server_id in raft_servers.keys() if
                           _server_id != self.server_id}
        self.active_append_threads = {_server_id: False for _server_id in self.clients.keys()}

    def __str__(self):
        return f"Server(id={self.server_id}, state={self.state.name}, " \
               f"term={self.current_term}, votedFor={self.voted_for})"

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
                threading.Thread(target=self.send_append_entries_to_server_multicast).start()
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
        self.leader_id = self.server_id
        self.start = time.time()
        self.election_timeout = random.uniform(1, 2)

    def send_append_entries(self, _server_id):
        commands = self.log.get_all_commands_from_index(self.next_index[_server_id])
        try:
            response = self.clients[_server_id].call(
                'append_entries', self.current_term, self.server_id, self.next_index[_server_id] - 1,
                self.log.get_entry(self.next_index[_server_id] - 1).term, commands, self.commit_index
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
            elif response['index'] != -1:
                logger.info(f"Node {_server_id} rejected append entries with index {response['index']}"
                            f"setting next index to {response['index']} + 1")
                logger.info(f"Node {_server_id} has missing entries")
                self.next_index[_server_id] = response['index'] + 1
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def send_append_entries_to_server_multicast(self, commands=None):
        # Stop all the threads from the executor before starting new ones. Some threads may be
        # still running if they append entries to a follower that is unreachable.

        # logger.info(f"signaling threads to stop")
        # # signal all threads to stop
        # for _server_id in self.active_append_threads.keys():
        #     self.active_append_threads[_server_id] = False
        #
        # logger.info(f"waiting for threads to stop")
        # # wait for all threads to stop
        # for future in concurrent.futures.as_completed(self.futures):
        #     future.result()
        #
        # logger.info(f"threads stopped")
        logger.info(f"Starting append entries multicast.")
        futures = {self.heartbeat_executor.submit(
            self.send_append_entries,
            _server_id)
            for _server_id in self.raft_servers.keys() if _server_id != self.server_id}
        for future in concurrent.futures.as_completed(futures):
            future.result()
        logger.info(f"Append entries multicast finished.")
        return

    def append_entries_to_leader(self, commands):
        if self.state != RaftState.LEADER:
            return False
        for command in commands:
            self.log.append_entry(self.current_term, command)
        return True

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
                response = self.clients[_server_id].call(
                    'request_vote', self.server_id, self.current_term,
                    self.log.get_last_index(),
                    self.log.get_entry(self.log.get_last_index()).term
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

    def append_entries_rpc(self, term, leader_id, prev_log_index, prev_log_term, commands, leader_commit):

        # # print all the input arguments
        # print("term: ", term)
        # print("leader_id: ", leader_id)
        print("prev_log_index: ", prev_log_index)
        print("prev_log_term: ", prev_log_term)
        # print("commands: ", commands)
        # print("leader_commit: ", leader_commit)

        logger.info(
            f"Received append_entries from RaftNode {leader_id} to RaftNode {self.server_id} with entries {commands}")
        response = {'term': self.current_term, 'success': False, 'index': -1}

        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {leader_id} with current term {self.current_term}")
            return response

        if term >= self.current_term:
            self.reset_election_timeout()
            self.leader_id = leader_id
            self.current_term = term

        """
        Receiver Implementation
        1. Reply false if term < currentTerm (§5.1)
        2. Reply false if log doesn’t contain an entry at prevLogIndex whose term matches prevLogTerm (§5.3)
        3. If an existing entry conflicts with a new one (same index but different terms), delete the 
           existing entry and all that follow it (§5.3)
        4. Append any new entries not already in the log
        5. If leaderCommit > commitIndex, set commitIndex = min(leaderCommit, index of last new entry)
        """

        # 1. Reply false if term < currentTerm (§5.1)
        # print("self.current_term: ", self.current_term)
        if term < self.current_term:
            return response

        print("self.log.get_last_index(): ", self.log.get_last_index())
        if prev_log_index > self.log.get_last_index() + 1:
            logger.info(
                f"RaftNode {self.server_id} rejected append_entries from RaftNode {leader_id} "
                f"due to missing log entries. Previous log index: {prev_log_index}, "
                f"Previous log term: {prev_log_term}, "
                f"Last log index: {self.log.get_last_index()}"
            )
            response['index'] = self.log.get_last_index()
            return response

        # 2. Reply false if log doesn’t contain an entry at prevLogIndex whose term matches prevLogTerm (§5.3)
        # 3. If an existing entry conflicts with a new one (same index but different terms), delete the
        #    existing entry and all that follow it (§5.3)
        print("self.log.get_entry(prev_log_index): ", self.log.get_entry(prev_log_index))
        if prev_log_term != self.log.get_entry(prev_log_index).term:
            logger.info(
                f"RaftNode {self.server_id} rejected append_entries from RaftNode {leader_id} "
                f"due to conflicting entries. Previous log index: {prev_log_index}, "
                f"Previous log term: {prev_log_term}, "
                f"Log term at index {prev_log_index}: {self.log.get_entry(prev_log_index).term}"
                f"Conflicting entries will be deleted."
            )
            # self.log.delete_entries_after(prev_log_index)
            return response

        # 4. Append any new entries not already in the log
        if commands is not None:
            for command in commands:
                self.log.append_entry(term, command)

        # 5. If leaderCommit > commitIndex, set commitIndex = min(leaderCommit, index of last new entry)
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, self.log.get_last_index())
            self.log.commit_all_entries_after(self.commit_index)

        response['success'] = True
        return response

    def request_vote_rpc(self, candidate_id, term, last_log_index, last_log_term):
        logger.info(f"RPC call received: request_vote for RaftNode {self.server_id}")
        response = {'term': self.current_term, 'vote_granted': False}

        if term < self.current_term:
            logger.info(
                f"Received outdated term, responding to RaftNode {candidate_id} with current term {self.current_term}")
            return response

        if term >= self.current_term:
            self.reset_election_timeout()

        if term > self.current_term or ((self.voted_for is None or self.voted_for == candidate_id)
                                        and (self.state == RaftState.FOLLOWER
                                             and last_log_index >= self.log.get_last_index()
                                             and last_log_term >= self.log.get_last_term())):
            response['vote_granted'] = True
            logger.info(
                f"Vote granted to RaftNode {candidate_id} by RaftNode {self.server_id}, transitioning to FOLLOWER state"
            )
            self.transition_to_follower()
        return response
