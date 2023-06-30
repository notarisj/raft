import unittest
from src.kv_store.trie_data_structure.data_tree import Trie


class TrieTest(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()

    def test_insert_and_search(self):
        data = {
            "key1": {
                "power": {
                    "office": {
                        "center": 22.063470471034165,
                        "stage": "oxws",
                        "product": {
                            "government": "stjw",
                            "pull": 90.44574907688828,
                            "language": "qnaz",
                            "computer": "xgzw",
                            "office": 0
                        },
                        "bank": "hdcq"
                    }
                },
                "dog": "mxpm",
                "animal": "aqxg"
            }
        }
        self.trie.insert(data)

        result = self.trie.search("key1")
        self.assertEqual(result, data['key1'])

    def test_delete(self):
        data = {
            "key1": {
                "power": {
                    "office": {
                        "center": 22.063470471034165,
                        "stage": "oxws",
                        "product": {
                            "government": "stjw",
                            "pull": 90.44574907688828,
                            "language": "qnaz",
                            "computer": "xgzw",
                            "office": 0
                        },
                        "bank": "hdcq"
                    }
                },
                "dog": "mxpm",
                "animal": "aqxg"
            }
        }
        self.trie.insert(data)

        # Delete key1 and its subtree
        result = self.trie.delete("key1")
        self.assertTrue(result)

        # Verify the deletion
        result = self.trie.search("key1")
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
