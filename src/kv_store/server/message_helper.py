import json


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
