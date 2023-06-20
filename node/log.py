import os
import json


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

    def __init__(self, uncommitted_log_file_path=None, committed_log_file_path=None):
        self.entries = []
        self.UNCOMMITTED_LOG_FILE_PATH = uncommitted_log_file_path
        self.COMMITTED_LOG_FILE_PATH = committed_log_file_path

        if os.path.exists(self.COMMITTED_LOG_FILE_PATH):
            with open(self.COMMITTED_LOG_FILE_PATH, 'r') as f:
                self.entries = [LogEntry.from_dict(json.loads(line)) for line in f]

        if os.path.exists(self.UNCOMMITTED_LOG_FILE_PATH):
            with open(self.UNCOMMITTED_LOG_FILE_PATH, 'r') as f:
                uncommitted_entries = [LogEntry.from_dict(json.loads(line)) for line in f]
                self.entries += uncommitted_entries

    def append_to_file(self, entry, file_path):
        with open(file_path, 'a') as f:
            f.write(json.dumps(entry.to_dict()))
            f.write('\n')

    def append_entry(self, term, command):
        index = len(self.entries) + 1
        entry = LogEntry(index, term, command)
        self.entries.append(entry)
        self.append_to_file(entry, self.UNCOMMITTED_LOG_FILE_PATH)
        return index

    def get_entry(self, index):
        return self.entries[index - 1]

    def get_last_index(self):
        return len(self.entries)

    def commit_entry(self, index):
        self.entries[index - 1].is_committed = True
        self.append_to_file(self.entries[index - 1], self.COMMITTED_LOG_FILE_PATH)
        self.delete_line_from_file(index, self.UNCOMMITTED_LOG_FILE_PATH)

    def get_last_term(self):
        return self.entries[-1].term

    def delete_line_from_file(self, index, file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()

        with open(file_path, "w") as f:
            for line in lines:
                entry = LogEntry.from_dict(json.loads(line))
                if entry.index != index:
                    f.write(line)

    def delete_entries_after(self, prev_log_index):
        self.entries = self.entries[:prev_log_index]
        self.rewrite_file_from_entries(prev_log_index)


    def rewrite_file_from_entries(self, prev_log_index):
        with open(self.UNCOMMITTED_LOG_FILE_PATH, "w") as f:
            for entry in self.entries[prev_log_index:]:
                f.write(json.dumps(entry.to_dict()))
                f.write('\n')

    def contains_entry_at_index(self, index):
        return index <= len(self.entries)

    def commit_all_entries_after(self, prev_log_index):
        for entry in self.entries[prev_log_index:]:
            entry.is_committed = True
            self.append_to_file(entry, self.COMMITTED_LOG_FILE_PATH)
        self.entries = self.entries[:prev_log_index]
        self.rewrite_file_from_entries(prev_log_index)

    def get_all_commands_from_index(self, index):
        commands = []
        for entry in self.entries[index - 1:]:
            commands.append(entry.command)
        return commands

    def get_all_commands_from_term(self, term, index_sort=False):
        commands = []
        for entry in self.entries:
            if entry.term == term:
                commands.append(entry.command)
        if index_sort:
            commands.sort(key=lambda x: x.index)
        return commands
