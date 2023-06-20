from kv_store.server.query_handler import RequestHandler


class TrieTester:

    def __init__(self, _data_path):
        self.data_path = _data_path
        self.request_handler = RequestHandler()

    def insert_data(self):
        with open(self.data_path, "r") as file:
            for line in file:
                escaped_line = line.replace("\"", "\\\"")
                command = "PUT {}".format(escaped_line).replace("\n", "")
                line = "{ \"command\" : \"" + command + "\" }"
                self.request_handler.execute(line)
        return None

    def delete_data(self, query):
        command = "DELETE {}".format(query).replace("\n", "")
        line = "{ \"command\" : \"" + command + "\" }"
        self.request_handler.execute(line)
        return None

    def search_data(self, query):
        command = "SEARCH {}".format(query).replace("\n", "")
        line = "{ \"command\" : \"" + command + "\" }"
        return self.request_handler.execute(line)


if __name__ == "__main__":
    trie_tester = TrieTester("/home/giannis/Desktop/raft/kv_store/resources/dataToIndex.txt")
    trie_tester.insert_data()
    result = trie_tester.search_data("key5")
    print(result)
    trie_tester.delete_data("key5")
    result = trie_tester.search_data("key5")
    print(result)
    result = trie_tester.search_data("key1")
    print(result)
    result = trie_tester.search_data("key1.power.office")
    print(result)
    result = trie_tester.search_data("key1.office")
    print(result)
