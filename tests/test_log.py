import unittest

from pymongo import MongoClient
from src.raft_node import Log


class TestLog(unittest.TestCase):
    def setUp(self):
        self.database_uri = 'mongodb://localhost:27017/'
        self.database_name = 'test_database'
        self.collection_name = 'test_collection'
        self.log = Log(self.database_uri, self.database_name, self.collection_name, 1)

    def tearDown(self):
        client = MongoClient(self.database_uri)
        client.drop_database(self.database_name)

    def test_append_and_get_entry(self):
        self.log.append_entry('term1', 'command1')
        entry = self.log.get_entry(1)
        self.assertEqual(len(self.log.entries), 1)
        self.assertEqual(entry.term, 'term1')
        self.assertEqual(entry.command, 'command1')

    def test_commit_entry(self):
        self.log.append_entry('term1', 'command1')
        self.log.commit_entry(1)
        self.assertTrue(self.log.entries[0].is_committed)

    def test_delete_entries_after(self):
        self.log.append_entry('term1', 'command1')
        self.log.append_entry('term2', 'command2')
        self.log.delete_entries_after(1)
        self.assertEqual(len(self.log.entries), 1)

    def test_get_last_index(self):
        self.log.append_entry('term1', 'command1')
        self.assertEqual(self.log.get_last_index(), 1)

    def test_get_last_term(self):
        self.log.append_entry('term1', 'command1')
        self.assertEqual(self.log.get_last_term(), 'term1')

    def test_commit_entries(self):
        self.log.append_entry('term1', 'command1')
        self.log.append_entry('term2', 'command2')
        self.log.commit_entries(0, 2)
        self.assertTrue(all(entry.is_committed for entry in self.log.entries))

    def test_get_last_commit_index(self):
        self.log.append_entry('term1', 'command1')
        self.log.commit_entry(1)
        self.assertEqual(self.log.get_last_commit_index(), 1)

    def test_get_all_entries_from_index(self):
        self.log.append_entry('term1', 'command1')
        self.log.append_entry('term2', 'command2')
        entries = self.log.get_all_entries_from_index(1)
        self.assertEqual(len(entries), 2)


if __name__ == "__main__":
    unittest.main()
