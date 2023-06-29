import json

from src.configurations import IniConfig
from src.kv_store.server.query_handler import RequestHandler
from src.kv_store.server.message_helper import get_key
from src.kv_store.server.server_json import ServerJSON, ServerJSONEncoder

raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')


def search_top_lvl_key(current_server_id: int, server_list: dict, _request: str,
                       query_handler: 'RequestHandler', client_handlers: dict) -> bool:
    """
    Search for a top-level key in the server list.

    This method searches for a top-level key in the server list by sending requests to other servers in the list.
    It checks if the key exists in any of the servers. If it finds it at a server, it returns True.

    Args:
        current_server_id (int): The ID of the current server.
        server_list (list): The list of servers to search.
        _request (str): The request containing the key to search.
        query_handler: The query handler object.
        client_handlers (dict): The dictionary containing the client sockets for each server.

    Returns:
        bool: True if the key exists in any of the servers, False otherwise.
    """
    key = get_key(_request)
    server_obj = ServerJSON("KV_SERVER", "SEARCH {}".format(key))
    _request = json.dumps(server_obj, cls=ServerJSONEncoder)
    response = query_handler.execute(server_obj)
    if response != "NOT FOUND" and response is not None:
        return True

    # Shuffle the server list to have a random order
    # random.shuffle(server_list)

    for server_id in server_list.keys():
        if int(server_id) != current_server_id:
            response = client_handlers[server_id].call('kv_request', _request)
            if response:
                print(f"Response from server with id: {server_id}")
                print(response)
            if response is not None and response != "NOT FOUND":
                return True
    return False


def search(current_server_id: int, server_list: dict, _request: 'ServerJSON', query_handler: 'RequestHandler',
           client_handlers: dict) -> str:
    """
    Search for a key in the server list.

    This method searches for a value in the server list by sending requests to other servers in the list.
    It checks if the value exists in any of the servers and returns the corresponding value. It uses SSL
    to communicate with the servers.

    Args:
        current_server_id (int): The ID of the current server.
        server_list (list): The list of servers to search.
        _request (str): The request containing the key to search.
        query_handler: The query handler object.
        client_handlers (dict): The dictionary containing the client sockets for each server.

    Returns:
        str: The value corresponding to the key if it exists in any of the servers, "NOT FOUND" otherwise.
    """
    _request.sender = "KV_SERVER"
    print(_request.to_json())
    # check if the key is in the current server
    response = query_handler.execute(_request)
    if response != "NOT FOUND" and response is not None:
        return response

    dump_request = json.dumps(_request, cls=ServerJSONEncoder)

    # Shuffle the server list to have a random order
    # random.shuffle(server_list)

    for server_id in server_list.keys():
        if int(server_id) != current_server_id:
            response = client_handlers[server_id].call('kv_request', dump_request)
            if response:
                print(f"Response from server with id: {server_id}")
                print(response)
            if response is not None and response != "NOT FOUND":
                return response
    return "NOT FOUND"



