import json
import socket
import re
import ssl

from src.configurations import IniConfig
from src.logger import MyLogger
# from src.kv_store.my_io.utils import send_request_opened_connection
from src.kv_store.server.server_json import ServerJSON, ServerJSONEncoder

logger = MyLogger()
raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')


class ExternalClient:
    """
    Represents an external client that connects to a server using a TCP socket and SSL.
    The client can interact with the server by sending messages and receiving responses.
    """

    def __init__(self, _server_ip: str, _server_port: int) -> None:
        """
        Initializes an instance of ExternalClient.

        Args:
            _server_ip (str): The IP address of the server to connect.
            _server_port (int): The port number of the server to connect.
        """
        self.server_ip = _server_ip
        self.server_port = _server_port
        self.client_socket = None

    def connect(self) -> None:
        """
        Connects to the server using a TCP socket and SSL.

        Raises:
            ConnectionRefusedError: If the connection to the server is refused.
            socket.timeout: If the connection times out.
            ssl.SSLError: If an SSL error occurs while connecting.
            socket.error: If a socket error occurs while connecting.
            Exception: If any other error occurs while connecting.
        """
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Create an SSL context
            context = ssl.create_default_context(cafile=raft_config.get_property('SSL', 'ssl_cert_file'))
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            # Wrap the client socket with SSL
            self.client_socket = context.wrap_socket(self.client_socket, server_hostname=self.server_ip)

            self.client_socket.connect((self.server_ip, self.server_port))
            logger.info("Connected to {}:{}".format(self.server_ip, self.server_port))
        except ConnectionRefusedError:
            logger.info("Failed to connect to {}:{}. Please ensure the server is running.".format(
                self.server_ip, self.server_port))
        except socket.timeout:
            logger.info("Connection to {}:{} timed out. Please check your network connection.".format(
                self.server_ip, self.server_port))
        except ssl.SSLError as e:
            logger.error("SSL error occurred while connecting to {}:{}: {}".format(
                self.server_ip, self.server_port, str(e)))
        except socket.error as e:
            logger.error("Socket error occurred while connecting to {}:{}: {}".format(
                self.server_ip, self.server_port, str(e)))
        except Exception as e:
            logger.error("An error occurred while connecting to {}:{}: {}".format(
                self.server_ip, self.server_port, str(e)))

    def start_interaction(self) -> None:
        """
        Starts the interaction loop with the server.
        The user can input messages to send to the server until they enter 'exit'.
        """
        while True:
            message = input(self.terminal_input_msg())
            formatted_message = self.message_formatter(message)
            if message.lower() == 'exit':
                self.disconnect()
                break
            logger.info(f"Send to KV_Server: '{formatted_message}'")
            # response = send_request_opened_connection(formatted_message, self.client_socket)
            # logger.info(response)

    def disconnect(self) -> None:
        """
        Disconnects from the server. Close the socket to the server.
        """
        try:
            self.client_socket.close()
            logger.info("Disconnected from the server.")
        except AttributeError:
            logger.info("No active connection to the server.")

    def message_formatter(self, message: str) -> str:
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
        server_obj = ServerJSON("CLIENT", message)
        server_json = json.dumps(server_obj, cls=ServerJSONEncoder)
        return server_json

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def terminal_input_msg() -> str:
        """
        Returns the input message prompt for the user.

        Returns:
            The input message prompt as a string.
        """
        msg = "Enter a message to send to the server: \n"
        msg += "  1. 'PUT \"key\": \"valid_json\"' to add a new key-value pair\n"
        msg += "  2. 'SEARCH key.path1.field1' to search the data in dot '.' separated path\n"
        msg += "  3. 'DELETE key' to delete the top-level key (only)\n"
        msg += "  4. 'exit' to quit\n"
        return msg
