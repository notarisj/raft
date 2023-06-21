from pymongo import MongoClient


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
        # self.save_entry(entry)
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
        self.save_entry(entry)

    def delete_entry_from_collection(self, entry):
        self.collection.delete_one({'index': entry.index})

    def delete_entries_after(self, prev_log_index):
        self.entries = self.entries[:prev_log_index]
        self.collection.delete_many({'index': {'$gt': prev_log_index}})

    def get_last_term(self):
        return self.entries[-1].term

    def commit_entries(self, commit_index, leader_commit):
        print(f"Committing entries from {commit_index} to {leader_commit}")
        for entry in self.entries[commit_index:leader_commit]:
            entry.is_committed = True
            self.save_entry(entry)

    def get_last_commit_index(self):
        return self.collection.count_documents({'is_committed': True})

    def get_all_entries_from_index(self, index):
        return self.entries[index - 1:]

    def is_empty(self):
        return len(self.entries) == 0
