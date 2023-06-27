from collections import ChainMap


class TrieNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.children = {}


class Trie:
    def __init__(self):
        self.root = TrieNode("")

    def build_trie(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode(char)
            node = node.children[char]
        node.value = value

    def insert(self, _json_obj, prefix="") -> None:
        if isinstance(_json_obj, dict):
            if not _json_obj:  # Empty dictionary case
                self.build_trie(prefix, {})
            else:
                for key, value in _json_obj.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    self.insert(value, new_prefix)
        else:
            self.build_trie(prefix, _json_obj)

    def search(self, key) -> dict | None:
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        if "." in node.children:
            return self.traverse_subtree(node.children["."], key, {})
        else:
            return self.traverse_subtree(node, key, {})

    def traverse_subtree(self, node, key, _json_obj) -> dict | None:
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

    def delete(self, key) -> str | None:
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        if "." in node.children:
            del node.children["."]
            return "OK"
        else:
            return None
