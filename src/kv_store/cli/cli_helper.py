import json
import re

from src.kv_store.server import ServerJSON, ServerJSONEncoder


def message_formatter(self, message) -> str:
    """
    Formats the message to be sent to the server.

    Args:
        message (str): The message to format.

    Returns:
        The formatted message.
    """
    if message.lower() == 'exit':
        return message

    if message.lower().startswith('put'):
        if not self.put_format_checker(message):
            return_msg = "Invalid format. Please use the following format: PUT \"key\": \"valid_json\""
            return return_msg
    elif message.lower().startswith('search'):
        if not self.search_format_checker(message):
            return_msg = "Invalid format. Please use the following format: SEARCH \"key.path1.field1\""
            return return_msg
    elif message.lower().startswith('delete'):
        if not self.delete_format_checker(message):
            return_msg = "Invalid format. Please use the following format: DELETE \"key\""
            return return_msg

    # message = self.escape_quotes(message)
    server_obj = ServerJSON(message)
    server_json = json.dumps(server_obj, cls=ServerJSONEncoder)
    return server_json


def put_format_checker(message) -> bool:
    """
    Checks if the PUT command is in the correct format.
    The value of the put key must be a valid JSON.

    Args:
        message (str): The PUT command.

    Returns:
        True if the format is correct, False otherwise.
    """
    value = message.split(": ", 1)[1]
    try:
        json.loads(value)
        return True
    except json.JSONDecodeError:
        return False


def search_format_checker(message) -> bool:
    """
    Checks if the SEARCH command is in the correct format.

    Args:
        message (str): The SEARCH command.

    Returns:
        True if the format is correct, False otherwise.
    """
    pattern = r'[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*'
    if re.match(pattern, message.split(" ", 1)[1]):
        return True
    else:
        return False


def delete_format_checker(message) -> bool:
    """
    Checks if the DELETE command is in the correct format.

    Args:
        message (str): The DELETE command.

    Returns:
        True if the format is correct, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9]+$"
    if re.match(pattern, message.split(" ", 1)[1]):
        return True
    else:
        return False
