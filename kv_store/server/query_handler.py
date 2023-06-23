import json

from kv_store.trie_data_structure.data_tree import Tree
from kv_store.server.message_handler import get_msg_command


class RequestHandler:
    def __init__(self):
        self.trie = Tree()

    @staticmethod
    def _parse_key_value(query) -> list[str]:
        return query.split(" ", 1)

    def execute(self, query) -> str:
        data = json.loads(query)
        query = data['command']
        query_parts = self._parse_key_value(query)

        command = query_parts[0]

        if command == "PUT":
            return self._execute_put_request(query_parts[1])
        elif command == "DELETE":
            return self._execute_delete_request(query_parts[1])
        elif command == "SEARCH":
            key_search = query_parts[1].replace("\"", "")
            return self._execute_search_request(key_search)
        else:
            print("Wrong query: " + query)
            print("Wrong type of query. Request must be: PUT, DELETE, SEARCH.")
            return "WRONG QUERY TYPE"

    def _execute_put_request(self, query) -> str:
        splitted_data = query.split(": ", 1)

        if self.trie.search(splitted_data[0]) is None:
            try:
                query = "{{{}}}".format(query)
                query = json.loads(query)
                self.trie.insert(query)
            except IndexError:
                self.trie.delete(splitted_data[0])
                print("Error while indexing data of \"" + query + "\". "
                      "Data don't have the right format.")
                print("Server will not index \"" + splitted_data[0] + "\".")
                return "ERROR"
            return "OK"
        else:
            return "Data \"" + query + "\" already exists."

    def _execute_search_request(self, query) -> str:
        query = query.replace("\"", "")
        result = self.trie.search(query)

        if result is None:
            return "NOT FOUND"
        else:
            return result

    def _execute_delete_request(self, query) -> str:
        if self.trie.search(query) is not None:
            self.trie.delete(query)
            return "OK"
        else:
            return "NOT FOUND"
