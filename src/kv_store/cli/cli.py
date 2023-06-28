import socket
import ssl
import sys

from prompt_toolkit import PromptSession

from src.kv_store.cli.cli_commands import *
from src.kv_store.my_io import connect_to_server

raft_config = IniConfig('/Users/notaris/git/raft/src/raft_node/deploy/config.ini')


def _exit():
    """
    Exits the KVStore client.
    """
    print("Exiting KVStore client. Bye!")
    sys.exit(0)


class ClientCli:

    def __init__(self):
        self.host = None
        self.port = None
        self.session = PromptSession(completer=basic_commands)
        self.basic_commands = None
        self.api_helper = None
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Create an SSL context
            print(raft_config.get_property('SSL', 'ssl_cert_file'))
            context = ssl.create_default_context(cafile=raft_config.get_property('SSL', 'ssl_cert_file'))
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            self.host = self.session.prompt("Hostname [127.0.0.1]: ", is_password=False)
            if not self.host:
                self.host = '127.0.0.1'
            self.port = self.session.prompt("Port [9001]: ", is_password=False)
            if not self.port:
                self.port = 9001

            # Wrap the client socket with SSL
            self.client_socket = context.wrap_socket(self.client_socket, server_hostname=self.host)

            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
        except ConnectionRefusedError:
            print(f"Failed to connect to {self.host}:{self.port}. Please ensure the server is running.")

    def _connect_to_server(self):
        self.host = self.session.prompt("Hostname [127.0.0.1]: ", is_password=False)
        if not self.host:
            self.host = '127.0.0.1'
        self.port = self.session.prompt("Port [9001]: ", is_password=False)
        if not self.port:
            self.port = 9001
        self.client_socket = connect_to_server(self.host, self.port,
                                               raft_config.get_property('SSL', 'ssl_cert_file'))

    def process_user_input(self, user_input):
        """
        Processes the user input and executes the corresponding command.

        Args:
            user_input (str): The user input to process.
        """
        # only allow to connect and exit commands if self.is_connected is False
        allowed_commands = ["connect", "exit", "clear", "help"]
        if self.client_socket is None:
            if user_input not in allowed_commands:
                print("You must first connect to the cluster. Type 'connect' to continue.")
                return
        switcher = {
            "PUT": lambda: send_command(user_input, self.client_socket),
            "SEARCH": lambda: send_command(user_input, self.client_socket, sync=True),
            "DELETE": lambda: send_command(user_input, self.client_socket),
            "clear": lambda: print(execute_system_command(user_input)),
            "connect": lambda: self._connect_to_server(),
            "exit": lambda: _exit(),
            "help": lambda: show_help(),
            "": lambda: None
        }

        func = switcher.get(user_input.split()[0], lambda: print("Unknown command:", user_input))
        func()

    def run(self) -> None:
        """
        Runs the KVStore client.
        """
        while True:
            try:
                if self.client_socket is None:
                    user_input = self.session.prompt("\n> ", is_password=False)
                else:
                    user_input = self.session.prompt(f"\n{self.host}:{self.port}> ", is_password=False)
                self.process_user_input(user_input)
            except KeyboardInterrupt:
                # Handle Ctrl+C
                break
            except EOFError:
                # Handle Ctrl+D
                break


if __name__ == "__main__":
    raft_cli = ClientCli()
    show_wellcome_screen()
    raft_cli.run()
