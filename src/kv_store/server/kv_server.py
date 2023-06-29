import json
import random
import threading
from typing import List

from src.configurations import IniConfig, JsonConfig
from src.kv_store.server.message_helper import get_key, check_id_exist
from src.kv_store.server.command_handler import search_top_lvl_key, search
from src.kv_store.server.query_handler import RequestHandler
from src.kv_store.server.raft_json import RaftJSON
from src.kv_store.server.server_json import ServerJSON
from src.logger import MyLogger
from src.raft_node.api_helper import api_post_request
from src.rpc import RPCServer, RPCClient

logger = MyLogger()
raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')
servers = JsonConfig('/Users/notaris/git/raft/src/raft_node/deploy/servers.json')


class KVServer:
    def __init__(self, _replication_factor: int, _id: int) -> None:
        """
        Initialize a KVServer instance.

        Args:
            _replication_factor (int): Replication factor.
            _id (str): Server ID.
        """
        self.replication_factor = _replication_factor
        self.server_id = _id
        self.kv_server_host = servers.get_property(str(self.server_id))['host']
        self.kv_server_port = servers.get_property(str(self.server_id))['kv_port']
        self.kv_server_socket = None
        self.api_server_host = servers.get_property(str(self.server_id))['host']
        self.api_server_port = servers.get_property(str(self.server_id))['api_port']
        self.query_handler = RequestHandler()

        self.rpc_server = RPCServer(host=self.kv_server_host, port=self.kv_server_port)
        self.rpc_server.register_function(self.client_request_rpc, 'client_request')
        self.rpc_server.register_function(self.kv_request_rpc, 'kv_request')
        self.rpc_server.register_function(self.raft_request_rpc, 'raft_request')

        # Create RPC clients for all other servers

        self.client_handlers = {}
        # self.client_handlers_status = {}
        # self.refresh_client_handlers()
        self.create_client_handlers()

    def run(self) -> None:
        """
        Start the KVServer.

        This method binds the server socket and listens for incoming connections.
        For each connection, a new thread is created to handle the every client.
        """
        threading.Thread(target=self.rpc_server.run).start()

    def create_client_handlers(self) -> None:
        """
        Refresh the client handlers.

        This method refreshes the client handlers by connecting to every server in the server list.
        """
        for server_id, server in servers.config.items():
            if int(server_id) != self.server_id:
                self.client_handlers[server_id] = RPCClient(host=server['host'], port=server['kv_port'])

    # def refresh_client_handlers(self) -> None:
    #     """
    #     Refresh the client handlers.
    #
    #     This method refreshes the client handlers by connecting to every server in the server list.
    #     """
    #     for server_id, server in servers.config.items():
    #         if int(server_id) != self.server_id:
    #             try:
    #                 self.client_handlers[server_id] = RPCClient(host=server['host'], port=server['kv_port'])
    #                 self.client_handlers_status[server_id] = False \
    #                     if self.client_handlers[server_id] is None else True
    #             except ConnectionRefusedError:
    #                 logger.info(f"Connection refused by {server_id}")

    # def refresh_client_handlers_if_needed(self) -> None:
    #     """
    #     Check if all servers are connected.
    #
    #     This method checks if all servers are connected by checking the client handlers status.
    #     """
    #     for server_id, server in servers.config.items():
    #         if int(server_id) != self.server_id and not self.client_handlers_status[server_id]:
    #             self.client_handlers[server_id] = RPCClient(host=server['host'], port=server['kv_port'])
    #             self.client_handlers_status[server_id] = False \
    #                 if self.client_handlers[server_id] is None else True

    def client_request_rpc(self, request: str) -> str:
        """
        Handle a request from a client.

        This method handles a request from a client by executing the appropriate
        action based on the command type. The appropriate commands are:
            - PUT: Send SEARCH request to KV-servers for the top-level key to check
                   if it already exists. If it exists send DELETE message over the Raft,
                   and then send PUT message over the Raft. If not exists, just send PUT
                   message over Raft.
            - DELETE: Send SEARCH request to KV-servers for the top-level key to check
                   if it already exists. If exists, send DELETE message over the Raft.
                   Firstly send SEARCH to KV-servers to avoid sending messages over Raft
                   for better performance and network usage.
            - SEARCH: Send SEARCH request to KV-servers without passing the message over Raft


        Args:
            request (str): Request received from the client.
        """
        shuffled_rep_ids = self.replication_ids()

        decoded_json = json.loads(request)
        server_instance = ServerJSON.from_json(decoded_json)
        command_type = server_instance.get_command_type()

        if command_type == 'PUT':
            # self.refresh_client_handlers_if_needed()
            if search_top_lvl_key(current_server_id=self.server_id, server_list=servers.config,
                                  _request=request, query_handler=self.query_handler,
                                  client_handlers=self.client_handlers):
                # stage 1 --> DELETE FIRST
                try:
                    self.send_to_raft(["DELETE " + server_instance.get_command_value()], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    return f"Failed to send request to Raft: {e}"

                # stage 2 --> PUT after deletion
                try:
                    self.send_to_raft([server_instance.commands], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    return f"Failed to send request to Raft: {e}"

                response = "Top level key \"" + server_instance.get_command_key() + "\" already exists. " \
                                                                                    "Send deletion message and then " \
                                                                                    "insert."
                return response
            else:
                # do not exist so PUT directly
                try:
                    self.send_to_raft([server_instance.commands], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    return f"Failed to send request to Raft: {e}"
                response = f"server id {self.server_id}: Send insertion message for " \
                           f"command {json.loads(request)['commands']}"
                return response
        elif command_type == 'DELETE':
            # self.refresh_client_handlers_if_needed()
            if search_top_lvl_key(current_server_id=self.server_id, server_list=servers.config,
                                  _request=request, query_handler=self.query_handler,
                                  client_handlers=self.client_handlers):
                # key exists so DELETE directly
                try:
                    self.send_to_raft(["DELETE " + server_instance.get_command_value()], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    return f"Failed to send request to Raft: {e}"
                response = "Send deletion message for top level key \"{}\"".format(get_key(request))
                return response
            else:
                # key does not exist so send error message
                response = f"Top level key {get_key(request)} not found to delete it"
                return response
        elif command_type == 'SEARCH':
            # self.refresh_client_handlers_if_needed()
            response = search(current_server_id=self.server_id, server_list=servers.config, _request=server_instance,
                              query_handler=self.query_handler, client_handlers=self.client_handlers)
            return response
        else:
            # not known command type
            response = f"{command_type} is invalid command from user"
            return response

    def send_to_raft(self, commands: List[str], shuffled_rep_ids: List[int]) -> None:
        """
        Sends a payload to the Raft server for processing.

        Args:
           commands (List[str]): The commands to send, represented as a list of strings.
           shuffled_rep_ids (List[int]): The shuffled list of replica IDs to determine the order of processing.
        """
        # TODO: catch the exception and send back to client.
        raft_obj = RaftJSON("RAFT", commands, shuffled_rep_ids)
        api_post_request(f"https://{self.api_server_host}:{self.api_server_port}/append_entries", raft_obj.to_json())

    def raft_request_rpc(self, request: str) -> None:
        """
        Handle a request from the Raft server.

        This method handles a request from the Raft server. For every command in the
        commands list it creates a ServerJSON obj and handles-executes the command.

        Args:
            request (str): Request received from the Raft server.
        """
        decoded_raft = json.loads(request)
        raft_request_instance = RaftJSON.from_json(decoded_raft)
        requests_list = raft_request_instance.commands

        if not check_id_exist(request, self.server_id):
            logger.info("Node ID {} not found in request. Ignore it.".format(self.server_id))
        else:
            for request in requests_list:
                temp_request = ServerJSON("RAFT", request)
                command_type = temp_request.get_command_type()
                if command_type == 'PUT':
                    self.query_handler.execute(temp_request)
                elif command_type == 'DELETE':
                    self.query_handler.execute(temp_request)
                elif command_type == 'UPDATE':
                    # TODO: implement update of servers
                    # a new node is added in the raft, the servers.json file is updated
                    pass
                else:
                    response = "\"{}\" is invalid command from a RaftServer".format(command_type)
                    logger.error(response)

    def kv_request_rpc(self, request: str) -> str:
        """
        Handle a request from another KVServer.

        This method handles a request from another KVServer by executing the
        appropriate action based on the command type. The only accepted command
        type from another KVServer is SEARCH. After searching trie, it sends the
        response back to the KVServer.

        Args:
            request (str): Request received from the KVServer.
        """
        decoded_json = json.loads(request)
        server_instance = ServerJSON.from_json(decoded_json)
        command_type = server_instance.get_command_type()
        if command_type == 'SEARCH':
            answer = self.query_handler.execute(server_instance)
            return answer
        else:
            # not known command type from KVServer
            response = f"{command_type} is invalid command from a KVServer"
            return response

    def replication_ids(self) -> List[int]:
        """
        Get a random list of replication IDs.

        This method returns a list of replication IDs with a length equal to the replication factor.

        Returns:
            list: A random list of replication IDs.
        """
        server_ids = [server_id for server_id in servers.config.keys() if server_id != self.server_id]
        return random.sample(server_ids, min(self.replication_factor, len(servers.config.keys())))
