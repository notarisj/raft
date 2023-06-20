import json
import socket
import re

from kv_store.my_io.utils import send_request_opened_connection


class ExternalClient:
    def __init__(self, _server_ip, _server_port):
        self.server_ip = _server_ip
        self.server_port = _server_port
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            print("Connected to {}:{}".format(self.server_ip, self.server_port))
        except ConnectionRefusedError:
            print("Failed to connect to {}:{}. Please ensure the server is running.".format(
                self.server_ip, self.server_port))

    def start_interaction(self):
        while True:
            message = input(self.terminal_input_msg())
            formatted_message = self.message_formatter(message)
            if message.lower() == 'exit':
                self.disconnect()
                break
            # response = send_request_opened_connection(formatted_message, self.client_socket)
            # print(response)
            print(formatted_message)

    def disconnect(self):
        try:
            self.client_socket.close()
            print("Disconnected from the server.")
        except AttributeError:
            print("No active connection to the server.")

    def message_formatter(self, message) -> str:
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

        message = self.escape_quotes(message)
        return self.get_basic_format(message)

    @staticmethod
    def put_format_checker(message) -> bool:
        value = message.split(": ", 1)[1]
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def search_format_checker(message) -> bool:
        pattern = r'[a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*'
        if re.match(pattern, message.split(" ", 1)[1]):
            return True
        else:
            return False

    @staticmethod
    def delete_format_checker(message) -> bool:
        pattern = r"^[a-zA-Z0-9]+$"
        if re.match(pattern, message.split(" ", 1)[1]):
            return True
        else:
            return False

    @staticmethod
    def escape_quotes(message) -> str:
        return message.replace("\"", "\\\"")

    @staticmethod
    def get_basic_format(message) -> str:
        msg = "{{ \"{}\": \"{}\"," \
              " \"{}\": \"{}\" }}".format("sender", "CLIENT", "command", message)
        return msg

    @staticmethod
    def terminal_input_msg() -> str:
        msg = "Enter a message to send to the server: \n"
        msg += "  1. 'PUT \"key\": \"valid_json\"' to add a new key-value pair\n"
        msg += "  2. 'SEARCH key.path1.field1' to search the data in dot '.' separated path\n"
        msg += "  3. 'DELETE key' to delete the top-level key (only)\n"
        msg += "  4. 'exit' to quit\n"
        return msg
