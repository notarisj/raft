class LogEntry:
    def __init__(self, index, term, command, is_committed=False):
        self.index = index
        self.term = term
        self.command = command
        self.is_committed = is_committed

    def __str__(self):
        return f"LogEntry(index={self.index}, term={self.term}, command={self.command}, is_committed={self.is_committed})"


class Log:
    def __init__(self):
        self.entries = []

    def append_entry(self, term, command):
        index = len(self.entries) + 1
        entry = LogEntry(index, term, command)
        self.entries.append(entry)

    def get_entry(self, index):
        return self.entries[index - 1]

    def commit_entry(self, index):
        self.entries[index - 1].is_committed = True

    def get_last_index(self):
        return len(self.entries)

    def delete_entries_after(self, prev_log_index):
        self.entries = self.entries[:prev_log_index]
