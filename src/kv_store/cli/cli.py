import sys

from prompt_toolkit import PromptSession

from src.kv_store.cli.cli_commands import *
from src.rpc import RPCClient

raft_config = IniConfig('src/configurations/config.ini')


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
        self.kv_store_rpc_client = None

    def connect(self):
        """
        Connects to the KVStore server.

        Returns:
            None

        Raises:
            ConnectionRefusedError: If the connection is refused.
        """
        try:

            self.host = self.session.prompt("Hostname [127.0.0.1]: ", is_password=False)
            if not self.host:
                self.host = '127.0.0.1'
            self.port = self.session.prompt("Port [9001]: ", is_password=False)
            if not self.port:
                self.port = 9001
            self.kv_store_rpc_client = RPCClient(host=self.host, port=self.port)
            print(f"Connected to {self.host}:{self.port}")
        except ConnectionRefusedError:
            print(f"Failed to connect to {self.host}:{self.port}. Please ensure the server is running.")

    def _connect_to_server(self):
        """
        Connects to the KVStore server.

        Returns:
            None
        """
        self.host = self.session.prompt("Hostname [127.0.0.1]: ", is_password=False)
        if not self.host:
            self.host = '127.0.0.1'
        self.port = self.session.prompt("Port [9001]: ", is_password=False)
        if not self.port:
            self.port = 9001
        self.kv_store_rpc_client = RPCClient(host=self.host, port=self.port)

    def process_user_input(self, user_input):
        """
        Processes the user input and executes the corresponding command.

        Args:
            user_input (str): The user input to process.
        """
        if not user_input:
            return
        # only allow to connect and exit commands if self.is_connected is False
        allowed_commands = ["login", "exit", "clear", "help"]
        if self.kv_store_rpc_client is None:
            if user_input not in allowed_commands:
                print("You must first login to the cluster. Type 'login' to continue.")
                return
        switcher = {
            "PUT": lambda: send_command(user_input, self.kv_store_rpc_client),
            "SEARCH": lambda: send_command(user_input, self.kv_store_rpc_client),
            "DELETE": lambda: send_command(user_input, self.kv_store_rpc_client),
            "clear": lambda: print(execute_system_command(user_input)),
            "login": lambda: self._connect_to_server(),
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
                if self.kv_store_rpc_client is None:
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
