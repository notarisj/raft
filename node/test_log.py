import unittest
import tempfile
import os
import json

from log import Log, LogEntry


class LogTests(unittest.TestCase):

    def setUp(self):
        self.uncommitted_log_file_path = tempfile.mkstemp()[1]
        self.committed_log_file_path = tempfile.mkstemp()[1]

        self.log = Log(self.uncommitted_log_file_path, self.committed_log_file_path)

    def tearDown(self):
        os.remove(self.uncommitted_log_file_path)
        os.remove(self.committed_log_file_path)

    def test_append_entry(self):
        term = 1
        command = "Test command"
        index = self.log.append_entry(term, command)

        # Check that the entry is added to the log
        self.assertEqual(len(self.log.entries), 1)

        # Check the properties of the added entry
        entry = self.log.get_entry(index)
        self.assertEqual(entry.index, index)
        self.assertEqual(entry.term, term)
        self.assertEqual(entry.command, command)
        self.assertFalse(entry.is_committed)

    def test_get_entry(self):
        term = 1
        command = "Test command"
        index = self.log.append_entry(term, command)

        # Check that the correct entry is retrieved
        entry = self.log.get_entry(index)
        self.assertEqual(entry.index, index)
        self.assertEqual(entry.term, term)
        self.assertEqual(entry.command, command)

    def test_get_last_index(self):
        # Add multiple entries to the log
        for i in range(5):
            self.log.append_entry(i, f"Command {i}")

        # Check the last index
        last_index = self.log.get_last_index()
        self.assertEqual(last_index, 5)

    def test_commit_entry(self):
        term = 1
        command = "Test command"
        index = self.log.append_entry(term, command)

        # Commit the entry
        self.log.commit_entry(index)

        # Check that the entry is marked as committed
        entry = self.log.get_entry(index)
        self.assertTrue(entry.is_committed)

        # Check that the entry is moved to the committed log file
        with open(self.committed_log_file_path, 'r') as f:
            committed_entries = [LogEntry.from_dict(json.loads(line)) for line in f]
        self.assertEqual(len(committed_entries), 1)
        self.assertEqual(committed_entries[0].index, index)

    # Write more test cases for the remaining methods in the Log class


if __name__ == '__main__':
    unittest.main()
