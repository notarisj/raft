from collections import ChainMap
from typing import Any


class TrieNode:
    def __init__(self, key: str, value=None):
        """
        Initialize a TrieNode object.

        Args:
            key (str): The key associated with the TrieNode.
            value (Any, optional): The value associated with the TrieNode. Defaults to None.
        """
        self.key = key
        self.value = value
        self.children = {}


class Trie:
    def __init__(self):
        """
        Initialize a Trie object.
        """
        self.root = TrieNode("")

    def build_trie(self, key: str, value: Any = None):
        """
        Build a trie based on the provided key and value.

        Args:
            key (str): The key for the trie node.
            value (Any, optional): The value for the trie node. Defaults to None.
        """
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode(char)
            node = node.children[char]
        node.value = value

    def insert(self, _json_obj: dict, prefix: str = "") -> None:
        """
        Insert a JSON object into the trie.

        Args:
            _json_obj (dict): The JSON object to insert.
            prefix (str, optional): The prefix for the JSON object keys. Defaults to "".
        """
        if isinstance(_json_obj, dict):
            if not _json_obj:  # Empty dictionary case
                self.build_trie(prefix, {})
            else:
                for key, value in _json_obj.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    self.insert(value, new_prefix)
        else:
            self.build_trie(prefix, _json_obj)

    def search(self, key: str) -> dict | None | str:
        """
        Search for a key in the trie and return the subtree of the key as JSON object.

        Args:
            key (str): The key to search for.

        Returns:
            dict | None: The JSON object associated with the key, or None if the key is not found.
        """
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        if "." in node.children:
            return self.traverse_subtree(node.children["."], key, {})
        elif node.value is not None:
            return node.value
        else:
            return "NOT FOUND"

    def traverse_subtree(self, node: 'TrieNode', key: str, _json_obj: dict) -> dict | None:
        """
        Traverse the subtree starting from the given node (last node of the string for search method)
        and construct the JSON object.

        Args:
            node (TrieNode): The starting node of the subtree.
            key (str): The key associated with the subtree.
            _json_obj (dict): The JSON object being constructed.

        Returns:
            dict | None: The constructed JSON object, or None if the subtree is empty.
        """
        if node.value is not None:
            return {key: node.value}
        else:
            concat_json = {}
            if node.key == ".":  # if node has children
                for child_key, child_node in node.children.items():
                    temp_json = self.traverse_subtree(child_node, child_key, _json_obj)
                    concat_json = dict(ChainMap(temp_json, concat_json))
                if "." in key:
                    key = key.replace(".", "")
                    _json_obj = dict(ChainMap({key: concat_json}, _json_obj))
                else:
                    _json_obj = dict(ChainMap(concat_json, _json_obj))
            else:
                for child_key, child_node in node.children.items():
                    temp_json = self.traverse_subtree(child_node, key + child_key, _json_obj)
                    concat_json = dict(ChainMap(temp_json, concat_json))
                if len(concat_json.items()) > 1 and len(node.children.items()) == 0:
                    _json_obj = dict(ChainMap({key: concat_json}, _json_obj))
                else:
                    _json_obj = dict(ChainMap(concat_json, _json_obj))
            return _json_obj

    def delete(self, key: str, node: 'TrieNode' = None) -> bool:
        """
        Delete a key from the trie. Find the last character of the key and delete all the subtree.
        If parent node of the key has no other child except key, delete the key node too (recursively).

        Args:
            key (str): The key to delete.
            node (TrieNode): The starting node of the subtree. Defaults to None.

        Returns:
            bool: True if the parent node should delete the node.children[char] where char is
            first letter of key at every level.
        """
        if node is None:
            node = self.root

        if len(key) == 0 and node.children["."]:
            del node.children["."]
            return len(node.children) == 0

        char = key[0]

        if char not in node.children:
            return False

        delete_node = self.delete(key[1:], node.children[char])

        if delete_node:
            del node.children[char]

        return len(node.children) == 0
