import json
from typing import Any

from src.kv_store.trie_data_structure.data_tree import Trie
from src.logger import MyLogger

logger = MyLogger()


class RequestHandler:
    def __init__(self):
        self.trie = Trie()

    def execute(self, query) -> str | None:
        # data = json.loads(query)
        # query = data['commands']
        # query_parts = self._parse_key_value(query)
        # command = query_parts[0]
        query_payload = query.get_command_value()
        command = query.get_command_type()

        if command == "PUT":
            return self._execute_put_request(query_payload)
        elif command == "DELETE":
            return self._execute_delete_request(query_payload)
        elif command == "SEARCH":
            key_search = query_payload.replace("\"", "")
            return self._execute_search_request(key_search)
        else:
            logger.info(f"Wrong query: {query}")
            logger.info("Wrong type of query. Request must be: PUT, DELETE, SEARCH.")
            return None

    # @staticmethod
    # def _parse_key_value(query) -> list[str]:
    #     return query.split(" ", 1)

    def _execute_put_request(self, query) -> str | None:
        splitted_data = query.split(": ", 1)

        if self.trie.search(splitted_data[0]) is None:
            try:
                query = "{{{}}}".format(query)
                query = json.loads(query)
                self.trie.insert(query)
            except IndexError:
                self.trie.delete(splitted_data[0])
                logger.info("Error while indexing data of \"" + query + "\". "
                                                                        "Data don't have the right format.")
                logger.info("Server will not index \"" + splitted_data[0] + "\".")
                return None
            return "OK"
        else:
            return "Data \"" + query + "\" already exists."

    def _execute_search_request(self, query) -> str | dict:
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
