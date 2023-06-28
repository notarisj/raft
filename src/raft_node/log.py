import json
import socket
import ssl
import threading
import time

from pymongo import MongoClient

from src.configurations import IniConfig, JsonConfig
from src.kv_store.my_io import send_message
from src.logger import MyLogger

logger = MyLogger()
raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')
servers = JsonConfig('/Users/notaris/git/raft/src/raft_node/deploy/servers.json').get_all_properties()


class LogEntry:
    def __init__(self, index, term, command, is_committed=False):
        self.index = index
        self.term = term
        self.command = command
        self.is_committed = is_committed

    def __str__(self):
        return f"LogEntry(index={self.index}, term={self.term}, " \
               f"command={self.command}, is_committed={self.is_committed})"

    def to_dict(self):
        return {
            'index': self.index,
            'term': self.term,
            'command': self.command,
            'is_committed': self.is_committed,
        }

    @staticmethod
    def from_dict(d):
        return LogEntry(d['index'], d['term'], d['command'], d['is_committed'])


class Log:
    def __init__(self, database_uri, database_name, collection_name):
        self.client_sockets = {}
        # self.server_port = servers[self.server_id]['kv_port']
        # self.server_ip = servers[self.server_id]['host']
        threading.Thread(target=self.connect).start()
        self.client = MongoClient(database_uri)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

        self.entries = []
        self.load_entries()

    def load_entries(self):
        cursor = self.collection.find({})
        self.entries = [LogEntry.from_dict(entry) for entry in cursor]

    def save_entry(self, entry):
        self.collection.insert_one(entry.to_dict())

    def append_entry(self, term, command):
        index = len(self.entries) + 1
        entry = LogEntry(index, term, command)
        self.entries.append(entry)
        self.save_entry(entry)
        return index

    def get_entry(self, index):
        if len(self.entries) < index or index == 0:
            return None
        return self.entries[index - 1]

    def get_last_index(self):
        return len(self.entries)

    def commit_entry(self, index):
        entry = self.entries[index - 1]
        entry.is_committed = True
        self.collection.update_one({'index': index}, {'$set': entry.to_dict()})

    def delete_entry_from_collection(self, entry):
        self.collection.delete_one({'index': entry.index})

    def delete_entries_after(self, prev_log_index):
        self.entries = self.entries[:prev_log_index]
        result = self.collection.delete_many({'index': {'$gt': prev_log_index}})
        print(f"Deleted {result.deleted_count} entries from collection.")

    def get_last_term(self):
        if len(self.entries) == 0:
            return 0
        return self.entries[-1].term

    def commit_entries(self, server_id, commit_index, new_commit_index):
        print(f"Committing entries from {commit_index} to {new_commit_index}")
        for entry in self.entries[commit_index:new_commit_index]:
            print('inside commit entries')
            entry.is_committed = True
            self.collection.update_one({'index': entry.index}, {'$set': entry.to_dict()})
            # Send entry to state machine
            try:
                print('apply to state machine')
                self.append_to_state_machine(server_id, entry.command)
            except ConnectionError as e:
                logger.error(f"ConnectionError: {e}")

    def get_last_commit_index(self):
        for i in range(len(self.entries) - 1, -1, -1):
            if self.entries[i].is_committed:
                return i + 1

    def get_all_entries_from_index(self, index):
        return self.entries[index - 1:]

    def is_empty(self):
        return len(self.entries) == 0

    def update_entry(self, index):
        entry = self.entries[index - 1]
        self.collection.update_one({'index': index}, {'$set': entry.to_dict()})

    def is_up_to_date(self, last_log_index, last_log_term):
        print(f"last_log_index: {last_log_index}, last_log_term: {last_log_term}")
        print(f"self.get_last_index(): {self.get_last_index()}")
        print(f"self.get_last_term(): {self.get_last_term()}")
        if last_log_term > self.get_last_term():
            return True
        elif last_log_term == self.get_last_term() and last_log_index >= self.get_last_index():
            return True
        else:
            return False

    def append_to_state_machine(self, server_id, _append_entry):
        print('server_id', server_id)
        print('_append_entry, _append_entry')
        send_message(_append_entry, self.client_sockets[str(server_id)])

    def connect(self):

        # for server_id, info in servers.items():

        while len(self.client_sockets) < len(servers):
            print('len(self.client_sockets)', len(self.client_sockets))
            print('len(servers)', len(servers))
            print(len(self.client_sockets) < len(servers))
            for server_id, info in servers.items():
                if server_id in self.client_sockets:
                    continue
                try:
                    # Create a TCP/IP socket
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    # Create an SSL context
                    context = ssl.create_default_context(cafile=raft_config.get_property('SSL', 'ssl_cert_file'))
                    context.check_hostname = True
                    context.verify_mode = ssl.CERT_REQUIRED

                    self.client_sockets[server_id] = context.wrap_socket(client_socket, server_hostname=info['host'])
                    # Wrap the client socket with SSL
                    self.client_sockets[server_id].connect((info['host'], info['kv_port']))
                    logger.info("Connected to {}:{}".format(info['host'], info['kv_port']))
                except ConnectionRefusedError:
                    logger.error("Failed to connect. Please ensure the server is running.")
                    del self.client_sockets[server_id]
            time.sleep(0.5)
