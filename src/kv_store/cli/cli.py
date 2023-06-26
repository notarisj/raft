import sys

from prompt_toolkit import PromptSession
from src.kv_store.cli.cli_commands import *


def _exit():
    print("Exiting KVStore client. Bye!")
    sys.exit(0)


class ClientCli:

    def __init__(self):
        self.api_username = None
        self.api_password = None
        self.host = None
        self.port = None
        self.session = PromptSession(completer=basic_commands)
        self.basic_commands = None
        self.api_helper = None
        self.is_connected = False

    def process_user_input(self, user_input):
        # only allow login and exit commands if self.is_connected is False
        # allowed_commands = ["login", "exit", "clear", "help"]
        # if not self.is_connected:
        #     if user_input not in allowed_commands:
        #         print("You must first login to the cluster. Type 'login' to continue.")
        #         return
        switcher = {
            "PUT": lambda: execute_put('key1', 'value1'),
            "SEARCH": lambda: execute_search('key1'),
            "DELETE": lambda: execute_delete('key1'),
            "clear": lambda: print(execute_command(user_input)),
            "exit": lambda: _exit(),
            "help": lambda: show_help(),
            "": lambda: None
        }

        func = switcher.get(user_input, lambda: print("Unknown command:", user_input))
        func()

    def run(self):
        while True:
            try:
                if not self.is_connected:
                    user_input = self.session.prompt("\n> ", is_password=False)
                else:
                    user_input = self.session.prompt(f"\n{self.api_username}@{self.host}> ", is_password=False)
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
