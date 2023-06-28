import json
import socket
import ssl
import random
import threading
from json import JSONDecodeError
from typing import List, Any

from src.configurations import IniConfig, JsonConfig
from src.kv_store.my_io.utils import receive_message, send_message, connect_to_server
from src.kv_store.server.message_helper import request_sender_type, get_key, check_id_exist
from src.kv_store.server.command_handler import search_top_lvl_key, search
from src.kv_store.server.query_handler import RequestHandler
from src.kv_store.server.raft_json import RaftJSON
from src.kv_store.server.server_json import ServerJSON
from src.logger import MyLogger
from src.raft_node.api_helper import api_post_request

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
        self.node_id = _id
        self.kv_server_host = servers.get_property(str(self.node_id))['host']
        self.kv_server_port = servers.get_property(str(self.node_id))['kv_port']
        self.kv_server_socket = None
        self.api_server_host = servers.get_property(str(self.node_id))['host']
        self.api_server_port = servers.get_property(str(self.node_id))['api_port']
        self.query_handler = RequestHandler()
        self.client_handlers = {}
        self.client_handlers_status = {}
        self.refresh_client_handlers()

    def start(self) -> None:
        """
        Start the KVServer.

        This method binds the server socket and listens for incoming connections.
        For each connection, a new thread is created to handle the every client.
        """
        self._server_socket_bind()
        if self.kv_server_socket is None:
            return

        while True:
            client_socket, client_address = self.kv_server_socket.accept()
            logger.info(f"New connection from: {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def refresh_client_handlers(self) -> None:
        """
        Refresh the client handlers.

        This method refreshes the client handlers by connecting to every server in the server list.
        """
        for _server_id, info in servers.config.items():
            server_id = int(_server_id)
            if int(server_id) != self.node_id:
                try:
                    self.client_handlers[server_id] = connect_to_server(info['host'], info['kv_port'],
                                                                        raft_config.get_property('SSL',
                                                                                                 'ssl_cert_file'))
                    self.client_handlers_status[server_id] = False \
                        if self.client_handlers[server_id] is None else True
                except ConnectionRefusedError:
                    logger.info(f"Connection refused by {server_id}")

    def refresh_client_handlers_if_needed(self) -> None:
        """
        Check if all servers are connected.

        This method checks if all servers are connected by checking the client handlers status.
        """
        for _server_id, info in servers.config.items():
            server_id = int(_server_id)
            if server_id != self.node_id and not self.client_handlers_status[server_id]:
                self.client_handlers[server_id] = connect_to_server(info['host'], info['kv_port'],
                                                                    raft_config.get_property('SSL', 'ssl_cert_file'))
                self.client_handlers_status[server_id] = False \
                    if self.client_handlers[server_id] is None else True

    def _server_socket_bind(self) -> None:
        """
        Bind the client socket.

        This method creates and binds the server socket to the specified host and port.
        It also sets up an SSL context and wraps the server socket with SSL.
        """
        try:
            self.kv_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.kv_server_socket.bind((self.kv_server_host, self.kv_server_port))

            # Create an SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=raft_config.get_property('SSL', 'ssl_cert_file'),
                                    keyfile=raft_config.get_property('SSL', 'ssl_key_file'))

            # Wrap the server socket with SSL
            self.kv_server_socket = context.wrap_socket(self.kv_server_socket, server_side=True)

            self.kv_server_socket.listen()
            logger.info("KV server started on {}:{}".format(self.kv_server_host, self.kv_server_port))
        except OSError as e:
            logger.info(f"KV socket binding error: {str(e)}")
            self._server_socket_close()

    def _server_socket_close(self) -> None:
        """
        Close the server socket.

        This method closes the server socket if it's open and logs any errors that occur.
        """
        if self.kv_server_socket:
            try:
                self.kv_server_socket.close()
                logger.info("KV server socket closed.")
            except OSError as e:
                logger.info(f"Error while closing KV socket: {str(e)}")
            self.kv_server_socket = None

    def handle_client(self, client_socket: Any) -> None:
        """
        Handle a client request.

        This method handles requests from a client. It receives a request
        from a client and determines its sender type. It then calls the
        appropriate handler based on the sender type. Have to note:
            - Every client has a different instance of this method.
            - Every request is a JSON string.

        Args:
            client_socket (socket): Client socket.
        """
        while True:
            request = receive_message(client_socket)
            logger.info(f"Received request: '{request}'")
            if request is None or request == "exit":
                break

            try:
                if request_sender_type(request, "CLIENT"):
                    self.client_request_handler(client_socket, request)
                elif request_sender_type(request, "RAFT"):
                    self.raft_request_handler(request)
                elif request_sender_type(request, "KV_SERVER"):
                    self.server_request_handler(client_socket, request)
                else:
                    self.wrong_sender_handler(client_socket, request)
            except JSONDecodeError:
                response = "Error while parsing request"
                send_message(response, client_socket)
                continue

        # Close the client socket
        client_socket.close()

    def client_request_handler(self, client_socket: Any, request: str) -> None:
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
            client_socket (socket): Client socket.
            request (str): Request received from the client.
        """
        shuffled_rep_ids = self.replication_ids()

        decoded_json = json.loads(request)
        server_instance = ServerJSON.from_json(decoded_json)
        command_type = server_instance.get_command_type()

        if command_type == 'PUT':
            self.refresh_client_handlers_if_needed()
            if search_top_lvl_key(current_server_id=self.node_id, server_list=servers.config,
                                  _request=request, query_handler=self.query_handler,
                                  client_handlers=self.client_handlers):
                # stage 1 --> DELETE FIRST
                try:
                    self.send_to_raft(["DELETE " + server_instance.get_command_value()], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    send_message(f"Failed to send request to Raft {e}", client_socket)
                    return

                # stage 2 --> PUT after deletion
                try:
                    self.send_to_raft([server_instance.commands], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    send_message(f"Failed to send request to Raft {e}", client_socket)
                    return

                response = "Top level key \"" + server_instance.get_command_key() + "\" already exists. " \
                                                                                    "Send deletion message and then " \
                                                                                    "insert."
                send_message(response, client_socket)
            else:
                # do not exist so PUT directly
                try:
                    self.send_to_raft([server_instance.commands], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    send_message(f"Failed to send request to Raft {e}", client_socket)
                    return
                response = "Send insertion message for command \"{}\"".format(json.loads(request)['commands'])
                send_message(response, client_socket)
        elif command_type == 'DELETE':
            self.refresh_client_handlers_if_needed()
            if search_top_lvl_key(current_server_id=self.node_id, server_list=servers.config,
                                  _request=request, query_handler=self.query_handler,
                                  client_handlers=self.client_handlers):
                # key exists so DELETE directly
                try:
                    self.send_to_raft(["DELETE " + server_instance.get_command_value()], shuffled_rep_ids)
                except Exception as e:
                    logger.error(f"Failed to send request to Raft: {e}")
                    send_message(f"Failed to send request to Raft {e}", client_socket)
                    return
                response = "Send deletion message for top level key \"{}\"".format(get_key(request))
                send_message(response, client_socket)
            else:
                pass
                # key does not exist so send error message
                # response = " Top level key \"{}\" not found to delete it".format(get_key(request))
                # send_message(response, client_socket)
        elif command_type == 'SEARCH':
            self.refresh_client_handlers_if_needed()
            response = search(current_server_id=self.node_id, server_list=servers.config, _request=server_instance,
                              query_handler=self.query_handler, client_handlers=self.client_handlers)
            send_message(response, client_socket)
        else:
            # not known command type
            response = "\"{}\" is invalid command from user".format(command_type)
            send_message(response, client_socket)

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

    def raft_request_handler(self, request: str) -> None:
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

        if not check_id_exist(request, self.node_id):
            logger.info("Node ID {} not found in request. Ignore it.".format(self.node_id))
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

    def server_request_handler(self, client_socket: Any, request: str) -> None:
        """
        Handle a request from another KVServer.

        This method handles a request from another KVServer by executing the
        appropriate action based on the command type. The only accepted command
        type from another KVServer is SEARCH. After searching trie, it sends the
        response back to the KVServer.

        Args:
            client_socket (socket): Client socket.
            request (str): Request received from the KVServer.
        """
        decoded_json = json.loads(request)
        server_instance = ServerJSON.from_json(decoded_json)
        command_type = server_instance.get_command_type()
        if command_type == 'SEARCH':
            answer = self.query_handler.execute(server_instance)
            send_message(answer, client_socket)
        else:
            # not known command type from KVServer
            response = "\"{}\" is invalid command from a KVServer".format(command_type)
            send_message(response, client_socket)

    @staticmethod
    def wrong_sender_handler(client_socket: Any, request: str) -> None:
        """
        Handle a request with an incorrect sender type.

        This method handles a request with an incorrect sender type by sending an error response.

        Args:
            client_socket (socket): Client socket.
            request (str): Request received from the client.
        """
        response = "\"{}\" is invalid request".format(request)
        send_message(response, client_socket)

    def replication_ids(self) -> List[int]:
        """
        Get a random list of replication IDs.

        This method returns a list of replication IDs with a length equal to the replication factor.

        Returns:
            list: A random list of replication IDs.
        """
        server_ids = [server_id for server_id in servers.config.keys() if server_id != self.node_id]
        return random.sample(server_ids, min(self.replication_factor, len(servers.config.keys())))
