import json
import socket
import random

from src.kv_store.my_io.utils import send_message, receive_message
from src.kv_store.server.message_handler import get_msg_command_value, get_key, format_msg_for_search


def search_top_lvl_key(current_server_id, server_list, _request, query_handler) -> bool:
    key = get_key(_request)
    execute_command = "SEARCH {}".format(key)
    data = json.loads(_request)
    data['command'] = execute_command
    _request = json.dumps(data)
    response = query_handler.execute(_request)
    if response != "NOT FOUND" and response is not None:
        return True

    _request = format_msg_for_search(_request, "KV_SERVER")

    # Shuffle the server list to have a random order
    random.shuffle(server_list)

    for server in server_list:
        server_id = server[2]
        if server_id != current_server_id:
            ip = server[0]
            port = server[1]

            for i in range(3):

                client_socket = None
                response = None
                try:
                    # Create a socket and connect to the server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((ip, port))

                    # Send the request to the server
                    send_message(_request, client_socket)

                    # Receive and process the response
                    response = receive_message(client_socket)
                    if response:
                        print(f"Response from server with id: {server_id}")
                        print(response)

                except socket.error as e:
                    print(f"Error connecting to server with id: {server_id}")
                    print(str(e))
                finally:
                    if client_socket:
                        client_socket.close()
                        if response is not None and response != "NOT FOUND":
                            return True
                        break
    return False


def search(current_server_id, server_list, _request, query_handler) -> str:
    command_value = get_msg_command_value(_request)
    response = query_handler.execute(command_value)

    if response != "NOT FOUND" and response is not None:
        return response

    _request = format_msg_for_search(_request, "KV_SERVER")

    # Shuffle the server list to have a random order
    random.shuffle(server_list)

    for server in server_list:
        server_id = server[2]
        if server_id != current_server_id:
            ip = server[0]
            port = server[1]

            for i in range(3):

                client_socket = None
                response = None
                try:
                    # Create a socket and connect to the server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((ip, port))

                    # Send the request to the server
                    # TODO: format the msg correctly
                    send_message(_request, client_socket)

                    # Receive and process the response
                    response = receive_message(client_socket)
                    if response:
                        print(f"Response from server with id: {server_id}")
                        print(response)

                except socket.error as e:
                    print(f"Error connecting to server with id: {server_id}")
                    print(str(e))
                finally:
                    if client_socket:
                        client_socket.close()
                        if response is not None and response != "NOT FOUND":
                            return response
                        break
    return "NOT FOUND"