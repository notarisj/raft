from src.kv_store.trie_data_structure.data_tree import Trie

# Create a new Trie instance
trie = Trie()

# Insert keys into the trie
trie.insert({"key1": {"power": {"office": {"center": 22.063470471034165, "stage": "oxws",
                                           "product": {"government": "stjw", "pull": 90.44574907688828,
                                                       "language": "qnaz", "computer": "xgzw", "office": 0},
                                           "bank": "hdcq"}}, "dog": "mxpm", "animal": "aqxg"}})

trie.insert({"key2": {"factor": 94.50748027574404}})

# trie.insert({"key20": {"dog": "svpy",
#                        "region": {"animal": "wzpe", "food": "sxmy", "statement": {"college": "kflu"}, "patient": 50,
#                                   "bank": "rhyt"}}})

trie.insert({"key22": {"city": "egbj", "place": "sadz"}})

# trie.insert({"key24": {"owner": {"pull": {"member": {"flight": 34, "charge": 50.06922595895755}, "food": "krlg"},
#                                  "height": 56.41566992913829}, "office": 100, "height": {"power": 6.922569754379659}}})

# trie.insert({"key43": {
#     "father": {"organization": "ilet", "charge": 46.577936022801005, "model": 89, "performance": 90.10933864528688},
#     "hospital": "pjvq", "center": 60.08944750425428, "strategy": {"service": {"task": 89, "rule": "wdba", "memory": 7,
#                                                                               "office": {"heavy": 35.326045016302174,
#                                                                                          "player": 61,
#                                                                                          "stage": "gkgv"}},
#                                                                   "street": "ulaz", "pull": {
#             "machine": {"bank": "qqkv", "series": 18.24566606650211}, "capital": "gkkv", "stage": "soun",
#             "service": {"government": "taxl", "food": "ibxe"}, "card": 73},
#                                                                   "kilo": {"capital": "hcsd", "father": "pzxq"}}}})

# Print the trie before deletion
print("Trie before deletion:")
print(trie.search(""))  # Search with an empty key to retrieve the entire trie
print()

# Delete key2 and its subtree
result = trie.delete("key22")
print("Deletion result:", result)
print()

# Print the trie after deletion
print("Trie after deletion:")
print(trie.search(""))  # Search with an empty key to retrieve the entire trie
