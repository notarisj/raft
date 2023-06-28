import json

from src.kv_store.server.server_json import ServerJSON
from src.kv_store.server.raft_json import RaftJSON
from src.kv_store.trie_data_structure.data_tree import Trie
from src.logger import MyLogger

logger = MyLogger()


class RequestHandler:
    """
    Handles the execution of different types of requests on a data tree.

    Attributes:
        trie (Trie): The data tree used for storing key-value pairs.
    """

    def __init__(self):
        """
        Initializes an instance of RequestHandler.
        """
        self.trie = Trie()

    def execute(self, query: 'ServerJSON' | 'RaftJSON') -> str | None:
        """
        Executes the given query.

        Args:
            query (Query): The query object representing the request.

        Returns:
            str or None: The result of the executed query, or None if the query is invalid.
        """
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

    def _execute_put_request(self, query: str) -> str | None:
        """
        Executes a PUT request by inserting the data into the data tree.

        Args:
            query (str): The query payload.

        Returns:
            str or None: The result of the PUT request, or None if an error occurs.
        """
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

    def _execute_search_request(self, query: str) -> str | dict:
        """
        Executes a SEARCH request by searching for the given key in the data tree.

        Args:
            query (str): The query payload.

        Returns:
            str or dict: The result of the SEARCH request.
        """
        query = query.replace("\"", "")
        result = self.trie.search(query)

        if result is None:
            return "NOT FOUND"
        else:
            return result

    def _execute_delete_request(self, query: str) -> str:
        """
        Executes a DELETE request by deleting the given key from the data tree.

        Args:
            query (str): The query payload.

        Returns:
            str: The result of the DELETE request.
        """
        if self.trie.search(query) is not None:
            self.trie.delete(query)
            return "OK"
        else:
            return "NOT FOUND"
