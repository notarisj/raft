import threading
from json import JSONDecodeError

from kv_store.server.message_handler import *
from kv_store.server.command_handler import *
from kv_store.server.api_requester import APIRequester
from kv_store.server.message_handler import get_key
from kv_store.server.query_handler import RequestHandler
from kv_store.my_io.read_file import get_servers_from_file


class KVServer:
    def __init__(self, _kv_server_host, _kv_server_port, _raft_server_host, _raft_server_port, _id, _server_list_file):
        self.node_id = _id
        self.kv_server_host = _kv_server_host
        self.kv_server_port = _kv_server_port
        self.kv_server_socket = None
        self.api_requester = APIRequester(_raft_server_host, _raft_server_port)
        self.server_list = get_servers_from_file(_server_list_file)
        self.query_handler = RequestHandler()

    def start(self):
        self._client_socket_bind()
        if self.kv_server_socket is None:
            return

        while True:
            client_socket, client_address = self.kv_server_socket.accept()
            print("New connection from:", client_address)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def _client_socket_bind(self):
        try:
            self.kv_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.kv_server_socket.bind((self.kv_server_host, self.kv_server_port))
            self.kv_server_socket.listen()
            print("KV server started on {}:{}".format(self.kv_server_host, self.kv_server_port))
        except OSError as e:
            print("KV socket binding error:", str(e))
            self._client_close_socket()

    def _client_close_socket(self):
        if self.kv_server_socket:
            try:
                self.kv_server_socket.close()
                print("KV server socket closed.")
            except OSError as e:
                print("Error while closing KV socket:", str(e))
            self.kv_server_socket = None

    def handle_client(self, client_socket):
        while True:
            request = receive_message(client_socket)
            print("Received request:", request)
            if request is None or request == "exit":
                break

            try:
                command_type = get_msg_command_type(request)

                if is_client_request(request):
                    if command_type == 'PUT':
                        if search_top_lvl_key(current_server_id=self.node_id, server_list=self.server_list,
                                              _request=request, query_handler=self.query_handler):
                            # stage 1 --> DELETE FIRST
                            request = format_to_send_over_raft(request, _sender="RAFT", _command_type="DELETE")
                            self.api_requester.post_append_entry(request)
                            response = "Top level key \"{}\" already exists. Send deletion message" \
                                .format(get_key(request))
                            send_message(response, client_socket)
                            # stage 2 --> PUT after deletion
                            request = format_to_send_over_raft(request, _sender="RAFT", _command_type="PUT")
                            self.api_requester.post_append_entry(request)
                            response = "Send insertion message for command \"{}\"".format(get_msg_command(request))
                            send_message(response, client_socket)
                        else:
                            # do not exist so PUT directly
                            # request = format_to_send_over_raft(request, _sender="RAFT", _command_type="PUT")
                            data = json.loads(request)
                            data['sender'] = "RAFT"
                            request = json.dumps(data)
                            self.api_requester.post_append_entry(request)
                            response = "Send insertion message for command \"{}\"".format(get_msg_command(request))
                            send_message(response, client_socket)
                    elif command_type == 'DELETE':
                        if search_top_lvl_key(current_server_id=self.node_id, server_list=self.server_list,
                                              _request=request, query_handler=self.query_handler):
                            # key exists so DELETE directly
                            request = format_to_send_over_raft(request, _sender="RAFT", _command_type="DELETE")
                            self.api_requester.post_append_entry(request)
                            response = "Send deletion message for top level key \"{}\"".format(get_key(request))
                            send_message(response, client_socket)
                        else:
                            # key does not exist so send error message
                            response = " Top level key \"{}\" not found to delete it".format(get_key(request))
                            send_message(response, client_socket)
                    elif command_type == 'SEARCH':
                        search(current_server_id=self.node_id, server_list=self.server_list, _request=request,
                               query_handler=self.query_handler)
                    else:
                        # not known command type
                        response = "\"{}\" is invalid command from user".format(command_type)
                        send_message(response, client_socket)
                elif is_raft_request(request):
                    if command_type == 'PUT':
                        self.query_handler.execute(request)
                    elif command_type == 'DELETE':
                        self.query_handler.execute(request)
                    else:
                        # not known command type
                        response = "\"{}\" is invalid command from a RaftServer".format(command_type)
                        send_message(response, client_socket)
                elif is_kv_server_request(request):
                    if command_type == 'SEARCH':
                        answer = self.query_handler.execute(request)
                        send_message(answer, client_socket)
                    else:
                        # not known command type from KVServer
                        response = "\"{}\" is invalid command from a KVServer".format(command_type)
                        send_message(response, client_socket)
                else:
                    response = "\"{}\" is invalid request".format(request)
                    send_message(response, client_socket)
            except JSONDecodeError:
                response = "Error while parsing request"
                send_message(response, client_socket)
                continue

        # Close the client socket
        client_socket.close()
