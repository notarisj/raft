import json
from collections import ChainMap


class TrieNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.children = {}


class Trie:
    def __init__(self):
        self.root = TrieNode("")

    def insert(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode(char)
            node = node.children[char]
        node.value = value

    def insert_from_json(self, _json_obj, prefix=""):
        if isinstance(_json_obj, dict):
            if not _json_obj:  # Empty dictionary case
                self.insert(prefix, {})
            else:
                for key, value in _json_obj.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    self.insert_from_json(value, new_prefix)
        else:
            self.insert(prefix, _json_obj)

    def search(self, key):
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        if "." in node.children:
            return self.subtree_to_json(node.children["."], key, {})
        else:
            return self.subtree_to_json(node, key, {})

    def subtree_to_json(self, node, key, _json_obj):
        if node.value is not None:
            return {key: node.value}
        else:
            if node.key == ".":  # if node has children
                concat_json = {}
                for child_key, child_node in node.children.items():
                    temp_json = self.subtree_to_json(child_node, child_key, _json_obj)
                    concat_json = dict(ChainMap(temp_json, concat_json))
                if "." in key:
                    key = key.replace(".", "")
                    _json_obj = dict(ChainMap({key: concat_json}, _json_obj))
                else:
                    _json_obj = dict(ChainMap(concat_json, _json_obj))
            else:
                concat_json = {}
                for child_key, child_node in node.children.items():
                    temp_json = self.subtree_to_json(child_node, key + child_key, _json_obj)
                    concat_json = dict(ChainMap(temp_json, concat_json))
                if len(concat_json.items()) > 1 and len(node.children.items()) == 0:
                    _json_obj = dict(ChainMap({key: concat_json}, _json_obj))
                else:
                    _json_obj = dict(ChainMap(concat_json, _json_obj))
            return _json_obj


trie = Trie()


json_obj = {
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
        "dog": {},
        "animal": "aqxg"
    }
}
trie.insert_from_json(json_obj)

search_key = "key1"
result = trie.search(search_key)
print(json.dumps(result, indent=4))
print()


json_obj_2 = {
    "key11": {
        "city": "ggsv",
        "hair": {},
        "factor": {
            "power": 55.257814040614164
        },
        "computer": {
                    "rule": "sopf",
                    "level": 23,
                    "model": 92
        }
    }
}
trie.insert_from_json(json_obj_2)
search_key = "key11"
result = trie.search(search_key)
print(json.dumps(result, indent=4))
print()

json_obj_3 = {
   "key43":{
      "father":{
         "organization":"ilet",
         "charge":46.577936022801005,
         "model":89,
         "performance":90.10933864528688
      },
      "hospital":"pjvq",
      "center":60.08944750425428,
      "strategy":{
         "service":{
            "task":89,
            "rule":"wdba",
            "memory":7,
            "office":{
               "heavy":35.326045016302174,
               "player":61,
               "stage": {}
            }
         },
         "street":"ulaz",
         "pull":{
            "machine":{
               "bank":"qqkv",
               "series":18.24566606650211
            },
            "capital":"gkkv",
            "stage":"soun",
            "service":{
               "government":"taxl",
               "food":"ibxe"
            },
            "card":73
         },
         "kilo":{
            "capital":"hcsd"
         }
      }
   }
}
trie.insert_from_json(json_obj_3)
search_key = "key43"
result = trie.search(search_key)
print(json.dumps(result, indent=4))
