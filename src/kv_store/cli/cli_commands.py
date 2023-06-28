import argparse
import json
import re
import subprocess

from prompt_toolkit.completion import WordCompleter

from src.configurations import IniConfig
from src.kv_store.my_io import send_message, receive_message
from src.kv_store.server import ServerJSON, ServerJSONEncoder

basic_commands = WordCompleter(["PUT", "SEARCH", "DELETE", "clear", "connect", "exit", "help"])
raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')


def show_wellcome_screen():
    """
    Displays the welcome screen.
    """
    print("=================================================================")
    print("================= Key Value Store Client (v1.0) =================")
    print("=================================================================")


def send_command(command: str, client_socket, sync=False):
    """
    Sends the command to the server.

    Args:
        command (str): The command to send.
        client_socket (socket): The client socket.
        sync: If true it waits for the response

    Raises:
        ValueError: If the command is invalid.
    """
    print(f"Sending command: {message_formatter(command)}")
    send_message(message_formatter(command), client_socket)
    if sync:
        print(receive_message(client_socket))


def message_formatter(message: str) -> str:
    """
    Formats the user's input message to be sent to the server as a ServerJSON class.
    The input string is checked for the following commands:
        - PUT
        - SEARCH
        - DELETE
        - EXIT
    and their respective formats.

    Args:
        message (str): The user's input message.

    Returns:
        The formatted message as a string.

    Raises:
        ValueError: If the message format is invalid.
    """
    if message.lower() == 'exit':
        return message

    if message.lower().startswith('put'):
        if not put_format_checker(message):
            return_msg = "Invalid format. Please use the following format: PUT \"key\": \"valid_json\""
            return return_msg
    elif message.lower().startswith('search'):
        if not search_format_checker(message):
            return_msg = "Invalid format. Please use the following format: SEARCH \"key.path1.field1\""
            return return_msg
    elif message.lower().startswith('delete'):
        if not delete_format_checker(message):
            return_msg = "Invalid format. Please use the following format: DELETE \"key\""
            return return_msg

    # message = self.escape_quotes(message)
    server_obj = ServerJSON("CLIENT", message)
    server_json = json.dumps(server_obj, cls=ServerJSONEncoder)
    return server_json


def put_format_checker(message: str) -> bool:
    """
    Checks if the format of the 'put' message is valid.
    The value of the put key must be a valid JSON.

    Args:
        message (str): The 'put' message.

    Returns:
        True if the format is valid, False otherwise.
    """
    value = message.split(": ", 1)[1]
    try:
        json.loads(value)
        return True
    except json.JSONDecodeError:
        return False


def search_format_checker(message: str) -> bool:
    """
    Checks if the format of the 'search' message is valid. Search string must be of type:
    "key.path1.field1"

    Args:
        message (str): The 'search' message.

    Returns:
        True if the format is valid, False otherwise.
    """
    pattern = r'[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*'
    if re.match(pattern, message.split(" ", 1)[1]):
        return True
    else:
        return False


def delete_format_checker(message: str) -> bool:
    """
    Checks if the format of the 'delete' message is valid.

    Args:
        message (str): The 'delete' message.

    Returns:
        True if the format is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9]+$"
    if re.match(pattern, message.split(" ", 1)[1]):
        return True
    else:
        return False


def execute_system_command(command: str) -> str:
    """
    Executes a command in the shell and returns the output.

    Args:
        command (str): The command to execute.

    Returns:
        str: The output of the command.
    """
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    _output, _ = process.communicate()
    return _output.decode().strip()


def show_help() -> None:
    """
    Displays the help information for the client tool.
    """
    parser = argparse.ArgumentParser(description='Key Value Client Tool Help')

    # Define commands and their descriptions
    commands = {
        'PUT': 'Inserts a new key (usage: PUT "key": "valid_json")',
        'SEARCH': 'Searches for a key (usage: SEARCH key.path.to.field1)',
        'DELETE': 'Deletes a key (usage: DELETE key)',
        'exit': 'Quit the client'
    }

    # Add commands as subparsers
    subparsers = parser.add_subparsers(title='Commands')

    for command, description in commands.items():
        subparsers.add_parser(command, help=description)

    parser.print_help()
