import json


def request_sender_type(request: str, _sender: str) -> bool:
    """
    Checks if the sender of a request matches the specified sender.

    Args:
        request (str): The request to check.
        _sender (str): The expected sender value.

    Returns:
        bool: True if the sender matches the expected sender, False otherwise.

    Raises:
        json.JSONDecodeError: If the request is not a valid JSON.
    """
    try:
        msg = json.loads(request)
        return msg['sender'] == _sender
    except json.JSONDecodeError as e:
        raise e


def is_client_request(request: str) -> bool:
    """
    Checks if a request is from the client.

    Args:
        request (str): The request to check.

    Returns:
        bool: True if the request is from the client, False otherwise.

    Raises:
        json.JSONDecodeError: If the request is not a valid JSON.
    """
    try:
        msg = json.loads(request)
        return msg['sender'] == 'CLIENT'
    except json.JSONDecodeError as e:
        raise e


def is_raft_request(request: str) -> bool:
    """
    Checks if a request is from the Raft consensus algorithm.

    Args:
        request (str): The request to check.

    Returns:
        bool: True if the request is from Raft, False otherwise.

    Raises:
        json.JSONDecodeError: If the request is not a valid JSON.
    """
    try:
        msg = json.loads(request)
        return msg['sender'] == 'RAFT'
    except json.JSONDecodeError as e:
        raise e


def is_kv_server_request(request: str) -> bool:
    """
    Checks if a request is from the KV server.

    Args:
        request (str): The request to check.

    Returns:
        bool: True if the request is from the KV server, False otherwise.

    Raises:
        json.JSONDecodeError: If the request is not a valid JSON.
    """
    try:
        msg = json.loads(request)
        return msg['sender'] == 'KV_SERVER'
    except json.JSONDecodeError as e:
        raise e


def get_key(_request: str) -> str:
    """
    Retrieves the key of the command from a request.

    Args:
        _request (str): The request containing the key.

    Returns:
        str: The extracted key.
    """
    msg = json.loads(_request)['commands']
    results = msg.split(" ", 3)
    key = results[1].replace(":", "").replace("\"", "")
    return key


def check_id_exist(request: str, _id: int) -> bool:
    """
    Checks if an ID exists in the replication nodes list of a request.

    Args:
        request (str): The request to check.
        _id (int): The ID to check.

    Returns:
        bool: True if the ID exists in the replication nodes, False otherwise.

    Raises:
        json.JSONDecodeError: If the request is not a valid JSON.
    """
    try:
        msg = json.loads(request)
        replication_nodes = msg.get("rep_ids", [])
        return str(_id) in replication_nodes
    except json.JSONDecodeError as e:
        raise e
